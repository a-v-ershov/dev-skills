---
name: build-tasks
description: "Work through the development plan: take tasks from .dev-skills/build-plan/ one at a time and run each through run-task. The order is deterministic, not a judgement call — the ready task (status todo, all blocked_by done) with the lowest id; no parallel tasks, one working tree. It refuses to start when the spec has moved ahead of the plan and offers plan-development first, skips tasks another session has claimed, and never retries a needs_human task. By default it runs straight through, pausing only for a real reason; one-at-a-time and thinned acceptance are opt-in. Resumable — the backlog is the source of truth. Use after plan-development. It writes no code and duplicates no cycle."
argument-hint: "[one-at-a-time | run N | review every N | <task-id> to start from]"
---

# Build Tasks Skill (work through the plan)

You work through the backlog: pick the next task, hand it to **`run-task`**, record the outcome,
continue. You choose *which* task, never *how* it is built — the cycle lives in `run-task` and is not
repeated here. Work is **sequential** on a single working tree on the current branch. The backlog is
the source of truth, so a killed run resumes without losing anything.

```
check the plan isn't stale → compute ready set → lowest id → /run-task → regen board → next (max 8)
```

## Language & git

Respond and reason in the user's language. Never translate code, identifiers,
commands, or file paths.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

Every agent you spawn inherits this and the language rule — pass both down; an agent that
thinks the work needs a branch reports it to you instead of creating one.

## Modes

Read `.dev-skills/build-plan/.build-config.md` for `mode` (write it if absent, default
**interactive**). Full rules: **`../_shared/build-pipeline/build-config.md`**. Backlog schema,
`ready`, and the board: **`../_shared/build-pipeline/backlog-format.md`**.

- **Straight through (default).** Between tasks you do not stop and do not ask permission. The only
  real reasons to pause: a task where the human has something to check by hand (`run-task` handles
  that), a `needs_human` escalation, a red gate, or the per-run limit.
- **One at a time** (opt-in, argument `one-at-a-time`) — confirm before each task.
- **Acceptance every N** (opt-in, argument `review every N`; suggest N=5) — **only the human turns
  this on**, never you. Manual acceptance then happens on every Nth task and always on the run's last
  task; the rest are passed to `run-task` with "acceptance deferred, manual review at TXX". Nothing
  else softens: the verifier, the fix round, the green gate, and the `needs_human` stop are unchanged.
  At the next manual acceptance, show the batch — one line per auto-accepted task since the last one
  (what was built + what proved it) — so the human can spot and undo something wrong. The mode lasts
  for this run only.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Step 0: Intake — backlog present? spec moved ahead of the plan? mode? interrupted run?
- [ ] Loop: ready set → lowest id → /run-task → regen board → acceptance if due → next (stop at 8 tasks)
- [ ] Done: report built / needs_human / blocked / spec_sync pending; at the limit, ask for /compact
```

### Step 0: Intake
- **No `.dev-skills/build-plan/tasks/`** → stop: there is nothing to run. Offer `/plan-development`
  first. A single task from a sentence, with no plan at all, is `/run-task "<request>"`.
- **Has the spec moved ahead of the plan?** Read the *Reconciled with spec* anchor in the header of
  `.dev-skills/build-plan/board.md` and check whether the spec changed since:
  `git log <anchor-commit>..HEAD -- .dev-skills/project-spec/`. If it did, **stop** and offer
  `/plan-development` to reconcile first — otherwise the run will confidently build what the user has
  already dropped. If the human says "go anyway", agree, but name which spec files diverged.
- **Interrupted run.** A task left `in_progress` is not restarted blindly: show its `## Log` and offer
  to continue it through `run-task` (which re-verifies before committing). Finished tasks are never
  rebuilt.
- **Also reclaim a stale env lock** left by a killed run
  (**`../_shared/build-pipeline/env-access.md`**).
- **Is another session working here?** List the tasks whose `claim.heartbeat` is fresher than 30
  minutes and say so in one line — those are skipped, not waited for. The user does run two sessions on
  one repository, and a run that quietly re-does another's task is worse than one that stops
  (**`../_shared/build-pipeline/backlog-format.md`** → `claim`). If a "study only, don't write" mode is
  asked for, read the tasks and plan them, and change no file until the other session's claim clears.
- **Does the scoped test target exist?** Confirm the `make test-scoped` equivalent named in
  `verification.md` is there and really selects. Missing or fake → say it once, now: every hand-off
  will otherwise pay for the whole suite, and `/setup-dev-environment` is the fix. Then proceed — the
  run is not blocked on it (**`../_shared/build-pipeline/quality-gate.md`**).
- An argument that is a task id → start from that task (its blockers must still be `done`).

### The loop
Repeat while ready tasks remain:

