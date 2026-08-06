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

Planning never re-opens product or technical decisions. A gap in the spec is surfaced back, not
invented here.

## Task granularity — coarse, at most 15 tasks

Tasks are **deliberately large**. The whole backlog holds **no more than 15 tasks**, and that ceiling
is the sizing instrument: pick the grain that fits the product into 15, not the grain that feels
natural feature by feature. A backlog of 40 micro-tasks is a planning failure, not thoroughness — it
buries the build loop in bookkeeping, multiplies verification rounds over slices too thin to be
verified on their own, and hides the real build order in noise.

- **Size top-down.** Count the committed features first, then choose the grain. Roughly ≤15 features →
  one task per feature is fine. More than that → group related features into one task per **coherent,
  independently verifiable slice** (a whole screen with its CRUD, an auth flow end to end, one
  integration including its config and error handling), and carry **all** the grouped features'
  acceptance criteria into that task's `acceptance` — grouping tasks never drops criteria.
- **Never split for tidiness.** A split is justified only when a feature's acceptance criteria are
  independently buildable *and* verifiable **and** the backlog still fits under 15. "Backend then
  frontend of the same thing", "the model, then the API, then the UI", "one task per field / per
  endpoint / per test" are steps inside a task's `## Description`, not tasks.
- **Prefer depth over count.** Sequencing that lives inside one deliverable belongs in the task's
  `## Description`; `blocked_by` is for order *between* deliverables. Splitting a task just to express
  an internal order spends the budget for nothing.
- **`setup`, dev-script, and custom-skill tasks count toward the 15 too.** Fold them together — all
  dev/test scripts into one build-out task, all custom project skills into one authoring task — when
  the feature tasks need the room.
- **If it genuinely doesn't fit**, never silently exceed. Say so: name the smallest honest number the
  committed scope reaches, and either get the user's yes for that count (interactive) or log it as a
  planning fork in `plan.summary.md` (autopilot).

The ceiling counts **open** tasks (`todo` / `in_progress` / `needs_human`); `done` and `cancelled`
tasks are history and don't consume it.

### This applies to everyone who files a task, not just planning

`plan-development` is not the only writer of task files. The release audits (`audit-security`,
`audit-performance`, `audit-product`), `refactor` and `write-tests` file `rework` tasks for what they
find; `run-task` files an `adhoc` task from a free-form request. **One backlog, one ceiling, one
grain** — they all follow this section, and they all count against the same 15 open tasks.

- **One task per coherent fix, not one per finding.** Findings that live in the same surface, share a
  cause, or would be fixed in one sitting by one agent are **one** `rework` task. Six missing
  authorization checks across five routes is one task ("enforce ownership on the document routes"),
  not six. **Nothing is dropped by grouping**: every finding becomes an entry in that task's
  `acceptance` with its own evidence link, so the fix is still verified finding by finding.
- **Split only when a single sitting genuinely can't hold it** — different subsystems, different
  fixes, or one part blocked on something the other isn't. "They were reported separately" and "they
  have different finding ids" are not reasons.
- **Severity groups separately from cause.** A 🔴 is not folded into a 🟡 bundle just to save a slot:
  the blocker gets its own task so it can be fixed and re-audited on its own.
- **At the ceiling, say so — never file silently past it.** If the honest grouping still doesn't fit
  under 15 open tasks, name the smallest honest number and get the user's yes (interactive) or log it
  as a fork (autopilot). A backlog of 40 findings-as-tasks is how a release phase buries the three
  things that actually block the cut.

## Deriving tasks (create mode)

1. **One `feature` task per committed feature** when the feature set fits the 15-task ceiling above;
   beyond that, one task per group of related features (occasionally split a large feature into a few
   tasks when its acceptance criteria are independently buildable/verifiable *and* the backlog still
   fits). Carry every covered feature's acceptance criteria into the task's `acceptance`, sharpened
   with the relevant flow criteria.
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
   skeletons are scaffolded by `setup-dev-environment`, so add a task to **build them out fully** (type
   `setup` or `feature`, `traces_to` the dev-architecture dev-scripts section) — normally **one task
   for the whole set**, split only when the ceiling leaves room. They widen the agent's
   verification loop, so blockers usually put the foundational ones early.
