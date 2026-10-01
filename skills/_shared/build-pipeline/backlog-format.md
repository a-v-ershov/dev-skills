# Backlog format & lifecycle (shared — build pipeline)

A **kanban backlog**: one markdown file per task, status in its frontmatter; a task's `blocked_by` list
*is* the dependency graph. The contract every build skill (`plan-development`, `build-tasks`,
`implement-feature`, `verify-feature`, `run-task`) reads and writes against.

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

`.dev-skills/build-plan/` is committed project documentation (like `.dev-skills/project-spec/`); each
skill creates it if absent.

## One file per task — `tasks/<id>-<slug>.md`

A status change edits only that task's file — nothing shared to contend on. IDs are `T###`, in
creation order, never reused.

**The board holds at most 15 open tasks, and every skill that files one respects that** —
`plan-development`, the release audits, `refactor`, `write-tests`, `run-task`'s adhoc entry point
(grain and the ceiling: `planning-method.md`).

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
claim:                        # present ONLY while status is in_progress; absent otherwise
  by: run-task@7f3c1a         # holder id — skill@session-prefix, so two sessions are distinguishable
  stage: verify               # build | verify | fix | solve | commit — what is happening RIGHT NOW
  since: 2026-06-18T11:05:00Z # when this stage started
  heartbeat: 2026-06-18T11:52:00Z   # re-stamped whenever the holder writes to the task; stale = 30 min
acceptance:                   # the behavioral criteria verify-feature must prove (from the spec)
  - "Given a logged-in user, When they search 'invoice', Then matching docs are listed"
  - "Given an empty query, When they search, Then a 400 is returned (not a 500)"
timings:                      # wall-clock seconds per stage, written by run-task when the task leaves
  build: 412                  # the implementer (or setup-dev-environment on a `setup` task)
  verify: 187                 # the separate verifier
  fix: 96                     # the one fix round + gate — absent when verification passed first time
  solve: 74                   # the solve pass + the static gate and the scoped test run
  total: 903                  # in_progress → done/needs_human, so it also holds the human's waiting time
history:                      # status transitions: time + actor + optional note. Append-only.
  - { at: 2026-06-18T10:00:00Z, to: todo,        by: plan-development }
  - { at: 2026-06-18T11:05:00Z, to: in_progress, by: implement-feature, note: "started" }
  - { at: 2026-06-18T13:10:00Z, to: done,        by: build-tasks, note: "verified + committed" }
---

## Description (for AI)

<The full brief for the executor agent: what to build, where it fits, relevant spec sections,
constraints, design notes — as long as it needs to be. `summary` is the one-line human view.>

## Log

<Append-only, newest last. Implementer and verifier write findings here — what was done, what was
found, evidence links. The verifier's findings land as a batch each round.>