1. **Compute the ready set** — `todo` tasks whose `blocked_by` are all `done`. Empty → go to Done.
   If the **open** count (todo + in_progress + needs_human) is over **15**, say so once and offer
   `/plan-development consolidate` before continuing — the ceiling is the backlog's, not just the
   planner's, and it is what keeps tasks coarse (**`../_shared/build-pipeline/planning-method.md`**).
   The human decides; the run is not blocked on it.
2. **Take one** — the **lowest `id`** among them, so two runs produce the same order. Announce it in
   one line and continue without asking; wait for confirmation only in one-at-a-time mode.
3. **Run it through `/run-task`** (via the Skill tool) — the whole cycle, no steps skipped and no
   logic of your own; a green gate is mandatory in autopilot too — the **static gate plus that task's
   scoped test selection**, never the whole suite
   (**`../_shared/build-pipeline/quality-gate.md`**). In *acceptance every N* mode, tell
   it whether this task's acceptance is deferred and where the manual one lands.
4. **A task that went `needs_human`** → don't take it again; show it to the human and move to the next
   ready task. One stuck task must not stop the whole plan.
5. **Regenerate `.dev-skills/build-plan/board.md`** from the task files — the progress header
   (done/total, %, and the **Now** line) included. `run-task` already refreshes it at each stage
   boundary; here you refresh the totals.
6. **Acceptance, when the human asked for it.** In *acceptance every N* mode, if this was the **Nth**
   task of the run — or the run's **last** one — do the manual acceptance now, before taking anything
   else: show the batch (one line per auto-accepted task since the previous acceptance: what was built
   + what proved it) and **wait**. Skipping this silently turns the mode the human switched on into a
   promise nobody kept.
7. **Next task — unless you hit the limit.** Count the tasks handled this run (including escalated
   ones): at **8**, stop even if ready tasks remain, and go to Done. An argument `run N` lowers the
   limit to N.

### Done: report
Report as a table: how many tasks finished this run · which went `needs_human` (the human's action
list, one line each on where it got stuck) · which remain blocked and by what · and which tasks sit at
**`spec_sync: pending`** — done, but not yet reflected in the spec. Point at
`.dev-skills/build-plan/board.md` for the detail.

Give each task a **time** column from its `timings.total`, and one line under the table splitting the
run into build / verify / fix / solve **plus the time spent waiting on you**, so the parts reconcile
with the total. Report the numbers flat, with no verdict attached
(**`../_shared/build-pipeline/backlog-format.md`**). End the report with the **«What you should do»**
block — imperative, one line per item, no pipeline jargon
(**`../_shared/build-pipeline/report-format.md`**).

**Stopped at the limit with ready tasks left** — ask the human to compact and re-run:

> Ran 8 tasks; <N> ready tasks remain. Continuing in this session isn't wise — the context is full of
> diffs and reports, and tasks start blurring together. Run `/compact` (or `/clear` for a fully fresh
> start) and call `/build-tasks` again: the plan, statuses, and logs live in `.dev-skills/build-plan/`,
> so the run picks up at the next task and nothing is lost.

You cannot compact the context yourself — the human runs that command. Your job here is to stop in
time and say so.

If no ready tasks remain but unfinished ones do, explain why (they wait on `needs_human` tasks). If
everything is `done`, say so plainly and point at the release phase (`/release-product`) — and add one
line saying that **the whole test suite has not been run yet**: the build loop only ever ran each
task's own selection, and the full run happens in the release pipeline
(**`../_shared/build-pipeline/quality-gate.md`**). Say it as a fact about where the suite gets run, not
as a warning to act on now.

## Rules

1. **Don't duplicate the cycle.** All per-task work is `/run-task`'s. You choose the next task and
   keep the books.
2. **One task at a time, one working tree.** No parallel tasks, no worktrees, no new branch.
3. **The plan sets the order** — ready tasks, lowest id. Never reshuffle "by importance".
4. **A task with unmet blockers is never taken.**
5. **`needs_human` is never retried automatically** and is always surfaced, in both modes.
6. **Don't stop between tasks and don't ask permission**; only the human slows it down, by choosing
   one-at-a-time.
7. **Acceptance every N is the human's switch**, never yours. Every Nth task and the run's last task
   are always manual, with the batch of auto-accepted ones shown. A failure, a red gate, or
   `needs_human` stops the run in any mode.
8. **At most 8 tasks per run.** At the limit, stop and ask for `/compact` — you don't compact anything
   yourself.
9. **A spec that moved past the plan means `/plan-development` first.** Running a plan that disagrees
   with the spec is confidently building the wrong thing.
10. **Finished work is never rebuilt**; an interrupted run continues rather than restarts.
11. **The board is regenerated** from the task files after every task, never hand-edited.
