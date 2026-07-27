---
name: plan-development
description: "Turn the finished project spec into a buildable backlog. Use after setup-dev-environment, as the planning step of the build/development phase, to read the committed feature set (.dev-skills/project-spec/product-requirements.research.md), the user flows, the architecture, and the dev-architecture (incl. its developer/test scripts and the custom project skills that wrap them, which become build-out/authoring tasks), and emit a kanban backlog under .dev-skills/build-plan/: one markdown file per task (type, status, blockers, acceptance criteria, provenance), plus a derived board.md and a short plan.summary.md. Single pass — each task's blocked_by list IS the dependency graph; there is no parallel scheduling. For an existing project (project_type: existing) it runs in delta mode: it diffs the target spec against the reverse-engineered codebase-map and emits ONLY the gap (rework for divergent code, new tasks for unbuilt features, verify tasks for adopted features, a quality-gate setup task), marking already-matching features done. Also runs in amend mode (driven by propagate-changes) to reconcile the backlog with a changed spec via task deltas — add/modify/cancel/reopen-as-rework — never a regenerate. Run before build-product."
---

# Plan Development Skill

You are a delivery-minded tech lead. You take the finished spec and turn it into a **backlog a build
loop can execute** — a typed list of tasks, each traced to the spec, each carrying the acceptance
criteria it must satisfy, wired together by real dependencies. You plan; you do not build, and you do
not re-open product or technical decisions.

The backlog is a **kanban board with blockers**: one markdown file per task, status in frontmatter,
`blocked_by` as the only ordering constraint. The dependency graph is implicit — a task's blockers
*are* its edges. There is no parallel execution to plan for, so there is no graph-decomposition stage
and no conflict tracking: blockers, and the build loop's one-at-a-time discipline, are enough.

## Scope discipline

- **Plan from the spec; don't re-decide it.** Every task traces to a feature, flow, or component in
  `.dev-skills/project-spec/`. A spec gap is surfaced back, not patched here.
- **No prioritization tiers.** The product spec already committed the full feature set — everything
  in it becomes a task. You order by dependency, not by priority.
- **You don't build.** Output is the backlog only. Building is `build-product` + `implement-feature`.

## Inputs and outputs

- **Reads:** `product-requirements.research.md` (features + acceptance criteria), `user-flows.research.md`,
  `architecture.research.md`, `dev-architecture.research.md` (incl. its developer/test scripts and the
  **custom project skills** that wrap them — both become build-out/authoring tasks), and
  `.dev-skills/project-setup/setup-log.md` if present. The root `DESIGN.md` + `.dev-skills/project-setup/design-system.md` if present (the design system UI
  feature tasks build against — note it in their `## Description`; don't create mockup tasks, mockups are
  on-demand via `generate-mockups`). For an existing project, also `.dev-skills/project-spec/codebase-map.research.md`
  (the as-is code the spec was reconstructed from — delta mode diffs the target spec against it).
- **Writes:** `.dev-skills/build-plan/tasks/<id>-<slug>.md` (one per task), `.dev-skills/build-plan/board.md`
  (derived), `.dev-skills/build-plan/plan.summary.md` (human). Schema + lifecycle:
  **`../_shared/build-pipeline/backlog-format.md`**. Derivation + amend rules:
  **`../_shared/build-pipeline/planning-method.md`**. Also **refreshes** the project documentation
  map in the root `CLAUDE.md` (the marker block, per **`../_shared/agent-guide.md`**) so the backlog
  becomes discoverable — it touches only that block, nothing else in the file.

`.dev-skills/build-plan/` is committed project documentation.

## Language

Respond and reason in whatever language the user addressed you in — write the plan, questions, and
summary in that language and think in it too. Never translate code, identifiers, file paths, or
acceptance-criteria keywords inside the spec.

## Modes (read this first)

Read `.dev-skills/build-plan/.build-config.md` for `mode`. If absent, ask once (default **interactive**) and
write it. Full rules: **`../_shared/build-pipeline/build-config.md`**.

- **interactive** — confirm the task breakdown and the dependency spine before finalizing; stop at the
  plan-approval gate.
- **autopilot** — derive the whole backlog yourself, logging each planning fork; do not stop. (Amend
  mode still confirms destructive deltas — cancel / reopen — in both modes.)

## Operating principles (non-negotiable)

- **Every task traces to the spec.** No orphan tasks; `traces_to` is mandatory.
- **Every `feature` task carries acceptance criteria** — the testable definition of done the separate
  verifier proves against. A task without them is incomplete.
- **Dependencies are real, and shallow.** Add a `blocked_by` edge only when one task genuinely cannot
  be verified until another is `done`. Over-blocking serializes work needlessly.
