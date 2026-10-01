# Planning method (shared — build pipeline)

How `plan-development` turns the spec into the kanban backlog and **amends** it when the spec changes.
Schema, lifecycle and board: **`backlog-format.md`**; this file is about *deriving* tasks. Single pass:
the blockers a task carries *are* the graph — no separate decomposition stage.

## Inputs (read, never re-decide)

- `.dev-skills/project-spec/product-requirements.research.md` — the committed feature set; each feature has
  ≥1 behavioral **acceptance criterion** and a "serves (validated need)" trace. These become tasks.
- `.dev-skills/project-spec/user-flows.research.md` — flows + per-flow criteria: sharpen task criteria,
  surface cross-feature ordering.
- `.dev-skills/project-spec/architecture.research.md` + `dev-architecture.research.md` — components and
  local stack, to size tasks and seed `setup` tasks and dependencies (auth before user-scoped
  features); also the **developer/test scripts** and **custom project skills** to build out.
- `.dev-skills/project-setup/setup-log.md` (if present) — what the environment already has; don't
  re-create it as `setup` tasks.
- The root `DESIGN.md` + `.dev-skills/project-setup/design-system.md` (if present) — referenced in a UI
  task's `## Description`. Never emit "mockup" tasks — mockups are on-demand (`generate-mockups`).

Planning never re-opens product or technical decisions; a spec gap is surfaced back, not invented.

## Consolidating an overgrown backlog

When the **open** count has passed the ceiling — or the human asks for fewer, bigger tasks — merge
instead of re-planning. Destructive to task files, so it confirms in both modes.

1. **Only `todo` tasks are eligible.** Never touch `in_progress` (a claim may be held), `done`,
   `cancelled`, or `needs_human` (it carries a human decision and is never merged away).
2. **Group by coherence, not by count** — same surface, subsystem or cause. A group whose only link is
   "they are both small" is a bag, not a task.
3. **Nothing is lost.** Members' `acceptance` entries move into the survivor **verbatim**, `traces_to`
   are concatenated, each `## Description` is carried over under a sub-heading. Dropping a criterion
   is a scope change, not a tidy-up.
4. **Blockers are recomputed**, not copied: the survivor's `blocked_by` is the union of the members',
   minus members of the same group.
5. **Write down where everything went.** The board carries a "what moved into what" table; each
   survivor's `## Log` names the ids it absorbed, so old ids stay resolvable after their files go.
6. **Confirm the merge plan before writing** — groups and what each absorbs — in both modes.

## Task granularity — coarse, at most 15 tasks

Tasks are **deliberately large**: **no more than 15 tasks**, and that ceiling is the sizing
instrument — pick the grain that fits the product into 15. 40 micro-tasks is a planning failure.

- **Size top-down.** Count the committed features first: roughly ≤15 → one task per feature; more → one
  per **coherent, independently verifiable slice** (a screen with its CRUD, an auth flow end to end,
  one integration with its config and error handling), carrying **all** its features' criteria.
- **Re-impose the ceiling.** The backlog grows after planning (audit rework, adhoc requests, release
  findings); **consolidation is an operation, not a favour** — "Consolidating an overgrown backlog".
- **Never split for tidiness** — only when a feature's criteria are independently buildable *and*
  verifiable **and** the backlog still fits under 15. "Backend then frontend", "model, API, UI", "one
  task per field / endpoint / test" are steps inside `## Description`.
- **Prefer depth over count.** Sequencing inside one deliverable belongs in `## Description`;
  `blocked_by` orders *between* deliverables.
- **`setup`, dev-script and custom-skill tasks count toward the 15** — fold all dev/test scripts into
  one build-out task and all custom skills into one authoring task when room is needed.
- **If it doesn't fit, never silently exceed.** Name the smallest honest number and get the user's yes
  (interactive) or log it as a planning fork in `plan.summary.md` (autopilot).

The ceiling counts **open** tasks (`todo` / `in_progress` / `needs_human`); `done` and `cancelled`
don't consume it.

### This applies to everyone who files a task, not just planning

The release audits (`audit-security`, `audit-performance`, `audit-product`), `refactor` and
`write-tests` file `rework` tasks; `run-task` files `adhoc` ones. **One backlog, one ceiling, one
grain** — all follow this section and share the same 15 open tasks.

- **One task per coherent fix, not one per finding.** Findings on the same surface, with a shared cause,
  or fixable by one agent in one sitting are **one** `rework` task — six missing authorization checks
  across five routes is one task ("enforce ownership on the document routes"). **Nothing is dropped**:
  each finding becomes its own `acceptance` entry with its evidence link.
- **Split only when one sitting can't hold it** — different subsystems, different fixes, or one part
  blocked on something the other isn't. "Reported separately" or "different finding ids" are not
  reasons.
- **Severity groups separately from cause.** A 🔴 is never folded into a 🟡 bundle to save a slot; it
  gets its own task so it can be fixed and re-audited alone.
- **At the ceiling, say so — never file silently past it**: smallest honest number, the user's yes
  (interactive) or a logged fork (autopilot).

## Deriving tasks (create mode)

1. **One `feature` task per committed feature** within the 15-task ceiling; beyond it, one per group of
   related features (grain and splits: "Task granularity"). Carry every covered feature's criteria into
   `acceptance`, sharpened with the relevant flow criteria.
