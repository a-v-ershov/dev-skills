---
name: run-task
description: "Drive ONE task through the full development cycle: the implementer builds it, a separate fresh verifier independently proves the acceptance criteria, its findings go back for exactly one fix round, the static gate plus this task's scoped test selection must be green (the whole suite is never run here — that is the release pipeline's), the human accepts the work (or it is auto-accepted when the diff holds nothing a person could check by hand), the spec is offered a catch-up edit if the product's behavior changed, and a checkpoint commit carrying the task id lands. Two entry points: a task id from the backlog (run-task T07) or a free-form request (run-task 'the card doesn't show the date'), in which case it files the task itself with origin: adhoc and acceptance criteria the user confirms. No iteration loop and no cap to tune — anything the single fix round leaves open escalates to needs_human. Use to build one task; build-tasks calls it repeatedly to work through the backlog. Sequential, single working tree, current branch. It conducts the implementer/verifier agents and the commit skill; it does not duplicate their procedures."
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
   → fail? → ONE fix round by the SAME implementer → static gate + this task's scoped tests
             → still failing / gate red? → needs_human, surface it, stop
   → solve pass (tidy this task's diff) → static gate + scoped tests green
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

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Git workflow

**One branch — the current one, normally `main`.** Never create a branch, never switch to another
branch, and never open a worktree on your own initiative. **The single exception:** the user
explicitly asked for a separate branch in this session — then use the name they gave (or propose one
and confirm it) and say plainly which branch the work is on. A request to commit, to fix, or to ship
is not a request to branch. Every agent you spawn inherits this — pass it down together with
the language rule, and an agent that thinks the work needs a branch reports it to you instead of
creating one. Full rule: **`../_shared/git-workflow.md`**.

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
- [ ] Stage 1: Start — status in_progress; show the acceptance criteria; acquire the env lease; start the clock
- [ ] Stage 2: Build — spawn the implementer agent (or dispatch a setup task to setup-dev-environment)
- [ ] Stage 3: Verify — spawn the verifier agent, ONCE
- [ ] Stage 4: Fix — one round by the same implementer + green gate, else needs_human
- [ ] Stage 5: Solve pass — tidy this task's own diff, behaviour-preserving; static gate + scoped tests green
- [ ] Stage 6: Accept — human digest + approval, or review: auto when nothing is hand-checkable
- [ ] Stage 7: Spec catch-up — behavior changed and undocumented? propose the edit (spec_sync)
- [ ] Stage 8: Commit — status done + timings + checkpoint commit via the commit skill; release the lease; regen board
```

### Timing the stages

**You** time the work, because nobody else can: an agent cannot see its own clock, and the duration of
a subagent never comes back inside the result you receive — only its text does. So bracket the stages
you dispatch. At Stage 1, and at each boundary of Stages 2–5, take one reading:

```sh
date -u '+%Y-%m-%dT%H:%M:%SZ %s'
```

Keep the epoch seconds and subtract: `build` (Stage 2), `verify` (Stage 3), `fix` (Stage 4 — only when
the fix round actually ran), `solve` (Stage 5), and `total` (Stage 1 → the end). Write them into the
task's `timings` block in **one** edit when the task leaves you, at Stage 8 or at the `needs_human`
stop. Schema and how to read the numbers: **`../_shared/build-pipeline/backlog-format.md`**.

### Stage 0: Intake
**A task id** (`T012`) → read that task file. **A free-form request** ("the card doesn't show the
date") → file it first: write a task file with `origin: adhoc`, a one-line `summary`, a full
`## Description`, `traces_to` empty for now, and **acceptance criteria you propose and the user
confirms** — a task with criteria you invented alone is a task nobody can verify. Size it the way
`plan-development` does (**`../_shared/build-pipeline/planning-method.md`**): **one coarse task is the
default**, even when the request names several things — a whole screen with its CRUD, a flow end to
end, a fix and the three places it repeats are one task, and the parts become `acceptance` entries.
Split only when one sitting genuinely cannot hold it (different subsystems, or one part blocked on the
other) — then say so, and remember the backlog carries **at most 15 open tasks** across the whole
product, so filing three where one would do spends a budget the plan needs.

Then confirm the task is **ready**: `status: todo` (or a stale `in_progress` from a killed run) and
every `blocked_by` is `done`. A task with an unmet blocker stops here — say which one.

### Stage 1: Start
Set `status: in_progress` with a `history` entry, and **regenerate `board.md` now** so the task moves
out of `Ready` into `In progress` — the build runs for an hour or more, and a board that only catches
up at the commit shows "nothing in progress" for exactly the stretch someone would look at it.
**Show the human the acceptance criteria** this task
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

**What the spawn prompt must carry.** The agent is fresh and knows nothing you know; a prompt that
passes only a task id makes it rediscover the project. Name: the task file's path · the project
`CLAUDE.md` and its invariants · **what recently changed** — the files the last closed tasks
rewrote, so it reads the current state instead of trusting line numbers in the task description ·
the branch rule and that it must not commit · the test boundary (unit inner loop, no e2e, no
adversarial suite — those are the verifier's; and it runs this task's scoped selection, never the
whole suite).

**If the agent dies before it reports** — an API error, a session limit, an interrupt — that is not a
failed task and not a `needs_human`. Check `git status`: an empty tree means nothing was lost, so
spawn a fresh implementer with the same brief. A non-empty tree means work landed with no account of
itself, so read its `## Log` (opened at its Stage 0) and either resume the same agent, or go to
Stage 3 telling the verifier plainly that the build is unattested and it must judge completeness too.
Never assume an interrupted build is finished, and never assume it is worthless.

### Stage 3: Verify (once)
Spawn the **`verifier` agent** (`subagent_type: verifier`, separate agent — it preloads
`verify-feature`). It authors adversarial tests for the acceptance criteria, drives the real stack,
and proves observable outcomes. It runs **once**: its findings must be actionable on their own.

### Stage 4: Fix (one round)
**Pass** → Stage 5. **Fail** → hand the findings to the **same** implementer agent for **exactly one**
fix round, then run the **static gate plus this task's scoped test selection** — which now includes the
verifier's committed tests, so the fix is checked without re-spawning the verifier and without paying
for the whole suite (**`../_shared/build-pipeline/quality-gate.md`**).
- Green → Stage 5.
- Still red, or a finding the implementer says it cannot close → set `status: needs_human`, append a
  `## Log` entry naming what still fails and what was tried, **write the `timings` you have**, release
  the lease, and **stop**. Report it plainly. **Never a second fix round.**

### Stage 5: Solve pass + gate
Direct the **same implementer agent** to a light cleanup **scoped to this task's own diff** — remove
dead or duplicated code it introduced, collapse needless abstraction, drop over-built generality —
strictly **behaviour-preserving** — and a flag, parameter or command named in
`.dev-skills/project-setup/verification.md` **is** behaviour: from inside the diff it looks like an
argument nobody varies, but it is part of the contract the verifier drives the product by.
Pre-existing rot in code this task didn't touch is out of scope: note it as a `rework` task, never
tidy it here. (Agents over-produce and don't feel maintenance cost;
a deliberate pass stops bloat from compounding.)

Then confirm the **static gate** (`make check-fast`) and this task's **scoped test run** are green —
the selection now includes the verifier's tests and the tests of every module this task touched, so
the tidy stays honest. **Do not run the whole suite here**: the build loop never does, and the
release pipeline runs it over everything (**`../_shared/build-pipeline/quality-gate.md`**). Red is
never committed and never triggers another round — it goes to `needs_human`.

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
Set `status: done` (history entry), take the final clock reading, and write the `timings` block — both
land **before** the commit, so the task file the commit captures is complete. Then make a **checkpoint
commit** via the `commit` skill — the message carries this task's id (e.g. `[T012]`) and what was done;
`commit` splits a substantial cleanup into its own `refactor:` commit. Release the env lease.
Regenerate `.dev-skills/build-plan/board.md` from the task files. Report in three lines — what was
built, how it was proven, what state the task is in — plus one line of timings:

> **Time:** build 6m52s · verify 3m07s · fix 1m36s · solve 1m14s · total 15m03s

Give it as it is, without commentary: it is wall-clock including every moment you waited on a human,
so it explains where the task's time went and nothing more.

## Rules

1. **Conduct, don't duplicate.** Never write or verify the feature yourself — spawn the `implementer`
   and `verifier` agents; invoke `setup-dev-environment` and `commit`.
2. **Verify in a separate, fresh agent** — never let the implementer approve its own work.
3. **One build, one verification, one fix.** No second fix round, no counter: whatever remains open
   goes to `needs_human`, in both modes. Never re-spawn the verifier to "check the fix" — its
   committed tests do that through the gate.
4. **Never commit red.** A red gate is `needs_human`, not another attempt. The gate here is the
   **static gate + this task's scoped test selection** — the whole suite is never run in the build
   loop; the release pipeline runs it (**`../_shared/build-pipeline/quality-gate.md`**).
5. **Accept before you commit.** Show what was built and how to check it; skip the question only when
   the diff genuinely holds nothing hand-checkable (`review: auto`, with the reason). Never mark
   `auto` to avoid an awkward answer.
6. **Let the spec catch up in the same commit.** A stale spec is what makes the *next* plan wrong.
7. **One task, one working tree, current branch.** No worktrees, no parallel tasks, no new branch
   unless the user asked for one.
8. **Hold the env lease for the task's span** and release it when the task leaves — committed or
   escalated. See **`../_shared/build-pipeline/env-access.md`**.
9. **Record the timings on the way out — escalated tasks included.** A task that went `needs_human` is
   exactly the one whose time is worth knowing; dropping it leaves a record where only the smooth
   tasks were measured. Never estimate a stage you forgot to clock — omit the key instead.
