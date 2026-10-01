# Keeping the docs and the plan in agreement (shared — spec + build pipelines)

Spec and backlog describe one product and drift in **two directions**, each handled by the skill
already doing the work — no propagation skill, no "do you want to propagate?" step:

| Drift | Who notices | What happens |
|-------|-------------|--------------|
| **The spec changed** — a phase doc was edited, so later docs and the plan may disagree with it | the phase skill that just edited it | it amends the docs it owns, then says which later documents and the backlog may now be stale and offers the one command that reconciles them (`/plan-development`) |
| **The product changed** — a task shipped behavior the spec doesn't describe | `run-task`, at the end of the task | it sets `spec_sync: pending` and proposes the concrete spec edit, which lands **in the same commit** as the code |

Drift is **recorded**, never enforced against the user's will or allowed to block work — a
`spec_sync: pending` task on the board, a divergence noted in a doc — so the next planning run sees it.

## Direction 1 — the spec changed

The chain of derivation:

```
idea-validation → product-requirements → user-flows → design-decisions → architecture
   → dev-architecture → [ backlog (.dev-skills/build-plan) ]
```

A change at stage N may need reconciling at N+1, N+2, … and finally the backlog — only **forward**
(editing upstream would be a new upstream change).

**Every stage skill supports an amend mode** — re-run on an existing document, it reconciles instead of
regenerating:

1. **Read** the changed upstream document and its own current one.
2. **Assess impact.** Still consistent → **self-skip**: report "no change needed", touch nothing.
3. **If affected, amend surgically** — in place, only what the change touches. **Preserve the
   `## Forks / Decisions log`**; never regenerate. Update `*.summary.md` if the essence changed.
4. **Record it** in the `## Forks / Decisions log`: what changed upstream, what changed here,
   confidence.
5. **Ask only on a critical question** (decision-changing, low-confidence, destructive); otherwise
   proceed and log.

Research is scoped to the amended part, never a full re-run.

**Then hand off, don't chase.** In one line, name the next document in the chain and offer its skill —
and, **if `.dev-skills/build-plan/tasks/` exists**, say the plan may be stale and `/plan-development`
reconciles it. The user decides how far to walk; `build-tasks` checks the spec-vs-plan anchor before a
run.

## Direction 2 — the product changed

`run-task` owns this end (its Stage 7). A task that shipped observable behavior the spec doesn't
describe — a new screen, a changed rule, an `adhoc` task with no `traces_to` — sets `spec_sync:
pending` and proposes the **written-out** edit: the feature line for `product-requirements.research.md`,
the step or screen for `user-flows.research.md`. Applied → it lands in the task's own commit and flips
to `spec_sync: done` (a deferred spec edit never happens). Declined → it stays `pending`, on the board
and in the run's final report.

## Backlog reconciliation (`plan-development` amend mode)

Against an existing backlog, `plan-development` emits **task deltas**, not a new plan — add / modify /
cancel / reopen-as-rework (`planning-method.md`), using `traces_to` to find the tasks a changed section
affects and clearing `spec_sync: pending` on tasks the spec now describes. Routine deltas proceed and
are logged; **cancel and reopen-as-rework always confirm with the human** (below).

**Never write code here.** Reconciliation updates documents and the backlog; the rebuild is a normal
`run-task` / `build-tasks` run afterwards.

## What always stops (regardless of mode)

- Any **destructive backlog delta** — cancelling a task, or reopening a `done` task as rework.
- Any **decision-changing or low-confidence** reconciliation a skill can't make safely.
