---
name: audit-skills
description: "Audit the skills, slash commands and subagents that ran in this Claude Code session — a standalone meta-utility invoked by hand, NOT part of the release chain and never run by release-product. Use it after a spec, build or release run to make the skills that drove it better next time. It reads the session transcript (scan_session.py) plus the live conversation and works out how each target actually behaved: steps it got wrong or skipped, gates it passed silently, work it repeated, questions it should not have asked, calls that were needlessly slow, invariants of this set it broke (one branch, the user's language, its own write scope, English commit messages) and artifacts it produced that do not match their own templates. Then it reports numbered, file-level edit proposals — pointing each one at the file that actually owns the rule (a SKILL.md, an agent, or a _shared/*.md method the whole pipeline reads) — and STOPS. It changes nothing on its own initiative: a proposal is applied only after the caller names the numbers, and even then only to skill/agent/command files, never to product code and never to the plugin version. Invoked manually as /audit-skills [<skill or agent name>] [--session <id>]."
argument-hint: "[<skill or agent name>] [--session <id>]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/skills/*' '*/agents/*' '*/commands/*' '*/.claude/*' '*/CLAUDE.md' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Audit Skills Skill

A standalone meta-utility. It looks back at the session you are in, works out how the **skills, slash
commands and subagents** that ran in it actually behaved, and proposes concrete edits to their source
files.

```
session transcript + live conversation + the artifacts produced → per-target findings → numbered proposals → STOP → apply only what was picked
```

This is **not** a release audit. `audit-security` / `audit-performance` / `audit-product` audit the
*product* against its spec and are run by `release-product`; this one audits the *tooling* — the
skills themselves — and is only ever invoked by hand. It never files rework tasks and never writes
into `.dev-skills/`.

## The one hard rule — propose, never apply

**This skill does not edit anything on its own initiative.** Not the skill it just audited, not a
"tiny obvious typo", not "while I'm in there". It reads, it reports, it ends the turn. Edits happen
only in a later turn, and only for the proposals the caller explicitly picked (**Stage 6**).

It is also read-only about the session itself: it never re-runs a skill "to check", never repeats a
subagent, and never touches the repository it is auditing. A write-scope guard backs this up — the
only files it can ever write are skill, agent, command and `CLAUDE.md` files; product code and the
version-carrying manifests are out of reach.

## Inputs and outputs

- **Reads:** the session transcript via `scan_session.py`; the conversation you can still see; the
  **source file of every target** (`SKILL.md`, `agents/*.md`, and the `_shared/*.md` method it
  inherits its procedure from); the **artifacts the run produced** (`.dev-skills/**`, `DESIGN.md`,
  backlog tasks) against the template they were written from.
- **Writes:** nothing, until the caller picks proposals — then `Edit`s to the skill / agent /
  command / `CLAUDE.md` files those proposals named. Never product code, never `.dev-skills/**`,
  never `plugin.json` / `marketplace.json`.
- **`$ARGUMENTS`:** `<skill or agent name>` — audit only that target (e.g. `run-task`,
  `dev-skills:verify-feature`, `implementer`); substring match is fine, default is every skill and
  agent that ran. `--session <id>` — audit a previous session (ids: `scan_session.py --list`).

## Language

Respond and reason in whatever language the user addressed you in — the report, the findings and the
questions all go in that language. Never translate code, identifiers, file paths, commands, skill or
agent names, or text you quote verbatim from a skill file.

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate
it (`findings` → замечания, `gate` → контрольная точка, `rework` → доработка), keep `fork`, `commit`,
`backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`, `onboarding`, `sanity check` in
Latin script and uninflected, never build hybrid verbs («закоммитить», «отскаффолдить»), and leave
template section headings and task fields (`## Forks / Decisions log`, `type: rework`) verbatim.

## Git workflow

