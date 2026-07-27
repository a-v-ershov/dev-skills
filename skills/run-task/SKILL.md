---
name: run-task
disable-model-invocation: true
description: "Drive ONE task through the full development cycle: the implementer builds it, a separate fresh verifier independently proves the acceptance criteria, its findings go back for exactly one fix round, the quality gate must be green, the human accepts the work (or it is auto-accepted when the diff holds nothing a person could check by hand), the spec is offered a catch-up edit if the product's behavior changed, and a checkpoint commit carrying the task id lands. Two entry points: a task id from the backlog (run-task T07) or a free-form request (run-task 'the card doesn't show the date'), in which case it files the task itself with origin: adhoc and acceptance criteria the user confirms. No iteration loop and no cap to tune — anything the single fix round leaves open escalates to needs_human. Use to build one task; build-tasks calls it repeatedly to work through the backlog. Sequential, single working tree, current branch. It conducts the implementer/verifier agents and the commit skill; it does not duplicate their procedures."
argument-hint: "[<task-id> | <free-form request>]"
---

# Run Task Skill (one task, end to end)

You drive **one** task from `todo` to a committed `done` — or to `needs_human`, honestly. You do not
write the feature or verify it yourself: you spawn the build-loop agents, invoke `commit`, and own the
decisions between the steps. Work is **sequential** on a single working tree on the current branch.

The cycle:

```
task in → show its acceptance criteria → implementer builds (fresh subagent + cheap self-check)
   → verifier (separate agent, ONE pass)
   → fail? → ONE fix round by the SAME implementer → gate (runs the verifier's own tests)
             → still failing / gate red? → needs_human, surface it, stop
   → solve pass (tidy this task's diff) → full gate green
   → acceptance: anything a human could check by hand? yes → show the digest and ask · no → review: auto
   → product behavior changed? → offer the spec catch-up edit (spec_sync), same commit
   → set done → checkpoint commit → regen board
```

**One build, one verification, one fix — then a decision.** There is no loop to bound and no
iteration setting: a finding that survives its own author's targeted fix is a signal about the task,
not something more rounds will resolve (see **`../_shared/build-pipeline/verification-method.md`**).

Each role runs as a **subagent**: the **`implementer`** agent (it preloads `implement-feature`) is
spawned **fresh for this task** and kept through the fix round (so it fixes code it just wrote); the
**`verifier`** agent (it preloads `verify-feature`) is a **separate** agent with no implementer bias.
Lifecycle rules: **`../_shared/build-pipeline/build-config.md`**.

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill and agent follows
the same rule. Never translate code, identifiers, commands, or file paths. (Commit messages are
always English — the `commit` skill enforces that.)

## Modes

Read `.dev-skills/build-plan/.build-config.md` for `mode`. If absent, ask once (default: interactive)
and write it. Full rules: **`../_shared/build-pipeline/build-config.md`**. Backlog schema + `ready`
+ board: **`../_shared/build-pipeline/backlog-format.md`**.

- **interactive** — confirm before starting, **ask the human to accept the finished work** (unless
  there is nothing hand-checkable), stop on `needs_human`.
- **autopilot** — run through: acceptance is recorded as `review: auto` with the reason, and the spec
  catch-up edit is applied and logged rather than offered. `needs_human` still stops.

When **`build-tasks`** invokes you it may pass *"acceptance deferred, manual review at TXX"* — then
skip the acceptance question for this task (record the digest and `review: auto` with that note) but
change nothing else: the verifier, the fix round, the green gate and the `needs_human` stop all still
apply. Deferring acceptance is the human's decision, never yours.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — resolve the input to a task file (id, or file a new adhoc task); confirm it's ready
- [ ] Stage 1: Start — status in_progress; show the acceptance criteria; acquire the env lease
- [ ] Stage 2: Build — spawn the implementer agent (or dispatch a setup task to setup-dev-environment)
- [ ] Stage 3: Verify — spawn the verifier agent, ONCE
- [ ] Stage 4: Fix — one round by the same implementer + green gate, else needs_human
- [ ] Stage 5: Solve pass — tidy this task's own diff, behaviour-preserving; full gate green
- [ ] Stage 6: Accept — human digest + approval, or review: auto when nothing is hand-checkable
- [ ] Stage 7: Spec catch-up — behavior changed and undocumented? propose the edit (spec_sync)
- [ ] Stage 8: Commit — status done + checkpoint commit via the commit skill; release the lease; regen board
```

### Stage 0: Intake
**A task id** (`T012`) → read that task file. **A free-form request** ("the card doesn't show the
date") → file it first: write a task file with `origin: adhoc`, a one-line `summary`, a full
`## Description`, `traces_to` empty for now, and **acceptance criteria you propose and the user
confirms** — a task with criteria you invented alone is a task nobody can verify. Check its size the
way `plan-development` would (one sitting, a vertical slice — "user can X", not "add a table"); if it
is really three tasks, say so and split it before building.

Then confirm the task is **ready**: `status: todo` (or a stale `in_progress` from a killed run) and
every `blocked_by` is `done`. A task with an unmet blocker stops here — say which one.

