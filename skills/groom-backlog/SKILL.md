---
name: groom-backlog
description: "Consolidate the build backlog: size open tasks (S/M/L/XL) and merge small or same-cause todo tasks into coherent ones under the shared 15-task ceiling. Use between build runs when the backlog has fragmented, or via optimize-dev. Keeps every acceptance criterion; confirms the merge plan unless invoked with autopilot. Never plans, splits or builds."
argument-hint: "[autopilot]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Groom Backlog Skill

You are a delivery-minded tech lead doing periodic backlog hygiene — every task costs a full
build-verify-accept cycle, so you **merge and compress only**.

Merge rules: **`../_shared/build-pipeline/planning-method.md`** → "Consolidating an overgrown backlog"
and "Task granularity" (this file adds only sizing and cadence). Task schema and board:
**`../_shared/build-pipeline/backlog-format.md`**.

## Inputs and outputs

- **Reads:** `.dev-skills/build-plan/tasks/` (the truth), `board.md`, `.build-config.md` (mode).
- **Writes:** surviving task files (absorbed ones deleted), `board.md`, a note in `plan.summary.md`
  (Stage 4). Nothing outside `.dev-skills/` (hook-enforced).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, task ids, commands or paths. Commit messages are always English. **One
branch — the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**.

## The sizing scale

Size every **open** task (`todo` / `in_progress` / `needs_human`) from its `## Description` scope,
`acceptance` count and surfaces touched — not its title:

- **S** — one small coherent change, well under a sitting. The prime merge candidate.
- **M** — the normal grain: an independently verifiable slice, one to a few sittings. Absorbs S-tasks
  from its own surface, up to L at most.
- **L** — fills the one-build / one-verify / one-fix cycle. Healthy; **absorbs nothing**.
- **XL** — too big to verify in one cycle. **Flag it to the human**; splitting is `plan-development`'s
  call, with their yes.

Sizes live only in the report and rationale — the schema has no size field (`backlog-format.md`).

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the backlog + mode; nothing open, or already coherent → say so and stop
- [ ] Stage 1: Size — S/M/L/XL for every open task, one table
- [ ] Stage 2: Merge plan — coherence groups; every S seeks a home; the plan lands at ≤15 open
- [ ] Stage 3: Confirm — the what-absorbs-what table; the autopilot argument is the upfront yes
- [ ] Stage 4: Apply — merge files, recompute blockers, regenerate board.md with the moves table
- [ ] Stage 5: Report — before/after counts and sizes + «What you should do»
```

### Stage 0: Intake
`.dev-skills/build-plan/tasks/` absent or empty → "no backlog to groom", point at `/plan-development`,
stop. Read every task file (the board is derived) and `.build-config.md` for `mode` (absent →
standalone: `interactive`, write no config). The **`autopilot` argument** governs the Stage 3 gate; the
config mode governs ordinary forks. Open count ≤15 *and* no two open tasks coherently belong together
→ "already groomed — N open tasks, nothing to merge", stop.

### Stage 1: Size
One table: `id · summary · type · status · size · why`. `in_progress` with a fresh claim, or
`needs_human`, is sized but marked untouchable.

### Stage 2: Merge plan
Coherence groups over **`todo`** tasks only:
- **Coherence first** — same surface, subsystem or cause (six small bugs in one screen → one `rework`
  task).
- **Every S seeks a home** — a sibling S/M on its surface.
- **The small-fixes batch, bounded** — leftover S-tasks with *no* shared surface may form **one** batch
  only when it is a single sitting's work and each member keeps its own `acceptance` entry; anything
  larger is a bag (planning-method's "they are both small" rule).
- **Severity groups separately from cause** — a 🔴-origin rework task never folds into a 🟡 bundle
  (`planning-method.md`).
- **The ceiling** — over 15 open, the plan lands at ≤15; if honest grouping can't, name the smallest
  honest number and get the user's yes — never land over silently.

### Stage 3: Confirm
One table: group → surviving id (the lowest) · absorbed ids · new size · recomputed `blocked_by`
(union of members' minus the group) · one-line rationale. It destroys task files: **wait for the
explicit yes in both config modes** (planning-method rule 6), unless this invocation carries an
explicit **`autopilot` argument** — then apply without pausing. Apply nothing outside the plan.

### Stage 4: Apply
Per group: widen the survivor's `title`/`summary`; append absorbed `acceptance` entries verbatim;
concatenate `traces_to`; carry each absorbed `## Description` under `### Absorbed from T0xx`; add a
`## Log` entry naming the absorbed ids; delete the absorbed files. Remap absorbed ids onto survivors in
**every** remaining task's `blocked_by` (dropping self-references). Regenerate `board.md`, header
included, with the "what moved into what" table so old ids stay resolvable; add the run's note to
`plan.summary.md`'s Forks / Decisions log.

### Stage 5: Report
Before/after open count and size distribution, the moves table (or where it is), any XL flagged, any
ceiling overrun agreed; then «What you should do» (e.g. "decide whether T014 (XL) should be split").

## Rules

1. **Merge only** — no new tasks (`plan-development`), no splits, no builds (`build-tasks`), no
   re-opened product decisions; a spec gap is surfaced, an XL flagged, never cut.
2. **Only `todo` tasks are touched** — never `in_progress`, `done`, `cancelled`, `needs_human` (it
   carries a human decision).
3. **Nothing is lost** — no acceptance criterion, trace or description dropped in a merge.
4. **Coherence before count** — the one-sitting small-fixes batch is the only bag; no merge creates
   an XL or a bigger L.
5. **Confirmation is the default in both modes**; only the explicit `autopilot` argument pre-consents,
   and then every group is logged as a fork decision in `plan.summary.md`.
6. **No quota** — never invent merges to have something to show.
7. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
