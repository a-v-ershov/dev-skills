---
name: plan-development
description: "Turn the spec into a kanban backlog under .dev-skills/build-plan/: coarse tasks (at most 15 open), each traced to the spec with acceptance criteria. Use after setup-dev-environment, before build-tasks. With existing code it plans only the gap; after a spec change it amends via task deltas; 'consolidate' merges the open backlog under the ceiling."
argument-hint: "[consolidate]"
---

# Plan Development Skill

You are a delivery-minded tech lead. You turn the finished spec in `.dev-skills/project-spec/` into a
**backlog a build loop can execute**: typed tasks, each traced to the spec and carrying its acceptance
criteria, wired by real dependencies. You plan — building is `build-tasks` + `implement-feature` — and
never re-open product or technical decisions; a spec gap is surfaced back, not patched here. **No
prioritization tiers**: the whole committed feature set becomes tasks, ordered by dependency.

The backlog is a **kanban board with blockers**: one markdown file per task, status in frontmatter,
`blocked_by` the only ordering constraint — the blockers *are* the graph; no parallel execution, no
graph-decomposition stage.

## Inputs and outputs

- **Reads:** `product-requirements.research.md` (features + acceptance criteria),
  `user-flows.research.md`, `architecture.research.md`, `dev-architecture.research.md`,
  `.dev-skills/project-setup/setup-log.md` if present, the root `DESIGN.md` +
  `.dev-skills/project-setup/design-system.md` if present (UI feature tasks build against it — note it
  in their `## Description`; no mockup tasks, mockups are on demand via `generate-mockups`), and the
  existing code, if any (delta mode).
- **Writes:** `.dev-skills/build-plan/tasks/<id>-<slug>.md` (one per task),
  `.dev-skills/build-plan/board.md` (derived), `.dev-skills/build-plan/plan.summary.md` (human) —
  committed project documentation. Schema + lifecycle:
  **`../_shared/build-pipeline/backlog-format.md`**; derivation + amend rules:
  **`../_shared/build-pipeline/planning-method.md`**. Also **refreshes** the project documentation map
  in the root `CLAUDE.md` (the marker block only, per **`../_shared/agent-guide.md`**).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths or acceptance-criteria keywords inside the spec. Commit
messages are always English. **One branch — the current one** (normally `main`): never branch, switch
or open a worktree unless the user explicitly asked in this session — **`../_shared/git-workflow.md`**.

## Modes (read this first)

Read `mode` from `.dev-skills/build-plan/.build-config.md`; if absent, ask once (default
**interactive**) and write it (**`../_shared/build-pipeline/build-config.md`**).

