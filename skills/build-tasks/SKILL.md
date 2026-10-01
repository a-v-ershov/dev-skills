---
name: build-tasks
description: "Work through the development plan: run tasks from .dev-skills/build-plan/ through run-task one at a time, lowest-id ready task first, at most 8 per run. Refuses to start when the spec moved ahead of the plan, skips tasks another session claimed, never retries needs_human. Resumable; writes no code. Use after plan-development."
argument-hint: "[one-at-a-time | run N | review every N | <task-id> to start from]"
---

# Build Tasks Skill (work through the plan)

You work through the backlog: pick the next task, hand it to **`run-task`**, record the outcome,
continue. You choose *which* task, never *how* it is built. The backlog is the source of truth, so a
killed run resumes without losing anything.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes

Read `mode` from `.dev-skills/build-plan/.build-config.md` (write it if absent, default
**interactive**; **`../_shared/build-pipeline/build-config.md`**). Backlog schema, `ready` and the
board: **`../_shared/build-pipeline/backlog-format.md`**.

- **Straight through (default)** — never stop or ask permission between tasks. The only pauses: a
  hand-check (`run-task` handles it), `needs_human`, a red gate, the per-run limit.
- **One at a time** (opt-in, argument `one-at-a-time`) — confirm before each task.
- **Acceptance every N** (opt-in, argument `review every N`; suggest N=5; this run only) — **only the
  human turns it on.** Manual acceptance on every Nth task and always on the run's last (loop step 6);
  the rest go to `run-task` with "acceptance deferred, manual review at TXX". The verifier, the fix
  round, the green gate and the `needs_human` stop are unchanged.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Step 0: Intake — backlog present? spec moved ahead of the plan? mode? interrupted run?
- [ ] Loop: ready set → lowest id → /run-task → regen board → acceptance if due → next (stop at 8 tasks)
- [ ] Done: report built / needs_human / blocked / spec_sync pending; at the limit, ask for /compact
```

### Step 0: Intake
- **No `.dev-skills/build-plan/tasks/`** → stop; offer `/plan-development`. A single task from a
  sentence, with no plan, is `/run-task "<request>"`.
- **Spec moved ahead of the plan?** Take the *Reconciled with spec* anchor from the header of
  `.dev-skills/build-plan/board.md`; run `git log <anchor-commit>..HEAD -- .dev-skills/project-spec/`.
  Changed → **stop** and offer `/plan-development` first; on "go anyway", name the diverged spec files.
- **Interrupted run** — a task left `in_progress`: show its `## Log`, offer to continue it through
  `run-task` (it re-verifies before committing). Reclaim a stale env lock left by a killed run
  (**`../_shared/build-pipeline/env-access.md`**).
- **Another session here?** Name, in one line, the tasks whose `claim.heartbeat` is fresher than 30
  minutes — skipped, not waited for (**`backlog-format.md`** → `claim`). In a "study only, don't write"
  mode, read and plan but change no file until the claim clears.
- **Scoped test target?** Confirm the `make test-scoped` equivalent named in `verification.md` exists
  and really selects. Missing or fake → say it once (every hand-off otherwise pays for the whole suite;
  `/setup-dev-environment` is the fix) and proceed (**`../_shared/build-pipeline/quality-gate.md`**).
- A task-id argument → start from that task (its blockers must still be `done`).

### The loop
Repeat while ready tasks remain:

1. **Ready set** — `todo` tasks whose `blocked_by` are all `done`. Empty → Done. **Open** count (todo +
   in_progress + needs_human) over **15** → say so once and offer `/plan-development consolidate`
   (**`../_shared/build-pipeline/planning-method.md`**); the human decides, the run goes on.
2. **Take the lowest `id`**; announce it in one line and continue (confirm first only in one-at-a-time).
3. **Run it through `/run-task`** (Skill tool) — the whole cycle, no logic of your own; the green gate
   (static + that task's scoped tests, never the whole suite) is mandatory in autopilot too. In
   *acceptance every N*, tell it whether this task's acceptance is deferred and where the manual one
   lands.
4. **`needs_human`** → show it to the human and move to the next ready task.
5. **Regenerate `.dev-skills/build-plan/board.md`** — progress header included (done/total, %, the
   **Now** line); `run-task` refreshes it per stage, you refresh the totals.
6. **Acceptance, when due** — in *acceptance every N*, on the run's **Nth** or **last** task, before
   taking anything else: show the batch (one line per auto-accepted task since the last acceptance:
   what was built + what proved it, so the human can undo something wrong) and **wait**.
7. **Next — unless at the limit.** Count tasks handled this run (escalated included): at **8**, stop
   even with ready tasks left and go to Done. `run N` lowers the limit to N.

### Done: report
A table: tasks finished this run · which went `needs_human` (one line each on where it got stuck) ·
which remain blocked and by what · which sit at **`spec_sync: pending`** (done, not yet in the spec);
point at `board.md` for detail. A **time** column per task from its `timings.total`, and one line under
the table splitting the run into build / verify / fix / solve **plus waiting on you**, reconciling with
the total — numbers flat, no verdict. End with the **«What you should do»** block
(**`../_shared/build-pipeline/report-format.md`**).

**Stopped at the limit with ready tasks left** — ask the human to compact and re-run:

> Ran 8 tasks; <N> ready tasks remain. Continuing in this session isn't wise — the context is full of
> diffs and reports, and tasks start blurring together. Run `/compact` (or `/clear` for a fully fresh
> start) and call `/build-tasks` again: the plan, statuses, and logs live in `.dev-skills/build-plan/`,
> so the run picks up at the next task and nothing is lost.

No ready tasks but unfinished ones → explain (they wait on `needs_human`). Everything `done` → say so,
point at `/release-product`, and add one line, as a fact rather than a warning: **the whole test suite
has not been run yet** — the loop ran each task's own selection; the full run is the release pipeline's.

## Rules

1. **Don't duplicate the cycle** — per-task work is `/run-task`'s; you pick the task and keep the books.
2. **One task at a time, one working tree** — no parallel tasks, no worktrees, no new branch.
3. **The plan sets the order** — ready tasks, lowest id; never reshuffle "by importance".
4. **A task with unmet blockers is never taken.**
5. **`needs_human` is never retried automatically** and is always surfaced, in both modes.
6. **Only the human slows the run** — by choosing one-at-a-time.
7. **Acceptance every N is the human's switch**, never yours. A failure, a red gate or `needs_human`
   stops the run in any mode.
8. **At most 8 tasks per run**; at the limit, stop and ask for `/compact` — you cannot compact yourself.
9. **A spec that moved past the plan means `/plan-development` first.**
10. **Finished work is never rebuilt**; an interrupted run continues rather than restarts.
11. **The board is regenerated** from the task files after every task, never hand-edited.
