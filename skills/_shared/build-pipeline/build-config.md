# Build config & modes (shared — build pipeline)

One setting governs the build pipeline. `build-tasks` sets it once; each build skill
(`setup-dev-environment`, `plan-development`, `implement-feature`, `verify-feature`, `run-task`,
`build-tasks`) reads it, and falls back gracefully when run standalone without one.

## The setting

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: ask the human at every fork; stop for approval at the hard gates ("Interactive
    rules").
  - `autopilot`: the AI resolves every fork and **logs each one** (the plan doc's
    `## Forks / Decisions log`, or the task's `## Log`); no prompts, no stops — **except** the two
    things that always stop (below).

There is **no iteration-count setting**: the per-task cycle is fixed at **one** — build once, verify
once, fix once (`verification-method.md`).

## Config file — `.dev-skills/build-plan/.build-config.md`

Small, human-readable. Written by `build-tasks` (or by the first build skill run standalone):

```
# Build pipeline config

- mode: interactive          # interactive | autopilot
```

## How a build skill uses it

1. At intake, read `.dev-skills/build-plan/.build-config.md`.
2. **Present:** use `mode`.
3. **Absent (standalone run):** ask the user for `mode` (one `AskUserQuestion`, default
   **interactive**), then write `.build-config.md` so later standalone skills inherit the choice.

`.dev-skills/build-plan/` is committed project documentation — no gitignore needed except for the
mockups tree (`mockup-method.md`).

## Agent lifecycle

`run-task` spawns the build-loop roles as **subagents** — **`implementer`** (preloads
`implement-feature`) and **`verifier`** (preloads `verify-feature`):

- **`implementer` — fresh per task, continuous within the task.** A fresh subagent (clean context) at
  task start; keep that *same* agent for the fix round — it remembers what it built and why. Discard it
  when the task finishes. One task, one context.
- **`verifier` — a separate agent from the implementer** (`verification-method.md`), spawned once per
  task; its committed tests outlive its context.

The orchestrator keeps only backlog state in its own context.

## Two things ALWAYS stop, regardless of mode

1. **`needs_human` escalation.** The one fix round doesn't close a critical criterion, or the
   implementer hits a blocker it cannot resolve — the task stops in both modes.
2. **Critical / destructive backlog change.** `plan-development` amend mode would cancel a task or
   reopen a `done` task as rework (or make any decision-changing edit it isn't confident about) — it
   asks in both modes. Routine, non-destructive reconciliation proceeds automatically.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged (plan Forks log, or task Log) with
  the choice, rationale, and confidence.
- **Still do the work.** Autopilot skips human prompts and ordinary gates — **not** the separate-agent
  verification, the fix round, or the checkpoint commits. It skips only the human acceptance step,
  recording `review: auto` with the reason.
- **Verification is never self-approved** — even in autopilot, `verify-feature` runs in a separate,
  fresh agent and proves real outcomes.

## Interactive rules

- Ask at each fork. Stop at the plan-approval gate, at a `needs_human` escalation, and before any
  destructive backlog change.
- `build-tasks` owns advancing between tasks; it may confirm each task (or each checkpoint commit) with
  the human per the orchestrator's gate.
