#!/bin/sh
# guard-write-scope.sh — a PreToolUse guard for Write|Edit.
#
# Enforces a write-scope invariant for skills that must not edit product code:
#   - verify-feature  → may write tests + the backlog (.dev-skills/build-plan), nothing else
#   - audit-*         → may write findings (.dev-skills/**) + the backlog, nothing else
#
# It reads the Claude Code hook JSON from stdin, extracts tool_input.file_path, and
# ALLOWS the write only if that path matches one of the glob patterns passed as
# arguments. Any other write is BLOCKED with exit code 2 (a blocking denial whose
# stderr is fed back to the agent as an actionable message).
#
# Usage (from a skill's frontmatter `hooks` block):
#   guard-write-scope.sh '*/tests/*' '*test*' '*/.dev-skills/build-plan/*' '/tmp/*'
#
# Patterns are shell globs matched (whole-string) against the absolute file path,
# so wrap substrings in '*...*' (e.g. '*/.dev-skills/release/*').

input=$(cat)

# Extract the first "file_path":"..." value. Paths do not contain double quotes,
# so a single sed capture is enough and avoids a hard dependency on jq/python.
file_path=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)

# No path on a Write|Edit call we recognize → nothing to guard; allow.
[ -z "$file_path" ] && exit 0

for pat in "$@"; do
  # shellcheck disable=SC2254  # $pat is an intentional glob pattern, not a literal.
  case "$file_path" in
    $pat) exit 0 ;;
  esac
done

# Matched no allowed pattern → block, with a message the agent can act on.
{
  echo "Blocked write to: $file_path"
  echo "This role may only write within: $*"
  echo "If the product code needs a change, report it as a finding for the implementer — do not edit it here."
} >&2
exit 2
