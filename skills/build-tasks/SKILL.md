---
name: build-tasks
description: "Work through the development plan: take tasks from .dev-skills/build-plan/ one at a time and run each through the run-task skill (implementer → separate verifier → one fix round → green gate → human acceptance → checkpoint commit). The order is deterministic and not a judgement call: the next task is the ready one (status todo, all blocked_by done) with the lowest id; no parallel tasks, one working tree. Before starting it checks whether the spec moved ahead of the plan and, if so, offers to reconcile via plan-development first rather than confidently building something already abandoned. A task that escalates to needs_human is not retried — the run continues and reports it at the end. By default it runs straight through, pausing only for a real reason (a task whose work a human can check by hand, needs_human, a red gate, the per-run limit); a one-at-a-time mode with confirmation before each task is opt-in, as is thinning acceptance to every Nth task. It takes at most 8 tasks per run, then stops and asks the human to compact the context and start it again — beyond that the session is full of diffs and reports and tasks start blurring together. Resumable: the backlog is the source of truth, so an interrupted run continues where it stopped and never rebuilds finished work. Use after plan-development. It writes no code and duplicates no cycle — all per-task work is run-task's."
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

## Language

Respond and reason in whatever language the user addressed you in. Never translate code, identifiers,
commands, or file paths.

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
- An argument that is a task id → start from that task (its blockers must still be `done`).

### The loop
Repeat while ready tasks remain:

1. **Compute the ready set** — `todo` tasks whose `blocked_by` are all `done`. Empty → go to Done.
2. **Take one** — the **lowest `id`** among them, so two runs produce the same order. Announce it in
   one line and continue without asking; wait for confirmation only in one-at-a-time mode.
3. **Run it through `/run-task`** (via the Skill tool) — the whole cycle, no steps skipped and no
   logic of your own; a green gate is mandatory in autopilot too. In *acceptance every N* mode, tell
   it whether this task's acceptance is deferred and where the manual one lands.
4. **A task that went `needs_human`** → don't take it again; show it to the human and move to the next
   ready task. One stuck task must not stop the whole plan.
5. **Regenerate `.dev-skills/build-plan/board.md`** from the task files.
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
run into build / verify / fix / solve. Report the numbers flat, with no verdict attached — they are
wall-clock, so they include every stretch the run spent waiting on you
(**`../_shared/build-pipeline/backlog-format.md`**).

**Stopped at the limit with ready tasks left** — ask the human to compact and re-run:

> Ran 8 tasks; <N> ready tasks remain. Continuing in this session isn't wise — the context is full of
> diffs and reports, and tasks start blurring together. Run `/compact` (or `/clear` for a fully fresh
> start) and call `/build-tasks` again: the plan, statuses, and logs live in `.dev-skills/build-plan/`,
> so the run picks up at the next task and nothing is lost.

You cannot compact the context yourself — the human runs that command. Your job here is to stop in
time and say so.

If no ready tasks remain but unfinished ones do, explain why (they wait on `needs_human` tasks). If
everything is `done`, say so plainly and point at the release phase (`/release-product`).

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
