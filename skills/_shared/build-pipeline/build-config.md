# Build config & modes (shared — build pipeline)

One setting governs how the build pipeline behaves. `build-tasks` sets it once; each build skill
(`setup-dev-environment`, `plan-development`, `implement-feature`, `verify-feature`,
`run-task`, `build-tasks`) reads it and adapts. Every skill is also runnable standalone, so it falls back
gracefully when no config exists.

## The setting

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: at every fork, ask the human; stop at hard gates (plan approval, before a
    destructive backlog change, after a `needs_human` escalation) for approval.
  - `autopilot`: the AI resolves every fork itself and **logs each one** (in the plan doc's
    `## Forks / Decisions log`, or the task's `## Log`); it does not prompt or stop — **except** for
    the two things that always stop regardless of mode (below).

There is **no iteration-count setting**: the per-task cycle is fixed at **one** — build once, verify
once, fix once (see `verification-method.md`). Nothing to tune, nothing to run away.

## Config file — `.dev-skills/build-plan/.build-config.md`

Small, human-readable. Written by `build-tasks` (or by the first build skill run standalone). Format:

```
# Build pipeline config

- mode: interactive          # interactive | autopilot
```

## How a build skill uses it

1. At intake, read `.dev-skills/build-plan/.build-config.md`.
2. **Present:** use `mode`.
3. **Absent (standalone run):** ask the user for `mode` (one `AskUserQuestion`, default
   **interactive**), then write `.build-config.md` so later standalone skills inherit the choice.

Whenever you create `.dev-skills/build-plan/`, it is committed project documentation — no special gitignore
is needed, since the build pipeline keeps no transient files (except the mockups tree, see
`mockup-method.md`).

## Agent lifecycle

`run-task` spawns the build-loop roles as **subagents** — the **`implementer`** agent (it
preloads `implement-feature`) and the **`verifier`** agent (it preloads `verify-feature`) — with a
deliberate context policy:

- **`implementer` — fresh per task, continuous within the task.** Spawn it as a fresh subagent (clean
  context) when a task starts, and keep that *same* agent for the fix round after verification — it
  remembers what it built and why, which is exactly what makes a one-round fix workable. Discard it
  when the task finishes; the next task gets a new one. One task, one context.
- **`verifier` — a separate agent from the implementer** (see `verification-method.md`), spawned once
  per task. The tests it authors persist as committed files, so its work outlives its context.

This keeps the orchestrator's own context thin (just backlog state) and each task's reasoning isolated.

## Two things ALWAYS stop, regardless of mode

Autopilot suppresses ordinary forks, but never these:

1. **`needs_human` escalation.** When the one fix round doesn't close a critical criterion, or the
   implementer hits a blocker it cannot resolve, the task stops in both modes — the whole point is to
   surface it to a human.
2. **Critical / destructive backlog change.** When `plan-development` amend mode would cancel a task or
   reopen a `done` task as rework (or make any decision-changing edit it isn't confident about), it
   asks the human in both modes. Routine, non-destructive reconciliation proceeds automatically.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged (plan Forks log, or task Log) with
  the choice, rationale, and confidence. Autopilot changes *who answers*, not *whether it's recorded*.
- **Still do the work.** Autopilot skips human prompts and ordinary gates — it does **not** skip the
  separate-agent verification, the fix round, or the checkpoint commits. The one thing autopilot does
  skip is the human acceptance step — it records `review: auto` with the reason.
- **Verification is never self-approved.** Even in autopilot, `verify-feature` runs in a separate,
  fresh agent (no bias from the implementer) and proves real outcomes — it does not rubber-stamp.

## Interactive rules

- Ask at each fork. Stop at the plan-approval gate, at a `needs_human` escalation, and before any
  destructive backlog change.
- `build-tasks` owns advancing between tasks; in interactive it may confirm each task (or each
  checkpoint commit) with the human per the orchestrator's gate.
