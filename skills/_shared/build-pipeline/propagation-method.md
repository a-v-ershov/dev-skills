# Keeping the docs and the plan in agreement (shared — spec + build pipelines)

The spec and the backlog describe the same product. They drift in **two directions**, and each
direction is handled by the skill already doing the work — there is no separate propagation skill and
no "do you want to propagate?" step:

| Drift | Who notices | What happens |
|-------|-------------|--------------|
| **The spec changed** — a phase doc was edited, so later docs and the plan may disagree with it | the phase skill that just edited it | it amends the docs it owns, then says which later documents and the backlog may now be stale and offers the one command that reconciles them (`/plan-development`) |
| **The product changed** — a task shipped behavior the spec doesn't describe | `run-task`, at the end of the task | it sets `spec_sync: pending` and proposes the concrete spec edit, which lands **in the same commit** as the code |

Neither direction is enforced against the user's will. Drift is **recorded** — a `spec_sync: pending`
task on the board, a divergence noted in a doc — so the next planning run sees it. Blocking work on
paperwork is how the paperwork gets abandoned.

## Direction 1 — the spec changed

The chain of derivation is:

```
idea-validation → product-requirements → user-flows → design-decisions → architecture
   → dev-architecture → [ backlog (.dev-skills/build-plan) ]
```

Each arrow means "derived from". A change at stage N may need reconciling at N+1, N+2, … and finally
in the backlog. Reconciliation only ever moves **forward** — a change never edits upstream (that would
be a new upstream change of its own).

**Every stage skill supports an amend mode** — re-run it on a document that already exists and it
reconciles rather than regenerates:

1. **Read** the changed upstream document and its own current one.
2. **Assess impact.** Still consistent? Then **self-skip** — report "no change needed" and touch
   nothing. This is the guard against over-propagating: most changes don't ripple far.
3. **If affected, amend surgically.** Update only the parts the change touches, in place. **Preserve
   the `## Forks / Decisions log`** — never regenerate from scratch. Update the `*.summary.md` too if
   the essence changed.
4. **Record it** — a `## Forks / Decisions log` entry: what changed upstream, what this doc changed in
   response, confidence.
5. **Ask only on a critical question** — a decision-changing fork, a low-confidence call, anything
   destructive. Otherwise proceed and log.

Research is scoped to the amended part, never a full re-run.

**Then hand off, don't chase.** After amending, the phase says in one line which document is next in
the chain and offers to run its skill — and, **if `.dev-skills/build-plan/tasks/` exists**, that the plan
may now be stale and `/plan-development` will reconcile it. The user decides how far to walk. This is
also why `build-tasks` checks the spec-vs-plan anchor before a run: a plan that disagrees with the
spec builds the wrong thing confidently.

## Direction 2 — the product changed

`run-task` owns this end (its Stage 7). A task that shipped observable behavior the spec doesn't
describe — a new screen, a changed rule, an `adhoc` task with no `traces_to` — sets `spec_sync:
pending` and proposes the **written-out** edit: the feature line for `product-requirements.research.md`,
the step or screen for `user-flows.research.md`. Applied, it lands in the task's own commit and flips
to `spec_sync: done`; declined, it stays `pending` and shows up on the board and in the run's final
report.

Why in the same commit: a spec edit that waits for a "documentation pass" never happens, and the next
`plan-development` run then plans from a picture the product outgrew.

## Backlog reconciliation (`plan-development` amend mode)

When `plan-development` runs against an existing backlog it emits **task deltas** rather than a new
plan — add / modify / cancel / reopen-as-rework (see `planning-method.md`), using `traces_to` to find
which tasks a changed spec section affects, and clearing `spec_sync: pending` on tasks whose behavior
the spec now describes.

**Cancel and reopen-as-rework are destructive — always confirm with the human**, in both modes.
Everything else routine proceeds and is logged.

**Never write code here.** Reconciliation updates documents and the backlog; rebuilding the affected
features is a normal `run-task` / `build-tasks` run afterwards.

## What always stops (regardless of mode)

- Any **destructive backlog delta** — cancelling a task, or reopening a `done` task as rework.
- Any **decision-changing or low-confidence** reconciliation a skill can't make safely.
