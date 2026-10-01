---
name: run-task
description: "Drive one backlog task (or a free-form request filed as origin: adhoc) through the full cycle: implement, one independent verification by a separate agent, one fix round, static gate + the task's scoped tests, acceptance, checkpoint commit. A small bounded change may take the quick lane; anything left open escalates to needs_human. Use for a single task; build-tasks runs the whole plan."
argument-hint: "[<task-id> | <free-form request>]"
---

# Run Task Skill (one task, end to end)

You drive **one** task from `todo` to a committed `done` — or honestly to `needs_human`. You never
write or verify the feature yourself: you spawn the build-loop agents, invoke `commit`, and own the
decisions between steps. Sequential, single working tree, current branch.

Two agents: the **`implementer`** (preloads `implement-feature`) is spawned fresh for this task and
kept through the fix round; the **`verifier`** (preloads `verify-feature`) is a separate agent with no
implementer bias. Lifecycle: **`../_shared/build-pipeline/build-config.md`**; why one fix round and no
counter: **`../_shared/build-pipeline/verification-method.md`**.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes

Read `mode` from `.dev-skills/build-plan/.build-config.md`; if absent, ask once (default interactive)
and write it (**`../_shared/build-pipeline/build-config.md`**). Backlog schema, `ready` and the board:
**`../_shared/build-pipeline/backlog-format.md`**.

- **interactive** — confirm before starting; ask the human to accept the finished work (unless nothing
  is hand-checkable); stop on `needs_human`.
- **autopilot** — acceptance recorded as `review: auto` with the reason; the spec catch-up edit applied
  and logged, not offered. `needs_human` still stops.

When `build-tasks` passes *"acceptance deferred, manual review at TXX"*, skip only the acceptance
question (record the digest and `review: auto` with that note); everything else is unchanged.

## The quick lane

A small change keeps its task record but drops the separate verifier — nothing else. Bounds, what it
drops and the one-way escalation: **`references/lanes-and-timing.md`** → "The quick lane". State the
bounds when you use it; **uncertain counts as ineligible**.

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

**Timing:** you hold the clock — a subagent's duration never comes back in its result. Bracket each
dispatched stage with `date -u '+%Y-%m-%dT%H:%M:%SZ %s'` and write the `timings` block in one edit
when the task leaves you (**`references/lanes-and-timing.md`** → "Timing the stages").

### Stage 0: Intake
- **Task id** (`T012`) → read the task file.
- **Free-form request** → file it first: `origin: adhoc`, one-line `summary`, full `## Description`,
  `traces_to` empty, and **acceptance criteria you propose and the user confirms**. One coarse task by
  default, the parts as `acceptance` entries, sized as `plan-development` does
  (**`../_shared/build-pipeline/planning-method.md`**); the backlog holds **at most 15 open tasks**.
- **Ready?** `status: todo` (or a stale `in_progress` from a killed run) and every `blocked_by` `done`;
  otherwise stop and name the blocker.
- **Unclaimed?** A `claim.heartbeat` fresher than 30 minutes belongs to another session — stop, name
  the holder and stage, offer the next ready task. Older → say you are reclaiming it and continue
  (**`backlog-format.md`** → `claim`).

### Stage 1: Start
Set `status: in_progress` (with a `history` entry) and write the `claim` block — holder id,
`stage: build`, `since`, `heartbeat` — **before you spawn anything**; regenerate `board.md` so its
**Now** line shows the task. Re-stamp `claim.stage` + `heartbeat` and regenerate the board at every
stage boundary (2→3→4→5→6). Show the human the acceptance criteria, one line each. Acquire the **env
lease** (**`../_shared/build-pipeline/env-access.md`**); subagents inherit it.

### Stage 2: Build
Dispatch by `type`: **`setup`** → invoke `setup-dev-environment` scoped to this task, then Stage 5 ·
**`feature`** / **`rework`** → spawn the **`implementer`** agent (`subagent_type: implementer`, fresh
context); it builds, self-checks the happy path and gets the cheap gate green · **`verify`**
(cross-cutting) → Stage 3 directly. Spawn prompt contents and how to resume a killed agent from the
task's `## Log`: **`references/lanes-and-timing.md`** → "Spawning and recovering an implementer".

### Stage 3: Verify (once)
Spawn the **`verifier`** agent (`subagent_type: verifier`). It authors adversarial tests for the
acceptance criteria, drives the real stack and proves observable outcomes. One pass; its findings must
be actionable on their own.

### Stage 4: Fix (one round)
Pass → Stage 5. Fail → the **same** implementer gets **exactly one** fix round, then run the **static
gate + this task's scoped tests** (now including the verifier's committed tests — no re-spawn, no whole
suite; **`../_shared/build-pipeline/quality-gate.md`**). Green → Stage 5. Still red, or a finding the
implementer cannot close → `status: needs_human`, a `## Log` entry (what fails, what was tried), the
`timings` you have, release the lease, **stop** and report plainly.

### Stage 5: Solve pass + gate
The same implementer tidies **this task's own diff**, behaviour-preserving — a flag, parameter or
command named in `verification.md` **is** behaviour; rot elsewhere becomes a `rework` note. Confirm the
static gate + scoped run are green; red goes to `needs_human`, never another round. Detail:
**`references/lanes-and-timing.md`** → "The solve pass".

### Stage 6: Accept · Stage 7: Spec catch-up
Look at the actual diff. Nothing hand-checkable (tests, internal logic, config, criteria the verifier
proved) → `review: auto` with a one-line reason. Otherwise show a short digest (what it does now · how
to see it · what the verifier proved) and, in interactive, wait. Observable behaviour the spec doesn't
describe → `spec_sync: pending` and **propose the concrete edit**, written out, landing in the **same
commit**. Digest format, declined acceptance: **`references/lanes-and-timing.md`** → "Accepting the
work and catching the spec up".

### Stage 8: Commit + hand back
Set `status: done` (history entry) and write `timings` — both before the commit. Checkpoint commit via
the `commit` skill, the message carrying the task id (`[T012]`); `commit` splits a substantial cleanup
into its own `refactor:` commit. Release the lease; regenerate `.dev-skills/build-plan/board.md`.
Report in three lines — built · proven · state — plus timings that add up (stages + waiting = total):

> **Time:** build 6m52s · verify 3m07s · fix 1m36s · solve 1m14s · waiting on you 2m14s · total 15m03s

Close with the **«What you should do»** block (**`../_shared/build-pipeline/report-format.md`**).

## Rules

1. **Conduct, don't duplicate** — agents build and verify, `setup-dev-environment` and `commit` do
   their jobs; you never do theirs.
2. **Verify in a separate, fresh agent**; the implementer never approves its own work.
3. **One build, one verification, one fix.** Whatever stays open goes to `needs_human`, in both modes;
   never re-spawn the verifier to check the fix — its committed tests do that through the gate.
4. **Never commit red.** The gate is the static gate + this task's scoped tests; the whole suite runs
   in the release pipeline (**`quality-gate.md`**).
5. **Accept before you commit.** `review: auto` only when the diff holds nothing hand-checkable, with
   the reason — never to dodge a question.
6. **The spec catches up in the same commit.**
7. **One task, one working tree, current branch.**
8. **The quick lane is bounded, asserted and one-way**; it drops only the separate verifier.
9. **Claim before you spawn, re-stamp at every stage**; never take a task another session holds.
10. **Hold the env lease for the task's span**, release it on exit (**`env-access.md`**).
11. **Record timings on the way out, escalated tasks included**; never estimate a stage you forgot to
    clock — omit the key.
