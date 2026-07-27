# Pipeline config & modes (shared — spec pipeline)

Three settings govern how every phase behaves. The orchestrator sets them once; each phase skill
reads them and adapts. Phase skills are also runnable standalone, so they fall back gracefully
when no config exists.

## The settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: at every fork, ask the human; stop at the phase's hard gate for approval.
  - `autopilot`: the AI resolves every fork itself and **logs each one** in the detailed doc's
    `## Forks / Decisions log`; it does not prompt the human and does not stop at gates. Low- and
    medium-confidence forks are surfaced in the human summary as "must answer".
- **`final_summary`** — `true` (default) | `false`. Whether the orchestrator builds the combined
  `.dev-skills/project-spec/summary.md` at the end of the run.

## Config file — `.dev-skills/project-spec/.spec-config.md`

Small, human-readable. Written by `create-project-spec` (or by the first phase skill run
standalone). Format:

```
# Spec pipeline config

- mode: interactive        # interactive | autopilot
- final_summary: true      # true | false
```

## How a phase skill uses it

1. At intake, read `.dev-skills/project-spec/.spec-config.md`.
2. **Present:** use `mode` for this phase. Separately, check whether the repo already holds code — if
   it does, read it and confirm rather than re-ask (see `elicitation-method.md` → "When the repo
   already has code"). That is a fact about the repo, not a setting.
3. **Absent (standalone run):** ask the user the settings (one `AskUserQuestion`, defaults
   pre-selected: interactive + final_summary true), then write
   `.spec-config.md` so later standalone phases inherit the choice. If the user just wants the
   single phase, interactive is the safe default. 

Everything under `.dev-skills/project-spec/` is committed project documentation — the pipeline
writes no transient files, so the directory needs no local `.gitignore`.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves goes into the Forks / Decisions log with
  options, choice, rationale, confidence, and source. Autopilot changes *who answers*, not
  *whether it's recorded*.
- **Surface what's risky.** Anything decided at medium/low confidence, or with material downside
  if wrong, is marked `Needs human confirm? = yes` and appears in the human summary (and, via the
  orchestrator, in the final `summary.md`).
- **Still do the work.** Autopilot skips the human prompts and gates — it does **not** skip
  research, review, the fixes, or the dual output. The reviewer still runs; the AI just resolves the
  🔴 findings itself (spending a reserved fetch where it genuinely changes a decision) instead of
  asking.
- **Persona is preserved.** An autopilot `validate-idea` is still adversarial — it pressure-tests
  the idea and can still reach a `kill` verdict. Autopilot means "don't ask the human", not "be
  agreeable".

## Interactive rules

- Ask at each fork (the phase's forcing questions), one dimension at a time.
- The fix stage stops on 🔴 review findings; the phase's hard gate stops for approval before the
  next phase. The orchestrator owns advancing between phases.
