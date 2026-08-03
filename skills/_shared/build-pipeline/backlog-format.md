# Backlog format & lifecycle (shared — build pipeline)

The build pipeline tracks work as a **kanban backlog**: one markdown file per task, status in the
file's frontmatter, dependencies expressed as blockers. The dependency graph is implicit — a task's
`blocked_by` list *is* the set of edges; nothing materializes a separate graph. This file is the
contract every build skill (`plan-development`, `build-tasks`, `implement-feature`,
`verify-feature`, `run-task`, `build-tasks`) reads and writes against.

## Where it lives

```
.dev-skills/build-plan/
  .build-config.md            # mode (see build-config.md)
  board.md                    # derived human view — regenerated, never hand-edited
  plan.summary.md             # short human summary of the build plan
  tasks/
    T001-<slug>.md            # one file per task
    T002-<slug>.md
    artifacts/                # verifier evidence (screenshots, logs) referenced from task logs.
                              # Copied in at acceptance — never a test's write target, or every
                              # later run rewrites it (verification-method.md).
```

`.dev-skills/build-plan/` is committed project documentation (like `.dev-skills/project-spec/`). Each skill creates
the directory if absent.

## One file per task — `tasks/<id>-<slug>.md`

The single-file-per-task layout is deliberate: a task's status changes only edit *that* task's own
file, so there is no shared file to contend on. IDs are `T###`, assigned in creation order and never
reused.

```yaml
---
id: T012
type: feature                 # setup | feature | verify | rework
title: "Search across documents"
summary: "Document search from the app header"        # SHORT, one line, for humans (the board)
status: todo                  # todo | in_progress | done | cancelled | needs_human
created: 2026-06-18T10:00:00Z                          # ISO-8601 UTC, set once on creation
blocked_by: [T003, T007]      # task ids that must be `done` before this is `ready`. [] if none.
traces_to: "product-requirements.research.md#search · user-flows.research.md#find-a-doc"
origin: spec                  # spec | adhoc — where the task came from
spec_sync: none               # none | pending | done — does the spec still describe the product?
review: pending               # pending | human | auto — how the finished work was accepted
acceptance:                   # the behavioral criteria verify-feature must prove (from the spec)
  - "Given a logged-in user, When they search 'invoice', Then matching docs are listed"
  - "Given an empty query, When they search, Then a 400 is returned (not a 500)"
timings:                      # wall-clock seconds per stage, written by run-task when the task leaves
  build: 412                  # the implementer (or setup-dev-environment on a `setup` task)
  verify: 187                 # the separate verifier
  fix: 96                     # the one fix round + gate — absent when verification passed first time
  solve: 74                   # the solve pass + the full gate
  total: 903                  # in_progress → done/needs_human, so it also holds the human's waiting time
history:                      # status transitions: time + actor + optional note. Append-only.
  - { at: 2026-06-18T10:00:00Z, to: todo,        by: plan-development }
  - { at: 2026-06-18T11:05:00Z, to: in_progress, by: implement-feature, note: "started" }
  - { at: 2026-06-18T13:10:00Z, to: done,        by: build-tasks, note: "verified + committed" }
---

## Description (for AI)

<The full, detailed task description for the executor agent: what to build, where it fits, the
relevant spec sections, constraints, and any design notes. This is the AI-facing brief — as long as
it needs to be. The frontmatter `summary` is the one-line human view; this is the depth.>

## Log

<Append-only, newest last. The implementer and the (separate) verifier write findings here — what
was done, what was found, evidence links. The verifier's findings accumulate as a batch each round.>

- 2026-06-18T12:31Z [implement-feature] Search endpoint + header UI done; happy path self-verified.
- 2026-06-18T12:45Z [verify-feature] FAIL: empty query → 500 (expected 400). artifacts/T012-empty.png
- 2026-06-18T12:58Z [implement-feature] fix round: empty query now 400; gate green (verifier tests pass).
- 2026-06-18T13:05Z [build-tasks] accepted by human; spec_sync pending → search added to flows.
```

### Field rules

- **`type`** — `setup` (an environment/scaffolding task, run by `setup-dev-environment`), `feature`
  (a product feature, run by `implement-feature` then `verify-feature`), `verify` (an optional
  cross-cutting check, e.g. an end-to-end pass over several features, or — in an existing project —
  proving a pre-existing/adopted feature against its acceptance criteria), `rework` (a fix to
  already-built code — filed by a release-phase finding (an `audit-*`, or a bug `refactor` /
  `write-tests` found and deliberately did not fix), a `plan-development` reopen, or
  `plan-development` delta mode reconciling a brownfield codebase against the target spec; `traces_to`
  points at the audit finding / changed spec section / as-is map finding; **dispatched exactly like
  `feature`**: `implement-feature` then `verify-feature`).
- **`summary`** — one line, plain language, no jargon; this is what the board shows a human.
- **`status`** — see the lifecycle below.
- **`created`** — ISO-8601 UTC, written once. Get the time at runtime (`date -u +%Y-%m-%dT%H:%M:%SZ`).
- **`blocked_by`** — the only ordering constraint. A task with no dependencies has `[]`.
- **`traces_to`** — provenance into the spec (research-doc section anchors). No orphan tasks: every
  `feature` task traces to a product-requirements feature and/or a user-flow. This is also what
  `plan-development` amend mode uses to find which tasks a changed spec section affects.
