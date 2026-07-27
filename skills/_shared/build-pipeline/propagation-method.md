# Change propagation method (shared — spec + build pipelines)

When a stage document is edited, the documents downstream of it may no longer agree with it. This
method reconciles them **forward**, automatically, surgically — and finally updates the backlog. It
spans both pipelines, so it lives in the build-pipeline shared dir but is referenced by the spec-phase
skills too (their `## Amend mode` sections) and driven by the `propagate-changes` conductor.

## The chain

```
idea-validation → product-requirements → user-flows → design-decisions → architecture
   → dev-architecture → [ backlog (.dev-skills/build-plan) ]
```

Each arrow is a dependency: the downstream document is derived from the upstream one. A change at
stage N may require reconciling N+1, N+2, … through to the backlog. Propagation only ever moves
**forward** (a change never reaches back up the chain — that would be a new upstream edit, its own
propagation).

## Detection: none — it is explicit and automatic

There is **no git/manifest/checksum staleness check**. The change is known because someone just made
it (a human edited a doc, or an upstream amend produced it). `propagate-changes` simply **reads the
current files directly** and reasons about what downstream needs adjusting. It runs forward
automatically — there is no "do you want to propagate?" gate. It pauses only for **critical or
destructive** questions (below).

## The per-skill amend contract

Every stage skill (the six spec phases and `plan-development`) supports an **amend mode**: invoked
with the upstream change, it reconciles **its own** document. The contract:

1. **Read** the changed upstream document and its own current document, directly.
2. **Assess impact.** Is its document still consistent with the upstream change? If **not affected**,
   self-skip — report "no change needed" and do not touch the file. (This is the guard against
   over-propagation: most changes don't ripple all the way down.)
3. **If affected, amend surgically.** Update only the parts the change touches, in place. **Preserve
   the `## Forks / Decisions log`** (and, for the backlog, task status/history) — never regenerate the
   document from scratch. Update the human `*.summary.md` too if the essence changed.
4. **Record it.** Add a `## Forks / Decisions log` entry noting the propagation: what upstream changed,
   what this doc changed in response, confidence. (For the backlog, append a `## Log` note on each
   touched task.)
5. **Ask only on a critical question.** If reconciling forces a decision the skill can't make safely —
   a decision-changing fork, a low-confidence call, or anything destructive — surface it to the human
   (both modes). Otherwise proceed and log it.

The skill does its normal research/sanity-checks as needed for the amended part — but scoped to the
change, not a full re-run.

## The conductor walk (propagate-changes)

`propagate-changes` drives the chain forward from the changed stage:

- For each downstream stage in order, invoke its skill in amend mode (via the Skill tool) with the
  upstream change. The skill amends or self-skips. **Routine reconciliation proceeds automatically;**
  only critical/destructive questions stop for the human.
- A change that an early stage absorbs without rippling further lets the walk stop early (later stages
  self-skip). A change that ripples continues down the chain.
- **Continue into the backlog.** After the spec stages, invoke `plan-development` in amend mode to
  reconcile the backlog as **task deltas** — add / modify / cancel / reopen-as-rework (see
  `planning-method.md`), using `traces_to` to find the affected tasks. **Cancel and reopen-as-rework
  are destructive — always confirm with the human**, in both modes.
- **Never write code.** Propagation updates documents and the backlog only. Rebuilding the affected
  features happens later, through the normal `build-product` loop, when the user runs it.

## What always stops (regardless of mode)

- Any **destructive backlog delta** — cancelling a task, or reopening a `done` task as rework.
- Any **decision-changing or low-confidence** reconciliation a stage can't make safely.

Everything else — routine, confident, non-destructive reconciliation — proceeds automatically and is
logged.