### Stage 1: Start
Set `status: in_progress` with a `history` entry. **Show the human the acceptance criteria** this task
will be judged by, one line each — it is the last cheap moment to catch a criterion that describes the
wrong thing. Acquire the **env lease** (**`../_shared/build-pipeline/env-access.md`**); subagents
inherit it.

### Stage 2: Build
Dispatch by `type`:
- **`setup`** → invoke `setup-dev-environment` (scoped to this task's work), then go to Stage 5.
- **`feature`** / **`rework`** → **spawn the `implementer` agent** (`subagent_type: implementer`,
  fresh, clean context — it preloads `implement-feature`). It builds, self-checks the happy path, and
  gets the cheap gate green before handing back.
- **`verify`** (cross-cutting) → skip to Stage 3 and spawn the verifier directly.

### Stage 3: Verify (once)
Spawn the **`verifier` agent** (`subagent_type: verifier`, separate agent — it preloads
`verify-feature`). It authors adversarial tests for the acceptance criteria, drives the real stack,
and proves observable outcomes. It runs **once**: its findings must be actionable on their own.

### Stage 4: Fix (one round)
**Pass** → Stage 5. **Fail** → hand the findings to the **same** implementer agent for **exactly one**
fix round, then run the **quality gate** — which now includes the verifier's committed tests, so the
fix is checked without re-spawning the verifier.
- Green → Stage 5.
- Still red, or a finding the implementer says it cannot close → set `status: needs_human`, append a
  `## Log` entry naming what still fails and what was tried, release the lease, and **stop**. Report
  it plainly. **Never a second fix round.**

### Stage 5: Solve pass + full gate
Direct the **same implementer agent** to a light cleanup **scoped to this task's own diff** — remove
dead or duplicated code it introduced, collapse needless abstraction, drop over-built generality —
strictly **behaviour-preserving**. Pre-existing rot in code this task didn't touch is out of scope:
note it as a `rework` task, never tidy it here. (Agents over-produce and don't feel maintenance cost;
a deliberate pass stops bloat from compounding.)

Then confirm the **full quality gate** is green (`make check` — lint/type + the whole accumulated
suite, which now includes the verifier's tests, so the tidy stays honest;
**`../_shared/build-pipeline/quality-gate.md`**). Red is never committed and never triggers another
round — it goes to `needs_human`.

### Stage 6: Accept
Look at the **actual diff** and decide whether a person could check anything by hand:

- **Nothing hand-checkable** (the diff is tests, internal logic, config; every criterion was proven by
  the verifier) → accept it yourself, set `review: auto`, and record the one-line reason. Don't
  manufacture a question.
- **Something hand-checkable** → show a short digest and, in interactive, wait:
  > **Built:** <what it does now, in plain language — not file names>
  > **See it yourself:** <the URL/screen · which seeded user · the exact steps>
  > **Already proven:** <what the verifier asserted, one line each>
  In autopilot, record the same digest with `review: auto`.

Deferring acceptance is the human's call. If they ask for changes, that is a **new task** (or a
`rework` one) — not a reopening of this cycle.

### Stage 7: Spec catch-up
If the work changed observable product behavior the spec doesn't describe — a new screen, a changed
rule, an `adhoc` task with no `traces_to` — set `spec_sync: pending` and **propose the concrete
edit**, written out rather than described: the feature line for `product-requirements.research.md`,
the step or screen for `user-flows.research.md`. Interactive: offer it, apply on a yes. Autopilot:
apply and log it. It lands in the **same commit** as the code, so the spec never drifts by a whole
task; then set `spec_sync: done`. If the user declines, leave `spec_sync: pending` — the board
surfaces it and the next planning run will see it. Never block the task on this.

### Stage 8: Commit + hand back
Set `status: done` (history entry) and make a **checkpoint commit** via the `commit` skill — the
message carries this task's id (e.g. `[T012]`) and what was done; `commit` splits a substantial
cleanup into its own `refactor:` commit. Release the env lease. Regenerate
`.dev-skills/build-plan/board.md` from the task files. Report in three lines: what was built, how it
was proven, what state the task is in.

## Rules

1. **Conduct, don't duplicate.** Never write or verify the feature yourself — spawn the `implementer`
   and `verifier` agents; invoke `setup-dev-environment` and `commit`.
2. **Verify in a separate, fresh agent** — never let the implementer approve its own work.
3. **One build, one verification, one fix.** No second fix round, no counter: whatever remains open
   goes to `needs_human`, in both modes. Never re-spawn the verifier to "check the fix" — its
   committed tests do that through the gate.
4. **Never commit red.** A red gate is `needs_human`, not another attempt.
5. **Accept before you commit.** Show what was built and how to check it; skip the question only when
   the diff genuinely holds nothing hand-checkable (`review: auto`, with the reason). Never mark
   `auto` to avoid an awkward answer.
6. **Let the spec catch up in the same commit.** A stale spec is what makes the *next* plan wrong.
7. **One task, one working tree, current branch.** No worktrees, no parallel tasks, no new branch
   unless the user asked for one.
8. **Hold the env lease for the task's span** and release it when the task leaves — committed or
   escalated. See **`../_shared/build-pipeline/env-access.md`**.