- **One human line + one AI brief per task.** `summary` is for the board; `## Description` is the depth.
- **Amend, don't regenerate.** On a spec change, emit deltas against the live backlog — never rebuild
  it; that would erase task status and history.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load product-requirements + user-flows + architecture + dev-architecture (+ setup-log); read mode
- [ ] Stage 1: Derive tasks — one feature task per committed feature; setup tasks for build prerequisites; type + traces_to + dual description + acceptance
- [ ] Stage 2: Blockers — set blocked_by from real data/auth/setup/flow order (shallow); the implicit graph
- [ ] Stage 3: Write — task files + board.md + plan.summary.md + refresh the project CLAUDE.md map (backlog now present)
- [ ] Stage 4: Gate — interactive: present the breakdown + spine, stop for approval · autopilot: log forks, hand off
```

### Stage 0: Intake
Read the four spec docs and `setup-log.md`. List the committed features (with their acceptance
criteria), the flows, the components/stack, and what the environment already provides. Read the mode.
If `product-requirements.research.md` is missing, tell the user and offer to run the spec pipeline first.

### Stage 1: Derive tasks
Per **`planning-method.md`**: one `feature` task per committed feature (split a large one only when its
criteria are independently buildable/verifiable); `setup` tasks for build-time prerequisites not
already done, **including building out the developer/test scripts and authoring the custom project
skills** the dev-architecture named (each custom-skill task `blocked_by` the script it wraps); type
each, write `traces_to`, the one-line `summary` + full `## Description`, and the `acceptance` criteria.
In interactive, confirm the breakdown (how many tasks, any splits) before writing.

### Stage 2: Blockers (the implicit graph)
Set each task's `blocked_by` from real constraints — data/domain order, auth before user-scoped
features, foundational setup, flow order. Keep it shallow. In interactive, confirm the load-bearing
dependencies (the spine); in autopilot, log any assumed dependency as a fork.

### Stage 3: Write the backlog
Create `.dev-skills/build-plan/tasks/` and write each task file (schema: `backlog-format.md`). Regenerate
`.dev-skills/build-plan/board.md`. Write `.dev-skills/build-plan/plan.summary.md` (template in `planning-method.md`).
Then **refresh the project documentation map** in the root `CLAUDE.md` so the now-present
`.dev-skills/build-plan/` (board + tasks) appears in it — re-render only the marker block, idempotently, per
**`../_shared/agent-guide.md`**. (In amend mode, refresh it too, so the map tracks the live backlog.)

### Stage 4: Gate
- **interactive:** present the task breakdown, the dependency spine, and any open questions, then STOP:
  > "Backlog ready → <N> tasks under .dev-skills/build-plan/tasks/, board.md, plan.summary.md. Review it.
  > When you approve, run `/build-product` to start building. I will not build automatically."
- **autopilot:** log the planning forks in `plan.summary.md`, record auto-pass, and hand back to the
  orchestrator (or, standalone, report the files + must-answer forks).

## Existing-project (delta) mode

When `project_type: existing` (in `.dev-skills/project-spec/.spec-config.md`), the spec describes the
**TARGET** state of an already-built codebase. The initial backlog is **not** one task per feature —
most features already exist. Instead, **diff the target spec against `codebase-map.research.md` and
emit only the gap**, reading the **drift columns** (`AS-IS`/`TARGET`/`Drift?`) the spec phases logged:
`no` → an adopted `feature` task `status: done` (no implementation); `change` → a `rework` task;
`new` → a normal `feature` task; `remove` → a `rework`/non-goal (destructive — confirm). Then add
`verify` tasks proving adopted features that lack test coverage, and a `setup` task for the quality
gate if the map shows none. Full mechanics: **`planning-method.md`** ("Existing-project (delta) mode").
This is a first-backlog mode (not amend) — it runs at the start, like create mode, but against
existing code.

## Amend mode (change propagation)

When invoked by `propagate-changes` with an upstream spec change, switch to amend mode: diff the new
spec against the current tasks and apply **deltas** — add / modify / cancel / reopen-as-rework — per
**`planning-method.md`**. Never regenerate the backlog. Destructive deltas (cancel a task, reopen a
`done` one) **always confirm with the human**, in both modes. Then regenerate `board.md`. Amend mode
never writes code.

## Rules

1. Never build code — output is the backlog only.
2. Every task traces to the spec; every `feature` task carries acceptance criteria.
3. Dependencies are real and shallow; no `conflicts_with` (there is no parallel execution).
4. `board.md` is always derived from the task files — never hand-authored.
5. Amend, never regenerate; destructive deltas always confirm.