- **`origin`** — `spec` (planned by `plan-development` from the spec — the normal case) or `adhoc`
  (raised directly by the user during a build run, e.g. "the card doesn't show the date"). An `adhoc`
  task has no `traces_to` until the spec catches up.
- **`spec_sync`** — `none` when the task changes nothing the spec describes; **`pending`** the moment
  the work changes observable product behavior that the spec doesn't yet reflect; `done` once the spec
  edit lands. A task sitting at `pending` means the next plan would be built from a stale picture —
  the board surfaces those.
- **`review`** — `pending` until the work is accepted; then `human` (a person looked at it) or `auto`
  (nothing a human could check by hand — the diff is tests and internal logic, all criteria proven by
  the verifier). Never set `auto` to skip an awkward conversation.
- **`acceptance`** — the behavioral, testable criteria (Given/When/Then or EARS) copied/derived from
  the feature's acceptance criteria in `product-requirements.research.md` (and the flow's criteria in
  `user-flows.research.md`). The definition of done the verifier proves against.
- **`timings`** — wall-clock **seconds** per stage, written once by `run-task` when the task leaves
  (`done` *or* `needs_human`); the whole block is absent until then, and a stage that didn't run has
  no key. It is honest wall-clock, **not** compute time: waiting on a permission prompt and on the
  human's acceptance answer is inside it, so `total` is normally larger than the stages added up and
  the remainder is mostly the human. Read it to see where a task's time went — never as a benchmark
  of a model or a target to optimize. One ratio is worth watching across tasks rather than within
  one: **`verify` against `build`**. Proving a feature should cost a fraction of building it, so a
  `verify` that keeps landing near or above its `build` says the two roles are covering the same
  ground — the verifier re-authoring what the implementer already wrote — and that is a finding about
  `implement-feature`, `verify-feature` and `verification-method.md`, not about the task in front of
  you.
- **`history`** — append-only transition log; each entry `{ at, to, by, note? }`. Never rewrite past
  entries.

## Status lifecycle

```
todo ──> in_progress ──> done
  │           │
  │           └──> needs_human   (the fix round didn't close it, or a blocker it can't resolve)
  └──> cancelled                  (scope removed — a feature deleted from the spec, not parked)
```

- **`todo`** — created, not started.
- **`in_progress`** — an executor has claimed it (set when `implement-feature`/`setup-dev-environment`
  begins).
- **`done`** — built, verified, accepted (`review: human` or `auto`), and committed.
- **`needs_human`** — escalated: the one fix round didn't close a critical criterion, the quality gate
  stayed red, or a blocker couldn't be resolved autonomously. The task's `## Log` holds the findings
  the human needs. Surfaced prominently on the board.
- **`cancelled`** — terminal; the work is no longer wanted (e.g. a feature removed from the spec).
  A `done` task whose feature changed is **not** cancelled — it is reopened as a rework task (see
  `propagation-method.md`).

`needs_human` and `cancelled` are not "fresh" work: the orchestrator never picks them.

## `ready` and the dependency graph

The graph is implicit in `blocked_by`. Derived on demand, never stored:

- **`ready(T)`** ⟺ `T.status == todo` **AND** every id in `T.blocked_by` is a task with `status: done`.
- A `todo` task with an unfinished (or `cancelled`/`needs_human`) blocker is **blocked** — not ready.
  (`blocked` is a derived display state, not a stored status.)
- **Pick one at a time:** the orchestrator selects a single `ready` task per iteration. When several
  are ready, tie-break deterministically by lowest `id` (declaration order) so runs are reproducible.

There is no parallelism: tasks are built one after another on a single working tree (see
`build-tasks`). Blockers are the only thing that serialize beyond that.

## `board.md` — the derived human view

Plain markdown a human opens directly (IDE preview / GitHub render / `glow`). It is **regenerated**
from the task files by `plan-development` and `run-task` — never hand-edited. Group by status,
list `id` · `summary`, and put any `needs_human` tasks first as a prominent group. Shape:

```markdown
# Build board

> Generated <date> · <N> tasks · <done>/<total> done
> Reconciled with spec: <commit sha> (<date>)

## ⚠ Needs human
- **T009** Reset-password email delivery — the fix round didn't close it (see task log)

## ↺ Spec not updated yet
- **T011** Bulk export — shipped, `spec_sync: pending`

## In progress
- **T012** Document search from the app header

## Ready
- **T014** Export a document to PDF

## Blocked
- **T015** Share a document by link — waiting on T012

## Done
- **T003** Project scaffold · **T007** Auth wiring

## Cancelled
- (none)
```

The **Reconciled with spec** line is the anchor `build-tasks` checks before a run: it records the
commit the backlog was last planned against, so `git log <sha>..HEAD -- .dev-skills/project-spec/`
answers "has the spec moved ahead of the plan?" in one command. `plan-development` writes it; nothing
else touches it.

Keep the board light: it is a dashboard, not the source of truth. The task files are the truth; the
board is derived from them every time.