- **interactive** — confirm the breakdown and the dependency spine; stop at the plan-approval gate.
- **autopilot** — derive the whole backlog yourself, logging each planning fork; do not stop
  (destructive amend deltas still confirm).

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load product-requirements + user-flows + architecture + dev-architecture (+ setup-log); read mode
- [ ] Stage 1: Derive tasks — coarse slices, ≤15 tasks total; setup tasks for build prerequisites; type + traces_to + dual description + acceptance
- [ ] Stage 2: Blockers — set blocked_by from real data/auth/setup/flow order (shallow); the implicit graph
- [ ] Stage 3: Write — task files + board.md + plan.summary.md + refresh the project CLAUDE.md map (backlog now present)
- [ ] Stage 4: Gate — interactive: present the breakdown + spine, stop for approval · autopilot: log forks, hand off
```

### Stage 0: Intake
Read the four spec docs and `setup-log.md`. List the committed features (with acceptance criteria),
the flows, the components/stack and what the environment already provides. Read the mode. No
`product-requirements.research.md` → say so and offer the spec pipeline first.

### Stage 1: Derive tasks
Per **`planning-method.md`** → "Task granularity": count the committed features, then pick the grain
that fits them into **≤15 tasks** — one `feature` task per feature when the set is small enough,
otherwise one per group of related features (split only when the criteria are independently
buildable/verifiable *and* the backlog still fits). Never split a feature into model / API / UI /
per-field steps; internal ordering goes in `## Description`. Add `setup` tasks for build-time
prerequisites not already done, **including building out the developer/test scripts and authoring the
custom project skills** the dev-architecture named (each custom-skill task `blocked_by` the script it
wraps) — they count toward the 15; fold them together when the feature tasks need the room. Type each
task; write `traces_to`, the one-line human `summary`, the full `## Description` (the AI brief) and the
`acceptance` criteria (every grouped feature's, none dropped). Interactive: confirm the breakdown
(count, grouping, splits) before writing.

**Leave room, and say what you left:** the release audits, `refactor`, `write-tests` and adhoc
requests file into the same 15 later (`planning-method.md`). State in `plan.summary.md` how many slots
the plan uses.

### Stage 2: Blockers (the implicit graph)
Set `blocked_by` from real constraints only — data/domain order, auth before user-scoped features,
foundational setup, flow order. Interactive: confirm the load-bearing dependencies
(the spine); autopilot: log each assumed dependency as a fork.

### Stage 3: Write the backlog
Create `.dev-skills/build-plan/tasks/` and write each task file (schema: `backlog-format.md`).
Regenerate `.dev-skills/build-plan/board.md` with its **Reconciled with spec** header line (current
HEAD sha + date — the anchor `build-tasks` uses to detect a spec that moved past the plan). Write
`.dev-skills/build-plan/plan.summary.md` (template in `planning-method.md`). Refresh the project
documentation map in the root `CLAUDE.md` so `.dev-skills/build-plan/` appears — marker block only,
idempotently; in amend mode too.

### Stage 4: Gate
- **interactive:** present the task breakdown, the dependency spine and any open questions, then STOP:
  > "Backlog ready → <N> tasks under .dev-skills/build-plan/tasks/, board.md, plan.summary.md. Review it.
  > When you approve, run `/build-tasks` to start building. I will not build automatically."
- **autopilot:** log the planning forks in `plan.summary.md`, record auto-pass, hand back to the
  orchestrator (standalone: report the files + must-answer forks).

## Existing-project (delta) mode

With working code, plan **only the gap** — most features already exist. From the spec's
`## Divergences (code vs intended)` sections plus a read of the code to confirm what works: `change` →
a `rework` task, `not built yet` → a normal feature task, `remove` → a confirmed removal, already
working and matching → recorded `done` (with a `verify` task where no test covers it). Method:
**`../_shared/build-pipeline/planning-method.md`** → "When the repo already has code".

## Consolidate mode (`/plan-development consolidate`)

With the argument `consolidate` — or whenever the human asks for fewer, bigger tasks — merge the
**open** backlog back under the ceiling instead of planning anything new
(**`../_shared/build-pipeline/planning-method.md`** → "Consolidating an overgrown backlog"): only
`todo` tasks are eligible; group by coherence; every acceptance criterion moves across verbatim;
blockers are recomputed; the board records what moved into what; the merge plan is confirmed before
anything is written, in both modes. No code touched, no spec read. **Offer it unasked** when a run
leaves more than 15 open tasks.

## Amend mode (change propagation)

After a spec change, diff the new spec against the current tasks and apply **deltas** — add / modify /
cancel / reopen-as-rework — per **`planning-method.md`**; never regenerate (it erases status and
history). Destructive deltas (cancel, reopen a `done` task) **always confirm**, in both modes. Then
regenerate `board.md`.

The **release phase files its findings** this way too (`audit-*`, `refactor`, `write-tests`): **one
`rework` task per coherent fix, not one per finding** — findings sharing a surface or a cause become
one task with each finding as its own `acceptance` entry (a 🔴 keeps its own task); prefer extending an
existing open task whose slice covers the finding.

## Rules

1. Never write code — output is the backlog only, in every mode.
2. **At most 15 open tasks in the backlog**, in every mode (create, amend, delta, consolidate),
   shared with every skill that files tasks. One task per coherent piece of work. Exceeding it needs
   the user's explicit yes — never silently.
3. Every task traces to the spec (`traces_to` mandatory); every `feature` task carries acceptance
   criteria.
4. A `blocked_by` edge only when one task cannot be verified until another is `done`; keep it shallow;
   no `conflicts_with`.
5. `board.md` is always derived from the task files — never hand-authored.
6. Amend, never regenerate; destructive deltas always confirm.
7. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
