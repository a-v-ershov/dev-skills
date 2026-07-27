# Planning method (shared — build pipeline)

How `plan-development` turns the spec into the kanban backlog, and how it **amends** that backlog
when the spec changes. The task schema, lifecycle, and board live in **`backlog-format.md`** — this
file is about *deriving* the tasks. Single pass: there is no separate "decompose into a graph" stage —
the blockers a task carries are the graph.

## Inputs (read, never re-decide)

- `.dev-skills/project-spec/product-requirements.research.md` — the committed feature set; each feature has
  ≥1 behavioral **acceptance criterion** and a "serves (validated need)" trace. These become tasks.
- `.dev-skills/project-spec/user-flows.research.md` — flows + their per-flow acceptance criteria; they sharpen
  a feature task's criteria and surface cross-feature ordering.
- `.dev-skills/project-spec/architecture.research.md` + `dev-architecture.research.md` — the components and
  the local stack, to size tasks and seed `setup` tasks and dependencies (e.g. auth before features
  that need a logged-in user); also the **developer/test scripts** and the **custom project skills**
  that wrap them to build out (their skeletons are scaffolded by `setup-dev-environment`; the full
  implementation/authoring is backlog work).
- `.dev-skills/project-setup/setup-log.md` (if present) — what the environment already has, so `setup` tasks
  aren't re-created.
- The root `DESIGN.md` + `.dev-skills/project-setup/design-system.md` (if present) — the committed design
  system UI feature tasks build against. Reference it in a UI task's `## Description` so the implementer
  applies it; do **not** emit "mockup" tasks — mockups are on-demand (`generate-mockups`), never backlog
  work.
- `.dev-skills/project-spec/codebase-map.research.md` (existing projects only) — the as-is facts the spec was
  reconstructed from; in **delta mode** (below) the backlog is the diff of the TARGET spec against this.

Planning never re-opens product or technical decisions. A gap in the spec is surfaced back, not
invented here.

## Deriving tasks (create mode)

1. **One `feature` task per committed feature** (occasionally split a large feature into a few tasks
   when its acceptance criteria are independently buildable/verifiable). Carry the feature's
   acceptance criteria into the task's `acceptance`, sharpened with the relevant flow criteria.
2. **`setup` tasks for environment work not already done** (per `setup-log.md`) that features depend
   on — e.g. a migration baseline, a seed fixture, an auth scaffold. Usually few; most setup is the
   `setup-dev-environment` skill's job, so only add `setup` tasks for build-time prerequisites.
3. **Type every task** (`setup` | `feature` | `verify`) and write **`traces_to`** for each — the spec
   section(s) it comes from. No orphans: a task that traces to nothing doesn't belong.
4. **Dual description.** `summary` = one human line; `## Description` = the full AI brief (what to
   build, the relevant spec sections, constraints, design notes).
5. **Acceptance.** Copy/derive the behavioral criteria the task must satisfy — the definition of done
   `verify-feature` proves against. A feature task with no acceptance criteria is incomplete.
6. **Developer/test-script tasks.** `dev-architecture.research.md` specifies purpose-built developer &
   test scripts (fast subset/stage runners, fixture/sample generators, intermediate inspectors); their
   skeletons are scaffolded by `setup-dev-environment`, so add tasks to **build them out fully** (type
   `setup` or `feature`, `traces_to` the dev-architecture dev-scripts section). They widen the agent's
   verification loop, so blockers usually put the foundational ones early.
7. **Custom-skill tasks.** `dev-architecture.research.md`'s *Custom project skills* table names the
   project-local Claude Code skills that wrap those scripts/harness into named verification jobs
   (`/run-integration-tests`, `/verify-flow`, `/reset-env`); their skeletons are scaffolded by
   `setup-dev-environment` under `.claude/skills/`, so add one `setup` task per skill to **author it
   fully** (`traces_to` the dev-architecture custom-skills section). Each is **`blocked_by` the
   dev/test-script-buildout task(s) it wraps** — a skill can't be verified until the script it runs
   works. They complement `verification.md`; a task that merely restates `verify-feature` doesn't belong.

## Setting blockers (the implicit graph)

For each task, set `blocked_by` to the task ids that must be `done` first. Derive dependencies from
**real** constraints, not guesses:

- **Data/domain order** — a feature that reads an entity depends on the task that creates it.
- **Auth/identity** — anything needing a logged-in user depends on the auth task.
- **Foundational setup** — features depend on the `setup` tasks that establish their substrate.
- **Flow order** — `user-flows.research.md` often implies a natural build order (create before edit
  before share).

Keep the graph shallow: only add an edge when one task genuinely cannot be verified until another is
`done`. Over-blocking serializes work that didn't need to be. There are no parallel waves to protect,
so there is **no `conflicts_with`** — blockers are the only ordering tool.

## Output

Write each task to `.dev-skills/build-plan/tasks/<id>-<slug>.md` (schema: `backlog-format.md`), regenerate
`.dev-skills/build-plan/board.md`, and write `.dev-skills/build-plan/plan.summary.md` — a short human view:

