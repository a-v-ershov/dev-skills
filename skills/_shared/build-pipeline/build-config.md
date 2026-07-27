# Build config & modes (shared — build pipeline)

Two settings govern how the build pipeline behaves. `build-product` sets them once; each build skill
(`setup-dev-environment`, `plan-development`, `implement-feature`, `verify-feature`,
`propagate-changes`) reads them and adapts. Every skill is also runnable standalone, so it falls back
gracefully when no config exists.

## The two settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: at every fork, ask the human; stop at hard gates (plan approval, before a
    destructive backlog change, after a `needs_human` escalation) for approval.
  - `autopilot`: the AI resolves every fork itself and **logs each one** (in the plan doc's
    `## Forks / Decisions log`, or the task's `## Log`); it does not prompt or stop — **except** for
    the two things that always stop regardless of mode (below).
- **`max_verify_iterations`** — integer, default **4**. The cap on the implement↔verify loop for a
  single task. When `verify-feature` has failed a critical acceptance criterion this many times, the
  task goes to `needs_human` instead of looping again.

## Config file — `.dev-skills/build-plan/.build-config.md`

Small, human-readable. Written by `build-product` (or by the first build skill run standalone). Format:

```
# Build pipeline config

- mode: interactive          # interactive | autopilot
- max_verify_iterations: 4   # cap on the implement↔verify loop before needs_human
```

## How a build skill uses it

1. At intake, read `.dev-skills/build-plan/.build-config.md`.
2. **Present:** use `mode` and `max_verify_iterations`.
3. **Absent (standalone run):** ask the user the two settings (one `AskUserQuestion`, defaults
   pre-selected: interactive + 4), then write `.build-config.md` so later standalone skills inherit
   the choice. Interactive is the safe default.

Whenever you create `.dev-skills/build-plan/`, it is committed project documentation — no special gitignore
is needed (unlike the spec pipeline's transient `*.review.md`, the build pipeline keeps no transient
files).

## Agent lifecycle

`build-product` spawns the build-loop roles as **subagents** — the **`implementer`** agent (it
preloads `implement-feature`) and the **`verifier`** agent (it preloads `verify-feature`) — with a
deliberate context policy:

- **`implementer` — fresh per task, continuous within a task.** Spawn it as a fresh subagent
  (clean context) when a task starts. Across the implement↔verify rounds of the *same* task, continue
  that *same* agent so it keeps the memory of what it already tried — do **not** re-spawn it per round
  (a fresh-per-round implementer re-derives the task each round and loses the loop's continuity). When
  the task finishes, discard it; the next task gets a new fresh agent. One task, one context.
- **`verifier` — a separate agent from the implementer** (see `verification-method.md`). It may
  be re-spawned per round, since the tests it authors persist as committed files.

This keeps the orchestrator's own context thin (just backlog state) and each task's reasoning isolated.

## Two things ALWAYS stop, regardless of mode

Autopilot suppresses ordinary forks, but never these:

1. **`needs_human` escalation.** When a task hits `max_verify_iterations` (or a blocker it cannot
   resolve), the loop stops for that task in both modes — the whole point is to surface it to a human.
2. **Critical / destructive change propagation.** When `propagate-changes` would cancel a task or
   reopen a `done` task as rework (or make any decision-changing edit it isn't confident about), it
   asks the human in both modes. Routine, non-destructive reconciliation proceeds automatically.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged (plan Forks log, or task Log) with
  the choice, rationale, and confidence. Autopilot changes *who answers*, not *whether it's recorded*.
- **Still do the work.** Autopilot skips human prompts and ordinary gates — it does **not** skip the
  separate-agent verification, the bounded loop, or the checkpoint commits.
- **Verification is never self-approved.** Even in autopilot, `verify-feature` runs in a separate,
  fresh agent (no bias from the implementer) and proves real outcomes — it does not rubber-stamp.

## Interactive rules

- Ask at each fork. Stop at the plan-approval gate, at a `needs_human` escalation, and before any
  destructive backlog change.
- `build-product` owns advancing between tasks; in interactive it may confirm each task (or each
  checkpoint commit) with the human per the orchestrator's gate.