**One branch — the current one, normally `main`.** Never create a branch, never switch to another
branch, and never open a worktree on your own initiative. **The single exception:** the user
explicitly asked for a separate branch in this session. Applying proposals is not a reason to branch,
and this skill never commits — committing is `/commit`'s job and the user's call. Full rule:
**`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Evidence — run scan_session.py; read the digest alongside the conversation
- [ ] Stage 1: Sources — read every target's file + the _shared method it inherits; note who owns each file
- [ ] Stage 2: Lenses — work the rubric's six lenses + the four for this set; every finding carries a fact
- [ ] Stage 3: Artifacts — compare what the run produced against the template it was written from
- [ ] Stage 4: Proposals — turn each finding into a specific edit to the file that owns the rule
- [ ] Stage 5: Rank + report (max 8), then STOP — the report is the last message of the turn
- [ ] Stage 6: Apply — only the numbers the caller picked, nothing adjacent
```

### Stage 0: Evidence

Resolve the script directory once and reuse it:

```
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-.claude}/skills/audit-skills"
[ -f "$SKILL_DIR/scan_session.py" ] || SKILL_DIR=".claude/skills/audit-skills"
python3 "$SKILL_DIR/scan_session.py"            # add --session <id> if one was given
```

The digest gives you what the conversation can't: which skills were loaded and **from which file on
disk**, per-run wall time and tool mix, subagent cost per run *and per role*, the slowest calls,
repeated calls, every file written, the invariant tripwires, every error and denial, and the user's
own turns verbatim.

You have **two sources and they answer different questions**:

| Source | Answers |
|---|---|
| The digest (transcript) | *What happened* — including turns already compacted out of your context |
| The conversation you can still see | *What it was for* — intent, what the user actually wanted, whether the result was any good |

Read both. A finding built on only one of them is usually wrong: the digest alone can't tell a slow
call from a correctly patient one, and the conversation alone hides everything before a compaction.

If the script fails (no transcript, unreadable file), say so plainly in one line and audit from the
conversation you can see — do not silently pretend you had the full picture.

### Stage 1: Sources

For each skill in the digest's **Skills loaded** table, `Read` its source file. A row marked
`⚠︎ found by search` was located by guessing — open it and confirm the `name:` in its frontmatter
matches before you say a single word about it.

For subagents, read the agent definition (`agents/<type>.md` in the plugin, `.claude/agents/`, or
`~/.claude/agents/`). In this set most agents are **thin wrappers** that preload a procedure skill —
so read that skill too, and expect the defect to live there rather than in the wrapper. Then read
the `_shared/*.md` method the skill points at: when a rule is stated once in `_shared/` and copied
into three skills, the copy is not where you fix it.

For an expensive or repeated agent role, open one subagent transcript
(`<session>/subagents/agent-<id>.jsonl`) — the main transcript shows what an agent cost, not what it
did.

**You may not write a finding about a file you have not read.** No exceptions — a finding is a claim
about specific wording in a specific file.

Note who owns each file:

| Location | Editable? |
|---|---|
| A repo checkout (`~/code/<repo>/skills/…`), `~/.claude/skills/`, `<project>/.claude/skills/` | Yes |
| `~/.claude/plugins/cache/…` | **No** — the next `/plugin update` discards the edit. Report it as upstream feedback, and if the same skill also lives in a repo the user maintains, point the proposal at the repo |
| Claude Code built-ins with no file on disk | No — report as behaviour to work around, not as an edit |

### Stage 2: Lenses

`Read` `$SKILL_DIR/references/rubric.md` and work through its six lenses — correctness, procedure
drift, triggering, redundancy, speed, user friction — each with the signals that betray it and the
evidence that proves it. That file also holds the severity scale and the full report template.

When any target belongs to a skill set with shared methodology and pipelines (this one does), also
`Read` `$SKILL_DIR/references/dev-skills-lenses.md`: the invariants of the set, artifact fidelity,
orchestration and hand-off, and where the fix belongs.

Every finding needs a **fact from the evidence** attached: a timestamp, a user quote, a call count,
a duration. "This could be clearer" is not a finding.

### Stage 3: Artifacts

