#!/usr/bin/env bash
# check-skill-size.sh — keep every SKILL.md inside the budget that survives a /compact.
#
# Why: when a session compacts, the harness re-injects each loaded skill's body and clips it
# at ~20 000 characters, silently, mid-sentence — and the tail is where the checklist and the
# rules live. Measured in the field: three skills came back as 19 997 / 19 992 / 20 000 chars
# with "[... skill content truncated for compaction]" where their `## Rules` used to be.
#
# So: body <= 15 000 characters, with headroom. Long catalogues, templates and rubrics belong
# in references/*.md, which load on demand and are never clipped.
#
# The `description` has a second, independent budget: it sits in context for EVERY session,
# whether or not the skill is ever used, so it pays rent on every single turn.
#
# Usage: scripts/check-skill-size.sh [--max-body N] [--max-desc N] [path ...]

set -uo pipefail

MAX_BODY=15000
MAX_DESC=700
paths=()

while [ $# -gt 0 ]; do
  case "$1" in
    --max-body) MAX_BODY="$2"; shift 2 ;;
    --max-desc) MAX_DESC="$2"; shift 2 ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) paths+=("$1"); shift ;;
  esac
done

root="$(cd "$(dirname "$0")/.." && pwd)"
if [ ${#paths[@]} -eq 0 ]; then
  while IFS= read -r f; do paths+=("$f"); done < <(find "$root/skills" -name SKILL.md | sort)
fi

fail=0
for f in "${paths[@]}"; do
  [ -f "$f" ] || { echo "missing: $f"; fail=1; continue; }
  name="$(basename "$(dirname "$f")")"

  # body = everything after the closing --- of the YAML frontmatter
  body=$(awk 'BEGIN{n=0} /^---$/ && n<2 {n++; next} n>=2 {print}' "$f" | wc -c | tr -d ' ')
  # description = the VALUE of the description: key (frontmatter only, quotes and key stripped)
  desc=$(awk 'BEGIN{n=0} /^---$/{n++; next} n==1' "$f" \
         | awk '/^description:/{f=1} f&&/^[a-zA-Z-]+:/&&!/^description:/{f=0} f' \
         | sed -e '1s/^description:[[:space:]]*"\{0,1\}//' -e '$s/"[[:space:]]*$//' \
         | tr -d '\n' | wc -c | tr -d ' ')

  if [ "$body" -gt "$MAX_BODY" ]; then
    echo "✖ $name: body $body > $MAX_BODY — move a catalogue, template or rubric into references/"
    fail=1
  fi
  if [ "$desc" -gt "$MAX_DESC" ]; then
    echo "✖ $name: description $desc > $MAX_DESC — say WHAT it does and WHEN to use it, nothing more"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "✔ every skill is inside the budget (body ≤ $MAX_BODY, description ≤ $MAX_DESC)"
fi
exit "$fail"