- 2026-06-18T12:31Z [implement-feature] Search endpoint + header UI done; happy path self-verified.
- 2026-06-18T12:45Z [verify-feature] FAIL: empty query → 500 (expected 400). artifacts/T012-empty.png
- 2026-06-18T12:58Z [implement-feature] fix round: empty query now 400; gate green (verifier tests pass).
- 2026-06-18T13:05Z [build-tasks] accepted by human; spec_sync pending → search added to flows.
```

### Field rules

- **`type`** — `setup` (environment/scaffolding, run by `setup-dev-environment`); `feature` (run by
  `implement-feature` then `verify-feature`); `verify` (optional cross-cutting check — an end-to-end
  pass over several features, or proving a pre-existing feature against its criteria); `rework` (a fix
  to built code, **dispatched exactly like `feature`** — filed by a release finding (an `audit-*`, or a
  bug `refactor` / `write-tests` found and did not fix), a `plan-development` reopen, or delta mode on
  a brownfield codebase; `traces_to` points at the finding / changed spec section / as-is map
  finding). Every task is **coarse** — one per coherent fix, each finding its own `acceptance` entry
  (`planning-method.md`).
- **`summary`** — one plain-language line, no jargon; the board shows it.
- **`status`** — see the lifecycle below.
- **`created`** — ISO-8601 UTC, written once; get the time at runtime (`date -u +%Y-%m-%dT%H:%M:%SZ`).
- **`blocked_by`** — the only ordering constraint; `[]` when none.
- **`traces_to`** — spec section anchors. No orphans: every `feature` task traces to a
  product-requirements feature and/or a user-flow. Amend mode uses it to find affected tasks.
- **`origin`** — `spec` (planned by `plan-development`) or `adhoc` (raised by the user during a build
  run, e.g. "the card doesn't show the date"); an `adhoc` task has no `traces_to` until the spec
  catches up.
- **`spec_sync`** — `none` when the task changes nothing the spec describes; **`pending`** the moment
  the work changes observable behavior the spec doesn't reflect; `done` once the spec edit lands. The
  board surfaces `pending` tasks (the next plan would start stale).
- **`review`** — `pending` until accepted; then `human` (a person looked at it) or `auto` (nothing
  hand-checkable — tests and internal logic, all criteria proven by the verifier). Never set `auto` to
  skip an awkward conversation.
- **`acceptance`** — behavioral, testable criteria (Given/When/Then or EARS) derived from
  `product-requirements.research.md` (and `user-flows.research.md`); what the verifier proves against.
- **`timings`** — wall-clock **seconds** per stage, written once by `run-task` when the task leaves
  (`done` *or* `needs_human`); absent until then; a stage that didn't run has no key. Prompts and the
  human's acceptance answer are inside it, so `total` normally exceeds the stages summed — the
  remainder is mostly the human. Never a model benchmark or a target. Across tasks, a `verify` near or
  above its `build` (proving should cost a fraction of building) means the verifier re-authors the
  implementer's work — a finding about `implement-feature`, `verify-feature` and
  `verification-method.md`, not about the task.
- **`claim`** — who is on this task **right now**; present only while `in_progress`. Written by
  `run-task` **before** it spawns anything, re-stamped (`stage`, `heartbeat`) at every stage boundary,
  removed when the task leaves `in_progress`. `stage` + `since` is the live status. A
  `claim.heartbeat` **fresher than 30 minutes** → another run skips the task and says who holds it;
  older → the holder is presumed dead and the task may be reclaimed — announced, never silently.
  Advisory, the task-level twin of the env lease (`env-access.md`): it prevents collisions, never locks
  a human out.
- **`history`** — append-only transition log, entries `{ at, to, by, note? }`. Never rewrite past
  entries.

## Status lifecycle

```
todo ──> in_progress ──> done
  │           │
  │           └──> needs_human   (the fix round didn't close it, or a blocker it can't resolve)
  └──> cancelled                  (scope removed — a feature deleted from the spec, not parked)
```

- **`todo`** — created, not started.
- **`in_progress`** — claimed. **`run-task` sets this, and writes `claim`, BEFORE it spawns the
  implementer**, so the state is readable while the expensive step runs.
- **`done`** — built, verified, accepted (`review: human` or `auto`), committed.
- **`needs_human`** — escalated: the fix round didn't close a critical criterion, the gate stayed red,
  or a blocker couldn't be resolved; the `## Log` holds what the human needs. Shown first on the board.
- **`cancelled`** — terminal; no longer wanted (a feature removed from the spec). A `done` task whose
  feature changed is **not** cancelled — it is reopened as rework (`propagation-method.md`).

`needs_human` and `cancelled` are not "fresh" work: the orchestrator never picks them.

## `ready` and the dependency graph

Derived on demand from `blocked_by`, never stored:

- **`ready(T)`** ⟺ `T.status == todo` **AND** every id in `T.blocked_by` is a task with `status: done`.
- A `todo` task with an unfinished (or `cancelled`/`needs_human`) blocker is **blocked** (`blocked` is a
  derived display state, not a stored status).
- **Pick one at a time:** one `ready` task per iteration; tie-break by lowest `id` for reproducibility.

No parallelism: tasks are built one after another on a single working tree (see `build-tasks`).

## `board.md` — the derived human view

Plain markdown a human opens directly (IDE preview / GitHub render / `glow`). **Regenerated** from the
task files by `plan-development` and `run-task` — never hand-edited. Group by status, list `id` ·
`summary`, `needs_human` first. Shape:

```markdown
# Build board

> Generated <date> · **<done>/<total> tasks done (<pct>%)** · <ready> ready · <blocked> blocked ·
> <needs_human> need you · <cancelled> cancelled
> **Now:** T012 · verify · started 11:05Z (52 min) — run-task@7f3c1a   ← or "Now: idle"
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

The header answers *how far along?* and *what are you doing right now?* The percentage counts `done`
against every task not `cancelled`. **Now** comes from the `claim` of the `in_progress` task (at most
one per session); with none it reads `Now: idle`. Regenerate the header at every stage boundary, not
only when a task finishes.

**Reconciled with spec** is the anchor `build-tasks` checks before a run: the commit the backlog was
last planned against, so `git log <sha>..HEAD -- .dev-skills/project-spec/` answers "has the spec moved
ahead of the plan?". Only `plan-development` writes it.

The board is a dashboard; the task files are the source of truth.
