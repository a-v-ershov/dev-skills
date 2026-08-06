---
name: run-task
description: "Drive ONE task through the full development cycle: the implementer builds it, a separate fresh verifier independently proves the acceptance criteria, its findings go back for exactly one fix round, the static gate plus this task's scoped test selection must be green (the whole suite is never run here), the human accepts the work or it is auto-accepted, and a checkpoint commit carrying the task id lands. Two entry points: a task id from the backlog, or a free-form request it files itself with origin: adhoc. A small, obvious change can take the quick lane instead. Anything the single fix round leaves open escalates to needs_human. Sequential, single working tree, current branch."
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

## Language & git

Respond and reason in the user's language. Each sub-skill and agent follows
the same rule. Never translate code, identifiers, commands, or file paths. (Commit messages are
always English — the `commit` skill enforces that.)

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

Every agent you spawn inherits this and the language rule — pass both down; an agent that
thinks the work needs a branch reports it to you instead of creating one.

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

## The quick lane

Not every task deserves the full cycle — a padding fix does not need a separate verifier. The lane
exists **inside** this skill so a small change keeps its record instead of going round the pipeline.
Its four eligibility bounds, what it drops (only the separate verifier), and the one-way escalation
rule are in **`references/lanes-and-timing.md`** → "The quick lane". Read it before using the lane, and
state the bounds out loud when you do. **Uncertain counts as ineligible.**


## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — resolve the input to a task file (id, or file a new adhoc task); confirm it's ready and unclaimed; full cycle or quick lane?
- [ ] Stage 1: Start — status in_progress + claim written BEFORE any spawn; show the acceptance criteria; acquire the env lease; start the clock
- [ ] Stage 2: Build — spawn the implementer agent (or dispatch a setup task to setup-dev-environment)
- [ ] Stage 3: Verify — spawn the verifier agent, ONCE
- [ ] Stage 4: Fix — one round by the same implementer + green gate, else needs_human
- [ ] Stage 5: Solve pass — tidy this task's own diff, behaviour-preserving; static gate + scoped tests green
- [ ] Stage 6: Accept — human digest + approval, or review: auto when nothing is hand-checkable
- [ ] Stage 7: Spec catch-up — behavior changed and undocumented? propose the edit (spec_sync)
- [ ] Stage 8: Commit — status done + timings + checkpoint commit via the commit skill; release the lease; regen board
```

### Timing the stages
**You** time the work — an agent cannot see its own clock and a subagent's duration never comes back
inside its result. Bracket each dispatched stage with `date -u '+%Y-%m-%dT%H:%M:%SZ %s'` and write the
`timings` block in one edit when the task leaves you. Full method:
**`references/lanes-and-timing.md`** → "Timing the stages".


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

**And confirm nobody else holds it.** A task whose `claim.heartbeat` is fresher than 30 minutes belongs
to another session — stop, name the holder and its stage, and offer the next ready task instead.
Older than that, the holder is presumed dead: say you are reclaiming it and why, then continue
(**`../_shared/build-pipeline/backlog-format.md`** → `claim`). Never take a fresh claim silently; the
user runs more than one session on this repository.

### Stage 1: Start
Set `status: in_progress` with a `history` entry **and write the `claim` block** — holder id,
`stage: build`, `since`, `heartbeat` — **before you spawn anything**, then **regenerate `board.md`
now** so the task moves out of `Ready` into `In progress` and the board's **Now** line says what is
happening. The build runs for an hour or more; a board that only catches up at the commit shows
"nothing in progress" for exactly the stretch someone would look at it.

**Re-stamp `claim.stage` + `heartbeat` and regenerate the board at every stage boundary** (2→3→4→5→6).
That is the whole status mechanism: someone can answer "what is it doing, and for how long?" from the
board alone, without interrupting the run.

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

**What the spawn prompt must carry, and what to do when the agent dies before it reports** —
including why a killed build is resumed from the task's `## Log` rather than rebuilt from zero:
**`references/lanes-and-timing.md`** → "Spawning and recovering an implementer". Read it before the
first spawn of a run.


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
Direct the **same implementer** to a light cleanup **scoped to this task's own diff**, strictly
behaviour-preserving — and remember that a flag, parameter or command named in `verification.md` **is**
behaviour. Pre-existing rot elsewhere is a `rework` note, never tidied here. Then confirm the **static
gate + this task's scoped run** are green; the whole suite is never run in the build loop. Red is never
committed and never triggers another round — it goes to `needs_human`. Full detail:
**`references/lanes-and-timing.md`** → "The solve pass".


### Stage 6: Accept · Stage 7: Spec catch-up
Look at the **actual diff**: nothing a person could check by hand (tests, internal logic, config, every
criterion proven by the verifier) → accept it yourself with `review: auto` and a one-line reason.
Something hand-checkable → show a short digest (what it does now in plain language · how to see it
yourself · what the verifier already proved) and, in interactive, wait.

If the work changed observable behaviour the spec doesn't describe, set `spec_sync: pending` and
**propose the concrete edit**, written out rather than described; it lands in the **same commit**.

Both stages in full, including what the digest looks like and what to do when the user declines:
**`references/lanes-and-timing.md`** → "Accepting the work and catching the spec up".


### Stage 8: Commit + hand back
Set `status: done` (history entry), take the final clock reading, and write the `timings` block — both
land **before** the commit, so the task file the commit captures is complete. Then make a **checkpoint
commit** via the `commit` skill — the message carries this task's id (e.g. `[T012]`) and what was done;
`commit` splits a substantial cleanup into its own `refactor:` commit. Release the env lease.
Regenerate `.dev-skills/build-plan/board.md` from the task files. Report in three lines — what was
built, how it was proven, what state the task is in — plus one line of timings:

> **Time:** build 6m52s · verify 3m07s · fix 1m36s · solve 1m14s · waiting on you 2m14s · total 15m03s

Give it as it is, without commentary — and **make it add up**: the stages plus the waiting must
reconcile with the total, because a report whose parts sum to less than its total invites exactly one
question, and it is a fair one. Close with the **«What you should do»** block, even when it is one line
saying there is nothing (**`../_shared/build-pipeline/report-format.md`**).

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
8. **The quick lane is bounded, asserted and one-way.** State the four bounds before you use it and
   escalate to the full cycle the moment one breaks. It drops the separate verifier and nothing else —
   never the task file, never the gate, never human acceptance.
9. **Claim before you spawn, re-stamp at every stage.** The board must be able to answer "what is it
   doing, and since when?" while the work is running, and a task another session holds is never taken.
10. **Hold the env lease for the task's span** and release it when the task leaves — committed or
   escalated. See **`../_shared/build-pipeline/env-access.md`**.
11. **Record the timings on the way out — escalated tasks included.** A task that went `needs_human` is
   exactly the one whose time is worth knowing; dropping it leaves a record where only the smooth
   tasks were measured. Never estimate a stage you forgot to clock — omit the key instead.
