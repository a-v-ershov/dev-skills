---
name: groom-backlog
description: "Consolidate the build backlog: size every open task, merge small or same-cause tasks into coherent larger ones, and bring the open count back under the shared 15-task ceiling. Use between build runs when the backlog has fragmented, or via optimize-dev. Only todo tasks are touched, no acceptance criterion is lost, and the merge plan is confirmed before writing unless invoked with autopilot. Works on .dev-skills/build-plan/ only; it merges — it never plans, splits, or builds."
argument-hint: "[autopilot]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Groom Backlog Skill

You are a delivery-minded tech lead doing periodic backlog hygiene. A backlog is a working instrument,
not an archive: every task on it costs a full build-verify-accept cycle of bookkeeping, so a board of
many small tasks buries the build loop in overhead and hides the real build order in noise. Field
data behind the ceiling: two projects planned at 15 tasks finished at 68 and 69, with the owner asking
four separate times to merge them back down. Grooming is that merge, done on schedule instead of on
complaint.

You **merge and compress only**. You never plan new work (`plan-development`), never split a task on
your own initiative, never build (`build-tasks`), and never re-open product decisions — a gap in the
spec is surfaced, not fixed here.

The merge rules are shared, not yours to reinvent:
**`../_shared/build-pipeline/planning-method.md`** → "Consolidating an overgrown backlog" and "Task
granularity" (this file adds only the sizing scale and the grooming cadence). Task schema and board:
**`../_shared/build-pipeline/backlog-format.md`**.

## Inputs and outputs

- **Reads:** `.dev-skills/build-plan/tasks/` (the truth), `board.md`, `.build-config.md` (mode).
- **Writes:** the surviving task files, removal of the absorbed ones, a regenerated `board.md` (with
  the "what moved into what" table), and a note in `plan.summary.md`'s Forks / Decisions log. Nothing
  outside `.dev-skills/` — enforced by a write-scope hook, not just by this sentence.

## Language & git

Respond and reason in the user's language — write the sizing table, the merge plan, and the report in
that language and think in it too. Never translate code, identifiers, task ids, commands, or paths.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## The sizing scale

Size every **open** task (`todo` / `in_progress` / `needs_human`) from its `## Description` scope,
its `acceptance` count, and the surfaces it touches — not from its title:

- **S** — one small coherent change; well under a single sitting. The prime merge candidate.
- **M** — the normal coarse grain: an independently verifiable slice, one to a few sittings. Can
  absorb S-tasks from its own surface.
- **L** — fills the one-build / one-verify / one-fix cycle to the brim. Healthy, but **absorbs
  nothing** — a merge must never create a bigger L.
- **XL** — too big to verify in one cycle. **Flag it to the human** (splitting is a planning decision
  for `plan-development`, and only with their yes); never split it yourself.

Sizes live in the report and the merge rationale only. The task schema has no size field and grooming
does not invent one — frontmatter stays exactly `backlog-format.md`.

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
Locate `.dev-skills/build-plan/tasks/`; absent or empty → "no backlog to groom", point at
`/plan-development`, stop. Read every task file (the files are the truth; the board is derived) and
`.build-config.md` for `mode` (absent → this is a standalone run; default `interactive`, don't write
config for a read-mostly pass). The **`autopilot` argument** governs the confirmation gate in Stage 3;
the config mode governs ordinary forks. Count open tasks. **Grooming has no quota**: if the open count
is at or under 15 *and* no two open tasks coherently belong together, report "already groomed — N open
tasks, nothing to merge" and stop. Do not invent merges to have something to show.

### Stage 1: Size
One table: `id · summary · type · status · size · why`. Anything `in_progress` with a fresh claim, or
`needs_human`, is sized for the picture but marked untouchable.

### Stage 2: Merge plan
Build coherence groups over the **`todo`** tasks only (never `in_progress`, `done`, `cancelled`, or
`needs_human` — a `needs_human` task carries a human decision and is never merged away):

- **Coherence first** — same surface, same subsystem, same cause. Six small bugs in the same screen
  are one `rework` task; three config chores in the same pipeline are one `setup` task.
- **Every S seeks a home** — into a sibling S/M on its surface. An M absorbs up to L at most; L and
  XL absorb nothing.
- **The small-fixes batch, bounded** — leftover S-tasks with *no* shared surface may form **one**
  batch task only when the whole batch is a single sitting's work and each member keeps its own
  `acceptance` entry. That bound is what separates a deliverable someone would fix in one go from a
  bag; planning-method's "they are both small is a bag" rule still holds for anything larger.
- **Severity groups separately from cause** — a 🔴-origin rework task is never folded into a 🟡 bundle
  just to save a slot (`planning-method.md`).
- **Nothing is lost** — every merged task's `acceptance` entries move verbatim, `traces_to` are
  concatenated, `## Description` is carried under a sub-heading. A consolidation that drops a
  criterion is a scope change wearing a tidy-up costume.
- **The ceiling** — over 15 open, the plan must land at ≤15; if honest grouping genuinely can't, name
  the smallest honest number and get the user's yes — never land over silently.

### Stage 3: Confirm
Present the plan as one table: group → surviving id (the lowest of the group) · absorbed ids · new
size · recomputed `blocked_by` (union of members' minus the group itself) · one-line rationale. The
operation destroys task files, so **by default it waits for the explicit yes in both config modes**
(planning-method rule 6). The single exception: an explicit **`autopilot` argument on this
invocation** is that yes given up front — apply without pausing and log every group as a fork decision
in `plan.summary.md`. In either path, apply nothing that is not in the presented plan.

### Stage 4: Apply
For each group: widen the survivor's `title`/`summary` to cover the group, append the absorbed
`acceptance` entries verbatim, concatenate `traces_to`, carry each absorbed `## Description` under an
`### Absorbed from T0xx` sub-heading, and append a `## Log` entry naming the absorbed ids. Delete the
absorbed files. Then sweep **every** remaining task's `blocked_by` and remap references to absorbed
ids onto their survivors (dropping self-references). Regenerate `board.md` — header included — with a
"what moved into what" table so old ids stay resolvable in prose, and add the run's note to
`plan.summary.md`'s Forks / Decisions log.

### Stage 5: Report
Before/after: open count, size distribution, the moves table (or where to find it), any XL flagged,
any ceiling overrun agreed with the user. End with «What you should do»
(**`../_shared/build-pipeline/report-format.md`**) — e.g. "nothing, the backlog is 11 coherent tasks"
or "decide whether T014 (XL) should be split".

## Rules

1. **Merge only.** No new tasks, no splits, no builds, no re-opened decisions. XL is flagged, not cut.
2. **Only `todo` tasks are touched.** `in_progress`, `done`, `cancelled`, `needs_human` — never.
3. **Nothing is lost** — acceptance verbatim, traces concatenated, descriptions carried, absorbed ids
   named in the survivor's `## Log` and the board's moves table.
4. **Coherence before count**; the one-sitting small-fixes batch is the only bag-shaped exception.
5. **No merge creates an XL** — a survivor the verify cycle can't hold is a worse backlog, not a
   shorter one.
6. **Confirmation is the default in both modes**; the explicit `autopilot` argument is the upfront
   consent, and every group is still logged as a fork.
7. **No quota.** An already-coherent backlog gets "nothing to merge", not invented merges.
8. **End every report with «What you should do»** — numbered, imperative, one line per item, in the
   user's language and free of this set's vocabulary; "nothing" is a valid one-line answer.
   **`../_shared/build-pipeline/report-format.md`**.
