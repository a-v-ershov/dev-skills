---
name: audit-skills
description: "Audit how this plugin's skills, slash commands and subagents behaved across every recorded Claude Code session that ran them (default), one session, or a date window — transcripts via scan_session.py, plus artifacts — and propose numbered edits to the files that own each rule. Proposes only; nothing is applied until the caller names numbers. By hand; never in the release chain."
argument-hint: "[<skill or agent name>] [--session <id> | --current] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--days N]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/skills/*' '*/agents/*' '*/commands/*' '*/.claude/*' '*/CLAUDE.md' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Audit Skills Skill

Works out how the **skills, slash commands and subagents** of this set behaved across the recorded
sessions that ran them, and proposes concrete edits to their source files.

```
every session that ran the plugin → cross-session digest → drill into the sessions behind the strongest signals
  (+ artifacts) → per-target findings → numbered proposals → STOP → apply only what was picked
```

Unlike `audit-security` / `audit-performance` / `audit-product` (the *product*, for `release-product`),
this audits the *tooling*, by hand only; it files no rework tasks and never writes into `.dev-skills/`.

## The one hard rule — propose, never apply

**Edit nothing on your own initiative** — not even a "tiny obvious typo". Read, report, end the turn;
edits come in a later turn, only for the proposals the caller picked (**Stage 6**). Never re-run a
skill "to check", repeat a subagent or touch the audited repository.

## Inputs and outputs

- **Reads:** the transcripts under `~/.claude/projects/` (`scan_session.py`), the visible
  conversation when the audited session is this one, every target's source (`SKILL.md`,
  `agents/*.md`, its `_shared/*.md` method), the artifacts the runs produced (`.dev-skills/**`,
  `DESIGN.md`, backlog tasks) in the projects the digest names.
- **Writes:** nothing until the caller picks — then `Edit`s to skill / agent / command / `CLAUDE.md`
  files only (the write-scope guard enforces it). Never product code, `.dev-skills/**`,
  `plugin.json` / `marketplace.json`.
- **`$ARGUMENTS`** (scope; default — **every session on disk that ran a `dev-skills:` skill**):
  `<skill or agent name>` — only that target (`run-task`, `dev-skills:verify-feature`, `implementer`;
  substring match) · `--session <id>` — one session (full id or the short id the digest prints) ·
  `--current` — this session only · `--since` / `--until YYYY-MM-DD`, `--days N` — a window. Sessions
  and ids: `scan_session.py --list` (takes the same window flags).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths, skill or agent names, or text quoted from a skill file.
Commit messages are always English. **One branch — the current one** (normally `main`): never branch,
switch or open a worktree unless the user explicitly asked in this session —
**`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Evidence — run scan_session.py (all sessions, or the scope given); drill into the sessions behind the strongest signals
- [ ] Stage 1: Sources — read every target's file + the _shared method it inherits; note who owns each file
- [ ] Stage 2: Lenses — work the rubric's seven lenses + the four for this set; every finding carries a fact
- [ ] Stage 3: Artifacts — compare what the run produced against the template it was written from
- [ ] Stage 4: Proposals — turn each finding into a specific edit to the file that owns the rule
- [ ] Stage 5: Rank + report (max 8), then STOP — the report is the last message of the turn
- [ ] Stage 6: Apply — only the numbers the caller picked, nothing adjacent
```

### Stage 0: Evidence

```
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-.claude}/skills/audit-skills"
[ -f "$SKILL_DIR/scan_session.py" ] || SKILL_DIR=".claude/skills/audit-skills"
python3 "$SKILL_DIR/scan_session.py"            # pass the scope flags the caller gave, unchanged
```

1. **Cross-session digest (default).** It finds every session where a `dev-skills:` skill actually
   ran — the model's `Skill` call or a typed `/dev-skills:<skill>` — and prints a map: one row per
   session (with the plugin version it loaded), per-skill aggregates, subagent cost by role,
   tripwires and errors with how many sessions show them, and the user turns inside skill runs (⚑ =
   interrupt or correction-shaped). It tells you *where to look*, not what went wrong.
2. **Drill down.** Pick the **≤4 sessions** behind the strongest signals — ⚑ turns, a skill with many
   user turns or errors inside its runs, a recurring tripwire or error, an expensive role — and run
   `scan_session.py --session <short id>` on each for the full digest (tool mix, slow and repeated
   calls, files written, every user turn, subagent transcripts). The user turns say *what it was
   for*; read around every signal before calling it a finding.
3. **Coverage.** The digest header names the oldest transcript on disk — Claude Code deletes them
   after `cleanupPeriodDays` (30 days by default). Say in the report what period you covered; raising
   the setting is the user's call — mention it, never change it.

`--session` / `--current` skip step 1 (one session; with `--current` the live conversation is
evidence too). No session in scope → say so and stop. Script fails → say so in one line, audit from
the conversation.

### Stage 1: Sources