A skill in this set is judged by what it produced, not only by how it ran. For each target that
writes a document, open the artifact **and** the template it was written from
(`skills/<name>/references/*-template.md`, `_shared/build-pipeline/backlog-format.md`,
`_shared/release-pipeline/report-template.md`) and compare them: missing sections, an empty
`## Sources`, an unfilled `## Forks / Decisions log`, tasks with no acceptance criteria or an empty
`traces_to`, a status the run never updated. A section the template requires and the output lacks is
a defect in the skill's wording — usually the section is described in prose but never appears in the
skill's own checklist. Details: `references/dev-skills-lenses.md`.

Skip this stage cleanly when the session produced no artifacts, and say so — don't invent a gap.

### Stage 4: Proposals

A proposal is a **specific edit to a specific file**, not advice. For each one:

- the file and the section/heading inside it — and it must be the file that *owns* the rule
  (`_shared/*.md` when the behaviour is shared, the `SKILL.md` when it is that skill's own, the
  agent when it is the wrapper's);
- the line or rule as it stands now (quoted) and what it becomes;
- what it would have changed in this session, in one sentence;
- the cost: every line added is context re-read on every future run — say when a proposal is a net
  addition, and prefer tightening or replacing existing wording over appending to it. If a skill's
  body is already at its budget, propose moving detail into `references/` rather than growing it.

Drop anything you can't express as an edit — unless it's a genuine constraint of the harness or of
the model, in which case keep it and label it **no file change — note only**.

### Stage 5: Rank + report, then stop

Order by severity (🔴 blocker → 🟡 major → ⚪ minor, defined for skills in `rubric.md`), and within a
severity by how cheap the fix is. Number the proposals in a single sequence across all targets, so
the caller can answer with numbers. Cap the report at the **8 strongest proposals** — a long list is
a list nobody acts on. Say how many you dropped.

The report is the **final text message of the turn**. No tool call after it, no work started, no
"and I've already fixed #3". Some UIs (e.g. the VSCode extension) render neither text printed before
a tool call nor `AskUserQuestion` previews — so the report has to be plain chat text that ends the
turn. Full template with a worked example: `references/rubric.md`.

If nothing is worth proposing, say exactly that and stop. A clean session is a valid result — do not
manufacture findings to fill the report.

### Stage 6: Apply, only when told to

Triggered by the caller naming numbers (`1, 4`), `all` / `все`, or describing a change. Then:

1. Apply **only** the picked proposals, as `Edit`s to the files named in them.
2. Keep the edits minimal — change the wording the proposal quoted, nothing adjacent.
3. When the rule is duplicated by design (the `## Language` and `## Git workflow` sections every
   skill carries), fix `_shared/` **and** the copies that drifted — a half-applied invariant is worse
   than the original defect. Say which files you touched.
4. **Do not touch the plugin's `version`** (`plugin.json` / `marketplace.json` — the user's to bump,
   see `CLAUDE.md`), do not commit, do not push.
5. Report per proposal: file, what changed, one line each. Say plainly if one turned out not to be
   applicable once you had the file open — don't improvise a different edit in its place.

## Rules

1. **Never edit a skill unasked** — Stage 6 runs only after an explicit pick. This is the skill's
   whole point.
2. **Never propose a change to a file you did not read**, and never quote a rule you did not see in
   it.
3. **Fix the rule where it lives** — `_shared/` for shared methodology, the `SKILL.md` for that
   skill's own procedure, the agent for the wrapper. Never paste a shared rule into a skill because
   it was easier to find there.
4. **Don't legislate for one incident.** One misstep can be noise; say so and propose the rule only
   if the evidence shows the failure mode repeating, or if the single occurrence was expensive.
5. **Don't rewrite a skill wholesale.** If a target is beyond repair by edits, say that in one line
   and stop — a rewrite is a separate decision the user makes.
6. **Don't audit what didn't run.** Skills absent from the digest get no findings, however tempting.
   A tripwire is a signal, not a verdict — read the conversation around it first.
7. **The digest can contain sensitive fragments** (commands, paths, prompts) and stays in the
   conversation — never write it to a file, never send it anywhere. `scan_session.py` itself is
   stdlib-only and read-only.
8. **Self-audit is fair game.** If `audit-skills` itself ran badly, propose fixes to this file too.