```markdown
# Build plan — <Product name>

> Generated <date> · <N> tasks · Mode: <interactive | autopilot>

## What gets built
- <3–6 bullets: the shape of the backlog — the main feature groups and the build order.>

## Build order (the dependency spine)
- <The few load-bearing dependencies, e.g. "auth (T002) → everything user-scoped">.

## Open questions for you
- <Any spec gap or low-confidence planning fork the human should resolve. If none: "None.">
```

Log any planning fork (e.g. how a large feature was split, an assumed dependency) in a
`## Forks / Decisions log` in `plan.summary.md`'s companion or inline — interactive asks; autopilot
decides and records, per `build-config.md`.

## Amend mode (change propagation)

When `propagate-changes` reaches the backlog after a spec change, it invokes `plan-development` in
**amend mode** with the upstream change. Do **not** regenerate the backlog — that would destroy task
status and history. Instead, diff the new spec against the current tasks and emit **deltas**:

- **Add** — a new feature/flow → a new `todo` task (with blockers + acceptance), appended with the
  next free id.
- **Modify** — a changed feature → update the affected task's `## Description` / `acceptance` /
  `summary` in place; append a `## Log` note recording the propagation. Use `traces_to` to find
  exactly which tasks a changed spec section touches.
- **Cancel** — a feature removed from the spec → set the task `status: cancelled` (terminal). **This
  is destructive — always confirm with the human** (both modes), per `build-config.md`.
- **Reopen as rework** — a feature changed in a way that invalidates already-`done` work → set the
  done task back to `todo` (or, if you want to preserve the original's history cleanly, add a new
  rework task that references it), append a `## Log` note explaining what changed and why it must be
  rebuilt. **Destructive — always confirm.** Already-built-but-now-wrong code becomes an explicit
  rework task, never a silent revert.

After applying deltas, regenerate `board.md`. Amend mode never builds code — it only updates the
backlog; the actual rebuild happens later through the normal `build-product` loop.

## Existing-project (delta) mode

When `project_type: existing` (see `../spec-pipeline/pipeline-config.md`), the spec was reconstructed
from an already-built codebase: the spec describes the **TARGET** state, and
`.dev-skills/project-spec/codebase-map.research.md` records the **as-is** code. So the *initial* backlog is
not "one task per feature" — most features already exist. Instead, **diff TARGET against as-is and
emit only the gap.** This is the brownfield create mode; it shares the add/modify/cancel/reopen
vocabulary with amend mode above.

The diff is already done for you: each phase's `## Forks / Decisions log` carries the **drift columns**
(`AS-IS` / `TARGET` / `Drift?`) for every reconciled feature/flow/component (see
`../spec-pipeline/existing-project-mode.md`). Read `Drift?` and emit one task per entry:

- **`no` (keep — built & matches TARGET)** → a `feature` task with **`status: done`**, a `history`
  note `"pre-existing, adopted from codebase-map"`, and the acceptance criteria copied in — but **no
  implementation work**. It exists for traceability and so dependent tasks see their blocker satisfied.
  Adopted-done is **provisional** (the map read the code, it didn't run it) — see the verification
  tasks below.
- **`change` (built but divergent)** → a **`rework`** task (`status: todo`), `traces_to` the changed
  spec section + the map's as-is finding; `## Description` states what exists and what the target is.
- **`new` (intended, not yet built)** → a normal `feature` task (`status: todo`), exactly as in create
  mode.
- **`remove` (built but not wanted)** → a `rework` task ("remove <feature>") or a recorded non-goal.
  **Destructive — always confirm with the human** (both modes), like an amend cancel.

Then add the **gap-closing setup/verify work** the map surfaced (the "missing tests + quality gate"
delta):

- **Regression coverage for adopted-done features.** From the map's *Tests & quality gate* section,
  for each adopted-done feature **not** already covered by existing tests, emit a `verify` task
  (`status: todo`, `traces_to` the feature) so `verify-feature` proves the pre-existing implementation
  against its acceptance criteria. This is what makes "adopted-done" real rather than assumed — a
  failure here files a `rework` task. (Where existing tests already cover a feature, no verify task is
  needed.)
- **Quality gate.** If the map shows no enforced gate (lint/format/type-check/test behind one
  `make check` + hooks — see `quality-gate.md`), emit a `setup` task to stand it up over the existing
  code, an early blocker for the rest.
- **Design-system reskin.** If `create-design-system` adopt mode logged a **token/reskin drift** in
  `.dev-skills/project-setup/design-system.md` (the realized system the user wants evolved — a `change`), emit
  a `rework` task `traces_to` the design system: apply the new `DESIGN.md` tokens to the affected
  surfaces. (No drift → the realized system is kept as-is, no task.)

Blockers are derived as in create mode, with one shortcut: an adopted-`done` task is a
**pre-satisfied** blocker, so a TARGET-only feature depending on an already-built entity is
immediately `ready`. Net result: the backlog holds **only** the gap — rework + new +
regression-coverage + gate — with matching features represented as `done`. Log the delta basis (which
drift entries produced which tasks) in `plan.summary.md`'s Forks / Decisions log.
