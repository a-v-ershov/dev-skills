# Pipeline config & modes (shared — spec pipeline)

The orchestrator sets these once; every phase reads them, and a phase run standalone falls back
gracefully when no config exists.

## The settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: ask the human at every fork; stop at the phase's hard gate for approval.
  - `autopilot`: the AI resolves every fork itself and **logs each one** in the detailed doc's
    `## Forks / Decisions log`; no prompts, no stops at gates. Low- and medium-confidence forks are
    surfaced in the human summary as "must answer".
- **`final_summary`** — `true` (default) | `false`. Whether the orchestrator builds the combined
  `.dev-skills/project-spec/summary.md` at the end of the run.

## Config file — `.dev-skills/project-spec/.spec-config.md`

Written by `create-project-spec` (or by the first phase skill run standalone):

```
# Spec pipeline config

- mode: interactive        # interactive | autopilot
- final_summary: true      # true | false
```

## How a phase skill uses it

1. At intake, read `.dev-skills/project-spec/.spec-config.md`.
2. **Present:** use `mode`. Separately check whether the repo already holds code — if so, read it and
   confirm rather than re-ask (`elicitation-method.md` → "When the repo already has code"); that is a
   fact about the repo, not a setting.
3. **Absent (standalone run):** ask in one `AskUserQuestion` (defaults pre-selected: interactive +
   final_summary true), then write `.spec-config.md` so later standalone phases inherit it. For a
   single phase, interactive is the safe default.

Everything under `.dev-skills/project-spec/` is committed project documentation — no transient
files, so no local `.gitignore`.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves goes into the Forks / Decisions log with
  options, choice, rationale, confidence and source. Autopilot changes *who answers*, not *whether
  it's recorded*.
- **Surface what's risky.** Medium/low confidence, or material downside if wrong →
  `Needs human confirm? = yes`, shown in the human summary (and, via the orchestrator, the final
  `summary.md`).
- **Still do the work.** Autopilot skips prompts and gates — **not** research, review, fixes or the
  dual output. The reviewer still runs; the AI resolves the 🔴 findings itself (spending a reserved
  fetch where it changes a decision).
- **Persona is preserved.** An autopilot `validate-idea` is still adversarial and can still reach a
  `kill` verdict. Autopilot means "don't ask the human", not "be agreeable".

## Interactive rules

- Ask at each fork (the phase's forcing questions), one dimension at a time.
- The fix stage stops on 🔴 review findings; the hard gate stops for approval before the next phase.
  The orchestrator owns advancing between phases.
