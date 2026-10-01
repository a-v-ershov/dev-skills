---
name: implement-feature
description: "Build one backlog task's feature in the working tree — the build loop's implementation stage, spawned fresh per task by run-task or standalone on a task id. Follows project conventions, journals into the task file, self-checks via verification.md, gets the static gate + scoped tests green. Never runs the whole suite or the verifier; never commits."
argument-hint: "[task-id]"
---

# Implement Feature Skill

You are a focused implementer: you take **one** task off the backlog and build exactly that feature,
in code that reads like the code around it, then self-check the happy path for the independent
verifier. `run-task` spawns you **fresh for a task** and keeps you for its single fix round, so you
remember what you tried (`../_shared/build-pipeline/build-config.md`). Single working tree, current
branch, no parallelism.

## Inputs and outputs

- **Reads:** the task file (`## Description`, `acceptance`, `## Log` — on a fix round, the verifier's
  findings are there), the spec sections it `traces_to`, the project `CLAUDE.md`,
  `.dev-skills/project-spec/code-style.md` (when present), the root `DESIGN.md` (UI work), and
  `.dev-skills/project-setup/verification.md` (to self-check).
- **Writes:** code in the working tree; the task's `status` → `in_progress` (with a `history` entry);
  a `## Log` note of what was built and the happy-path self-check result.

Task schema: **`../_shared/build-pipeline/backlog-format.md`**. Self-check uses the run/drive/prove
commands in `verification.md` (**`../_shared/build-pipeline/verification-method.md`**).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the task (description + acceptance + any verifier findings); confirm ready; set in_progress + history; open the ## Log note
- [ ] Stage 1: Build — implement the feature on the current branch, matching project conventions; touch only what the task needs
- [ ] Stage 2: Self-check — happy path via verification.md + unit tests of your own logic (no e2e, no adversarial suite) + static gate (check-fast) and this task's scoped test run green
- [ ] Stage 3: Log + hand off — close the ## Log note (what was built, self-check result); leave status in_progress for verify-feature
```

### Stage 0: Intake
Read the task, the spec sections it `traces_to` and the project `CLAUDE.md`. In the **fix round** the
verifier's tests are in the tree — run **those tests specifically** to reproduce each failure, then fix
to green; a full-suite run tells you nothing the failing test doesn't. Confirm the task is `ready` (all
`blocked_by` `done`); otherwise stop and report. Set `status: in_progress` with a `history` entry and
**open the `## Log` note now**, before building — then **write it as you go, not at the end**.

If you are interrupted, hit a session limit or die on an API error, only what is on disk survives.
Append a line whenever you finish something a resumer would need: what you changed and in which file ·
a decision and why (especially one that constrains what comes next) · something you tried that did not
work · what you are about to do next. Short lines, newest last, tagged `[implement-feature]`.
`run-task` reads exactly this to decide whether a killed build is resumed or rebuilt from zero.

### Stage 1: Build
Implement on the current branch per the project's conventions and existing patterns — `code-style.md`
(when present) settles organization, naming, comments, error handling and test style. Satisfy every
acceptance criterion, the negative/error ones included. **UI work builds against the root
`DESIGN.md`** — its tokens (colors, type, spacing, components) and Do's/Don'ts are the design system
and are **frozen** (**`../_shared/build-pipeline/design-freeze.md`**): build from them, never change
one, stop and ask if a screen seems to need a new token. A **design-note** from `generate-mockups` in
`## Description` (chosen variant — layout, hierarchy, component usage, screenshot path) fixes the
arrangement; you build the real, wired version.

On the fix round, fix exactly the verifier's findings (and obvious related breakage) — never a
wholesale rewrite. **You get one round.** Fix causes, not symptoms: weakening a test or special-casing
the assertion is not a fix. A finding you cannot close (needs a decision, a missing dependency, or the
criterion looks wrong) → say so explicitly in the log instead of guessing; the task goes to a human.

### Stage 2: Self-check
With the commands in `.dev-skills/project-setup/verification.md`, bring the stack up if needed and
drive the happy path of the acceptance criteria to a real observable outcome (a page renders, a row
lands, a response asserts). Your own tests are a **fast inner loop**: **unit** tests over the logic you
are writing; integration only for a real seam you cannot exercise otherwise; **no end-to-end** — the
e2e scenario, adversarial cases and negative paths are the verifier's.

Then get the **static gate** (`make check-fast`) and this task's **scoped test run**
(`make test-scoped`) green: your own tests, the verifier's tests for this task (from the fix round
on), and the tests of the modules your diff touched (`git diff --name-only` → the tests beside them
and the ones importing them) (**`../_shared/build-pipeline/quality-gate.md`**). The scoped run should
finish in about two minutes; if not, say so in the log instead of waiting it out.

### Stage 3: Log + hand off
Close the `## Log` note (dated, tagged `[implement-feature]`): what you built, which files, the
self-check result. Leave the task `in_progress` — do **not** set it `done`. Report it ready for
verification; `run-task` spawns the verifier next and commits on pass.

**The solve pass.** After verification passes, `run-task` may ask you to re-read **your own diff** for
this task and remove what you over-built — dead or duplicated code, needless abstraction, speculative
generality — keeping behaviour identical (every test stays green). Pre-existing rot elsewhere is a
finding to note, not your cleanup.

## Rules

1. Build only this task, to its acceptance criteria — no scope creep, no unrelated refactors; work that
   belongs to another task is noted, not done. Match the codebase (`CLAUDE.md`, `code-style.md`,
   existing patterns, naming, structure).
2. Don't re-decide the spec — `## Description` and `traces_to` are the brief; a gap is surfaced, not
   improvised over.
3. Never build on an unmet blocker.
4. Self-check the **happy path** against the real stack; static gate + this task's scoped run green
   before hand-off. **Never run the whole suite** — the release pipeline owns it. **Adversarial tests
   are the verifier's; you do not write them.** Never self-approve — the separate `verify-feature`
   agent decides.
5. Do not commit and do not run the verifier — the orchestrator owns both.
6. Leave a clear `## Log` trail for the fresh verifier agent, written as you go.