2. **`setup` tasks** for build-time prerequisites features depend on and not already done (per
   `setup-log.md`) — a migration baseline, a seed fixture, an auth scaffold. Few: most setup is
   `setup-dev-environment`'s job.
3. **Type every task** (`setup` | `feature` | `verify`) and write **`traces_to`** — the spec section(s)
   it comes from. No orphans.
4. **Dual description.** `summary` = one human line; `## Description` = the full AI brief (what to
   build, relevant spec sections, constraints, design notes).
5. **Acceptance** — the behavioral criteria `verify-feature` proves against. A feature task without
   them is incomplete.
6. **Developer/test-script tasks.** Normally **one task for the whole set** (`setup` or `feature`,
   `traces_to` the dev-scripts section) to **build out fully** the scripts `dev-architecture.research.md`
   specifies and `setup-dev-environment` scaffolded. They widen the verification loop: order the
   foundational ones early.
7. **Custom-skill tasks.** One `setup` task (one per skill only if the ceiling allows) to **author
   fully** the project-local skills in `dev-architecture.research.md`'s *Custom project skills* table
   (`/run-integration-tests`, `/verify-flow`, `/reset-env`; skeletons under `.claude/skills/`),
   `traces_to` the custom-skills section, each **`blocked_by` the script build-out task(s) it wraps**.
   They complement `verification.md`; one that merely restates `verify-feature` doesn't belong.

## Setting blockers (the implicit graph)

Set `blocked_by` to the ids that must be `done` first, from **real** constraints:

- **Data/domain order** — a feature that reads an entity depends on the task that creates it.
- **Auth/identity** — anything needing a logged-in user depends on the auth task.
- **Foundational setup** — features depend on the `setup` tasks that establish their substrate.
- **Flow order** — `user-flows.research.md` often implies one (create before edit before share).

Keep the graph shallow: an edge only where one task cannot be verified until another is `done`. There
is **no `conflicts_with`** (no parallel waves) — blockers are the only ordering tool.

## Output

Write each task to `.dev-skills/build-plan/tasks/<id>-<slug>.md` (schema: `backlog-format.md`), regenerate
`.dev-skills/build-plan/board.md`, and write `.dev-skills/build-plan/plan.summary.md`:

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

Log every planning fork (a split, an assumed dependency) in a `## Forks / Decisions log` in
`plan.summary.md`'s companion or inline — interactive asks; autopilot decides and records
(`build-config.md`).

## Amend mode (change propagation)

Entered by re-running `plan-development` on an existing backlog after a spec change. **Never
regenerate** — that destroys status and history; diff the new spec against the tasks and emit
**deltas**:

- **Add** — a new feature/flow → a new `todo` task (blockers + acceptance), next free id. The ceiling
  holds over **open** tasks: if the feature fits an open task's slice, extend that task (a **modify**
  delta); if the open count would pass 15, say so and confirm the count with the user.
- **Modify** — a changed feature → update the task's `## Description` / `acceptance` / `summary` in
  place and append a `## Log` note; `traces_to` finds which tasks a changed section touches.
- **Cancel** — a feature removed from the spec → `status: cancelled` (terminal).
- **Reopen as rework** — a change that invalidates `done` work → set it back to `todo` (or add a new
  rework task referencing it), with a `## Log` note on what changed and why. Built-but-now-wrong code
  becomes an explicit rework task, never a silent revert.

**Cancel and reopen are destructive — always confirm with the human**, both modes (`build-config.md`).
Then regenerate `board.md`. Amend mode never builds code; the rebuild is a normal `build-tasks` run.

## When the repo already has code (delta planning)

With working code, plan only the gap. Read **the spec's `## Divergences (code vs intended)` sections**
(each line marked `change` / `remove` / `not built yet`) and **the code itself** — a feature the spec
assumes but that isn't really implemented is `not built yet`, whatever the table says. Emit per line:

- **`change` (built but divergent)** → a **`rework`** task, `traces_to` the spec section; its
  `## Description` states what exists now and the target.
- **`not built yet`** → a normal `feature` task, as in create mode.
- **`remove` (built, not wanted)** → a `rework` task ("remove <feature>") or a recorded non-goal.
  **Destructive — always confirm with the human**, both modes.

A feature that works and matches the intent gets a `feature` task with **`status: done`** and a
`history` note `"pre-existing"`, so dependents see the blocker satisfied. That "done" is **provisional**
(reading code is not running it): each such feature **not** covered by tests gets a `verify` task
(a failure files a `rework` task). Plus two gap-closers:

- **Quality gate.** No enforced gate (lint/format/type-check behind `make check-fast` + a hook, a scoped
  test run, the full suite behind `make check` — `quality-gate.md`)? A `setup` task to stand it up — an
  early blocker for everything else.
- **Design-system reskin.** `setup-dev-environment` recorded that the realized design system is to be
  evolved → a `rework` task applying the new `DESIGN.md` tokens to the affected surfaces.

Blockers as in create mode; a pre-existing `done` task is a **pre-satisfied** blocker. Log which
divergence produced which task in `plan.summary.md`'s Forks / Decisions log. Recorded-`done` tasks don't
count toward the ceiling; group one surface's divergences into one `rework` task (and the pre-existing
features' `verify` tasks into a few end-to-end passes), not one task per line.
