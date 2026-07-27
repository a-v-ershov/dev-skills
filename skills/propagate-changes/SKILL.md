---
name: propagate-changes
disable-model-invocation: true
description: "Reconcile the downstream documents after an upstream spec change. Use when a stage document in .dev-skills/project-spec/ has been edited (e.g. product vision changed) and the later stages — architecture, dev-architecture — and the build backlog need to be brought back in line. A thin cross-cutting conductor: it walks the dependency chain FORWARD from the changed stage, invoking each downstream stage's own skill in amend mode to surgically update its document (preserving the Forks/Decisions log), then continues into the backlog via plan-development (add/modify/cancel/reopen-as-rework task deltas). Runs automatically — no 'do you want to propagate?' gate — and pauses only for critical or destructive questions (cancelling a task, reopening a done one). It never writes code; rebuilding the affected features is a separate build-product run."
argument-hint: "[--from <stage>]"
---

# Propagate Changes Skill (conductor)

You are the conductor of change propagation. When a stage document changes, you bring everything
downstream of it back into agreement — **forward only**, surgically, automatically. You do not do each
stage's reconciliation yourself; you invoke that stage's own skill in **amend mode** (via the Skill
tool) and move on. You never write code.

The chain you walk:

```
idea-validation → product-requirements → user-flows → design-decisions → architecture
   → dev-architecture → [ backlog (.dev-skills/build-plan) ]
```

A change at stage N may ripple to N+1, N+2, … through to the backlog — or be absorbed early, in which
case later stages self-skip and the walk stops. Full method, the per-skill amend contract, and what
always stops for the human: **`../_shared/build-pipeline/propagation-method.md`**.

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill follows the same
rule on its own. Never translate code, identifiers, file paths, or commands.

## Modes

Read `.dev-skills/build-plan/.build-config.md` (or `.dev-skills/project-spec/.spec-config.md`) for `mode`. Full
rules: **`../_shared/build-pipeline/build-config.md`**.

- The forward walk over the **spec** documents runs **automatically** in both modes — routine,
  confident reconciliation does not stop.
- **Always stops for the human, in both modes:** any destructive backlog delta (cancel a task, reopen
  a `done` one) and any decision-changing / low-confidence reconciliation a stage can't make safely.

## Operating principles (non-negotiable)

- **Forward only.** Reconcile stages after the changed one; never edit upstream (that's a new change).
- **Surgical, not regenerated.** Each stage amends its own document in place, preserving its
  Forks/Decisions log (and, for the backlog, task status/history).
- **Assess impact; self-skip if unaffected.** Don't over-propagate — most changes don't ripple all the
  way down. A stage that isn't affected reports "no change needed" and the walk can stop.
- **Automatic, but not reckless.** Run without a "propagate?" gate, but stop for critical/destructive
  questions.
- **Never write code.** You update documents and the backlog only. Rebuilding is `build-product`.

## Procedure

```
- [ ] Step 0: Identify the changed stage (named, or --from), read its current document, read mode
- [ ] Step 1: Walk the spec forward — for each downstream stage, invoke its skill in amend mode; it amends or self-skips
- [ ] Step 2: Backlog — invoke plan-development (amend mode) → task deltas; destructive deltas confirm
- [ ] Done: report what changed at each stage + the backlog deltas + whether a build-product rebuild is now needed
```

### Step 0: Identify the changed stage
Determine which stage document changed — from `--from <stage>`, from what the user tells you, or by
asking which doc they edited. Read that document (the new state). Note its position in the chain; the
downstream stages are everything after it.

### Step 1: Walk the spec forward
For each downstream stage in chain order, **invoke its skill in amend mode** (via the Skill tool),
passing the upstream change. The skill reads the changed upstream + its own doc, **assesses impact**,
and either **self-skips** (reports "no change needed") or **amends surgically** (updating its
`*.research.md` + `*.summary.md`, preserving its Forks/Decisions log, logging the propagation). It
asks the human only on a critical question. If a stage absorbs the change and nothing ripples further,
let the walk stop. The stage skills, in order, are: `define-product-requirements`, `create-user-flows`,
`define-design-decisions`, `design-architecture`, `design-dev-architecture` (each gained an amend mode).

### Step 2: Reconcile the backlog
After the spec stages, invoke `plan-development` in **amend mode**. It diffs the new spec against the
current tasks and emits **deltas** — add / modify / cancel / reopen-as-rework — using `traces_to` to
find affected tasks, then regenerates `board.md`. **Cancel and reopen-as-rework are destructive —
confirm with the human** (both modes). No code is written.

### Done: report
Summarize: which stages amended (and which self-skipped), the backlog deltas applied, and — because
some `done` tasks may have been reopened as rework — whether a `build-product` run is now needed to
rebuild the affected features. Point the user at the changed docs and `.dev-skills/build-plan/board.md`.

## Rules

1. **Conduct, don't duplicate.** Each stage reconciles itself via its own skill's amend mode; the
   backlog via `plan-development`. You sequence; you don't rewrite their logic.
2. **Forward only; surgical; preserve decision logs and task history.** Never regenerate a document.
3. **Automatic for routine reconciliation; always stop for destructive/critical questions.**
4. **Self-skip unaffected stages** — don't over-propagate.
5. **Never write code.** Rebuilding affected features is a separate `build-product` run.