`Read` every skill in the digest's **Skills loaded** table (a row marked `⚠︎ found by search` was
guessed — confirm its frontmatter `name:` first). For subagents read the definition (`agents/<type>.md`
in the plugin, `.claude/agents/`, `~/.claude/agents/`); most are **thin wrappers** preloading a
procedure skill — read that too, the defect usually lives there — then the `_shared/*.md` method it
points at. For an expensive or repeated role open one subagent transcript
(`<session>/subagents/agent-<id>.jsonl`): the main one shows cost, not what it did.

**Version check.** Older sessions may have run an older skill — the digest's `plugin` column says
which (a version, or `local checkout`). Before a finding becomes a proposal, confirm the **current**
file still carries its cause; already fixed → drop it.

Ownership: a repo checkout (`~/code/<repo>/skills/…`), `~/.claude/skills/`,
`<project>/.claude/skills/` → editable. `~/.claude/plugins/cache/…` → **no** (the next
`/plugin update` discards it): upstream feedback, or point the proposal at the user's repo if the skill
lives there too. Claude Code built-ins with no file → behaviour to work around.

### Stage 2: Lenses

`Read` `$SKILL_DIR/references/rubric.md` — seven lenses (correctness, procedure drift, triggering,
redundancy, speed, user friction, simplicity), the severity scale, the report template. For a set with
shared methodology (this one), also `Read` `$SKILL_DIR/references/dev-skills-lenses.md`: invariants of
the set, artifact fidelity, orchestration and hand-off, where the fix belongs. Every finding carries a
**fact from the evidence** — session short id + timestamp, user quote, call count, duration — and
**how many sessions show it**; "this could be clearer" is not a finding.

### Stage 3: Artifacts

Compare each written document with its template (`skills/<name>/references/*-template.md`,
`_shared/build-pipeline/backlog-format.md`, `_shared/release-pipeline/report-template.md`): missing
sections, an empty `## Sources`, an unfilled `## Forks / Decisions log`, tasks without acceptance
criteria or with an empty `traces_to`, a status never updated. A missing required section is a defect
in the skill's wording — usually described in prose but absent from its checklist
(`references/dev-skills-lenses.md`). No artifacts → skip and say so.

### Stage 4: Proposals

A proposal is a **specific edit to a specific file**, not advice:
- the file and section that *owns* the rule — `_shared/*.md` when shared, the `SKILL.md` for the
  skill's own, the agent for the wrapper's;
- the current line (quoted) and what it becomes;
- what it would have changed in this session, one sentence;
- the cost — every added line is re-read on every run: flag a net addition, prefer tightening over
  appending, move detail into `references/` when a body is at its budget.

Drop anything not expressible as an edit, except a genuine harness or model constraint — label it
**no file change — note only**.

### Stage 5: Rank + report, then stop

Open with the scope covered (window, sessions, projects). Order by severity (🔴 blocker → 🟡 major →
⚪ minor, per `rubric.md`), then by how many sessions show it, then by cheapness of fix; one
number sequence across all targets; cap at the **8 strongest** and say how many you dropped. The
report is the **final plain-text message of the turn** — no tool call after it, nothing "already
fixed" (some UIs render neither text before a tool call nor `AskUserQuestion` previews). Template:
`references/rubric.md`. Nothing worth proposing → say so and stop; don't manufacture findings.

### Stage 6: Apply, only when told to

Triggered by numbers (`1, 4`), `all` / `все`, or a described change:

1. Apply **only** the picked proposals, as `Edit`s to the files they name — the quoted wording, nothing
   adjacent.
2. A rule duplicated by design (the `## Language` and `## Git workflow` sections every skill carries):
   fix `_shared/` **and** the drifted copies; say which files you touched.
3. **Never touch the plugin's `version`** (`plugin.json` / `marketplace.json` — the user's, see
   `CLAUDE.md`); never commit (`/commit`'s job, the user's call), never push.
4. Report per proposal: file, what changed, one line. Not applicable once the file is open → say so;
   don't improvise a different edit.

## Rules

1. **Never edit a skill unasked** — Stage 6 runs only after an explicit pick.
2. **Never write a finding about, or quote a rule from, a file you did not read.**
3. **Fix the rule where it lives** (Stage 4) — never paste a shared rule into a skill.
4. **Don't legislate for one incident** — a failure repeating across sessions, or one expensive
   occurrence; say how many sessions show it.
5. **Don't rewrite a skill wholesale** — a target beyond repair by edits gets one line saying so.
6. **Don't audit what didn't run** in the scope. A tripwire is a signal, not a verdict — read around it
   first; a finding the current file already fixes is dropped.
7. **The digests can hold sensitive fragments** from every project — never write them to a file or
   send them anywhere. `scan_session.py` is stdlib-only and read-only; never edit Claude Code settings.
8. **Self-audit is fair game** — if `audit-skills` ran badly, propose fixes to this file too.