7. **Custom-skill tasks.** `dev-architecture.research.md`'s *Custom project skills* table names the
   project-local Claude Code skills that wrap those scripts/harness into named verification jobs
   (`/run-integration-tests`, `/verify-flow`, `/reset-env`); their skeletons are scaffolded by
   `setup-dev-environment` under `.claude/skills/`, so add a `setup` task to **author them fully**
   (`traces_to` the dev-architecture custom-skills section) — one task per skill only when the ceiling
   allows, otherwise one authoring task for the whole set. Each is **`blocked_by` the
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

After a spec change, re-running `plan-development` against an existing backlog puts it in
**amend mode** with the upstream change. Do **not** regenerate the backlog — that would destroy task
status and history. Instead, diff the new spec against the current tasks and emit **deltas**:

- **Add** — a new feature/flow → a new `todo` task (with blockers + acceptance), appended with the
  next free id. The 15-task ceiling holds in amend mode too, counted over the **open** tasks: when a
  new feature belongs to an existing open task's slice, extend that task (a **modify** delta) instead
  of adding a thirteenth, fourteenth, fifteenth one. If the addition genuinely pushes the open count
  past 15, say so and confirm the count with the user rather than growing the backlog silently.
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
backlog; the actual rebuild happens later through a normal `build-tasks` run.

## When the repo already has code (delta planning)

If the project already has working code, the initial backlog is **not** "one task per feature" — most
of them exist. Plan only the gap. Two inputs, both already available:

- **the spec's `## Divergences (code vs intended)` sections** — what the phases found different
  between the code and the intent, each marked `change` / `remove` / `not built yet`;
- **the code itself** — read it to confirm what genuinely works before planning anything. A feature
  the spec assumes exists but that isn't really implemented is a `not built yet`, whatever the
  divergence table says.

Emit per line:

- **`change` (built but divergent)** → a **`rework`** task, `traces_to` the spec section; its
  `## Description` states what exists now and what the target is.
- **`not built yet`** → a normal `feature` task, exactly as in create mode.
- **`remove` (built, not wanted)** → a `rework` task ("remove <feature>") or a recorded non-goal.
  **Destructive — always confirm with the human**, in both modes.

A feature that already works and matches the intent gets a `feature` task with **`status: done`** and
a `history` note `"pre-existing"` — no implementation work, but dependent tasks see their blocker
satisfied and the traceability holds. That "done" is **provisional**: reading code is not running it,
so for each such feature **not** already covered by tests, add a `verify` task so `verify-feature`
proves it against its acceptance criteria (a failure there files a `rework` task).

Then the two gap-closers:

- **Quality gate.** No enforced gate (lint/format/type-check behind `make check-fast` + a hook, a
  scoped test run, and the full suite behind `make check` —
  see `quality-gate.md`)? Emit a `setup` task to stand it up over the existing code — an early blocker
  for everything else.
- **Design-system reskin.** If `setup-dev-environment` recorded that the realized design system is to
  be evolved, emit a `rework` task to apply the new `DESIGN.md` tokens to the affected surfaces.

Blockers derive as in create mode, with one shortcut: a pre-existing `done` task is a **pre-satisfied**
blocker. Net result: the backlog holds only the gap — rework + new + regression coverage + gate. Log
which divergence produced which task in `plan.summary.md`'s Forks / Decisions log.

The ceiling applies here as well, and it is easier to respect: the recorded-`done` tasks don't count,
so the 15 are all gap work. Group divergences that live in the same surface into one `rework` task
(and the pre-existing features' `verify` tasks into a few end-to-end passes) rather than filing one
task per line of the divergence table.
