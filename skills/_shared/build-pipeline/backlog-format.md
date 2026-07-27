# Backlog format & lifecycle (shared — build pipeline)

The build pipeline tracks work as a **kanban backlog**: one markdown file per task, status in the
file's frontmatter, dependencies expressed as blockers. The dependency graph is implicit — a task's
`blocked_by` list *is* the set of edges; nothing materializes a separate graph. This file is the
contract every build skill (`plan-development`, `build-product`, `implement-feature`,
`verify-feature`, `propagate-changes`) reads and writes against.

## Where it lives

```
.dev-skills/build-plan/
  .build-config.md            # mode + max_verify_iterations (see build-config.md)
  board.md                    # derived human view — regenerated, never hand-edited
  plan.summary.md             # short human summary of the build plan
  tasks/
    T001-<slug>.md            # one file per task
    T002-<slug>.md
    artifacts/                # verifier evidence (screenshots, logs) referenced from task logs
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
verify_attempts: 0            # bumped by verify-feature each implement↔verify cycle
acceptance:                   # the behavioral criteria verify-feature must prove (from the spec)
  - "Given a logged-in user, When they search 'invoice', Then matching docs are listed"
  - "Given an empty query, When they search, Then a 400 is returned (not a 500)"
history:                      # status transitions: time + actor + optional note. Append-only.
  - { at: 2026-06-18T10:00:00Z, to: todo,        by: plan-development }
  - { at: 2026-06-18T11:05:00Z, to: in_progress, by: implement-feature, note: "started" }
  - { at: 2026-06-18T13:10:00Z, to: done,        by: build-product, note: "verified + committed" }
---

## Description (for AI)

<The full, detailed task description for the executor agent: what to build, where it fits, the
relevant spec sections, constraints, and any design notes. This is the AI-facing brief — as long as
it needs to be. The frontmatter `summary` is the one-line human view; this is the depth.>

## Log

<Append-only, newest last. The implementer and the (separate) verifier write findings here — what
was done, what was found, evidence links. The verifier's findings accumulate as a batch each round.>

- 2026-06-18T12:31Z [implement-feature] Search endpoint + header UI done; happy path self-verified.
- 2026-06-18T12:45Z [verify-feature] iter 1 FAIL: empty query → 500 (expected 400). artifacts/T012-empty.png
- 2026-06-18T13:05Z [verify-feature] iter 2 PASS: both acceptance criteria proven (DB rows asserted).
```

### Field rules

- **`type`** — `setup` (an environment/scaffolding task, run by `setup-dev-environment`), `feature`
  (a product feature, run by `implement-feature` then `verify-feature`), `verify` (an optional
  cross-cutting check, e.g. an end-to-end pass over several features, or — in an existing project —
  proving a pre-existing/adopted feature against its acceptance criteria), `rework` (a fix to
  already-built code — filed by a release-phase `audit-*` finding, a `propagate-changes` reopen, or
  `plan-development` delta mode reconciling a brownfield codebase against the target spec; `traces_to`
  points at the audit finding / changed spec section / as-is map finding; **dispatched exactly like
  `feature`**: `implement-feature` then `verify-feature`).
- **`summary`** — one line, plain language, no jargon; this is what the board shows a human.
- **`status`** — see the lifecycle below.
- **`created`** — ISO-8601 UTC, written once. Get the time at runtime (`date -u +%Y-%m-%dT%H:%M:%SZ`).
- **`blocked_by`** — the only ordering constraint. A task with no dependencies has `[]`.
- **`traces_to`** — provenance into the spec (research-doc section anchors). No orphan tasks: every
  `feature` task traces to a product-requirements feature and/or a user-flow. This is also what
  `propagate-changes` uses to find which tasks a changed spec section affects.
- **`verify_attempts`** — starts at 0; `verify-feature` increments it each implement↔verify round and
  escalates to `needs_human` at the cap (`max_verify_iterations`, default 4).
- **`acceptance`** — the behavioral, testable criteria (Given/When/Then or EARS) copied/derived from
  the feature's acceptance criteria in `product-requirements.research.md` (and the flow's criteria in
  `user-flows.research.md`). The definition of done the verifier proves against.
- **`history`** — append-only transition log; each entry `{ at, to, by, note? }`. Never rewrite past
  entries.

## Status lifecycle

```
todo ──> in_progress ──> done
  │           │
  │           └──> needs_human   (verify cap hit, or a blocker the executor can't resolve)
  └──> cancelled                  (scope removed — a feature deleted from the spec, not parked)
```

- **`todo`** — created, not started.
- **`in_progress`** — an executor has claimed it (set when `implement-feature`/`setup-dev-environment`
  begins).
- **`done`** — built **and** verified green; committed.
- **`needs_human`** — escalated: the bounded implement↔verify loop hit `max_verify_iterations` with a
  critical acceptance criterion still failing, or a blocker can't be resolved autonomously. The task's
  `## Log` holds the accumulated findings the human needs. Surfaced prominently on the board.
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
`build-product`). Blockers are the only thing that serialize beyond that.

## `board.md` — the derived human view

Plain markdown a human opens directly (IDE preview / GitHub render / `glow`). It is **regenerated**
from the task files by `plan-development` and `build-product` — never hand-edited. Group by status,
list `id` · `summary`, and put any `needs_human` tasks first as a prominent group. Shape:

```markdown
# Build board

> Generated <date> · <N> tasks · <done>/<total> done

## ⚠ Needs human
- **T009** Reset-password email delivery — verify failed 4× (see task log)

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

Keep the board light: it is a dashboard, not the source of truth. The task files are the truth; the
board is derived from them every time.
