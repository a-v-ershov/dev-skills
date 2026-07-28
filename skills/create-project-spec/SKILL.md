---
name: create-project-spec
description: "Produce a project's initial documentation end to end, from a raw idea to a buildable spec. Use when starting a new project (or a major new initiative) and you want the full guided flow rather than running each step by hand. Orchestrates the pipeline — gather-context → validate-idea → define-product-requirements → create-user-flows → define-design-decisions → design-architecture → design-dev-architecture — where each phase researches real-world facts within a fixed budget, runs an adversarial review whose findings it applies in place, and emits a detailed research doc + a short human summary. Opens with gather-context, which interviews the user to turn a short brief into a rich shared understanding the whole pipeline builds on. Works on an empty repo or one that already has code: when code is present each phase reads it, reports what it found, and confirms rather than re-asks, recording anything the user wants changed as a divergence. Asks two setup choices up front (interactive vs autopilot; final combined summary) and can finish with one human-readable spec summary. A thin conductor: it sequences the focused sub-skills, it does not duplicate their logic."
argument-hint: "[--from <step>]"
---

# Create Project Spec Skill (orchestrator)

You are the conductor of the project-documentation pipeline. You do not do the work of each
phase yourself — you invoke the focused sub-skill for each step (via the Skill tool), let it run
its own internal pipeline (research → draft → adversarial review → merge → dual output), and move
on according to the chosen mode.

The pipeline produces, in order — **two** files per phase (the reviewer writes none: it returns its
findings and the phase applies them in place):

| Step | Sub-skill | Detailed doc | Human summary |
|------|-----------|--------------|---------------|
| 1 | `gather-context` | `project-brief.research.md` | `project-brief.summary.md` |
| 2 | `validate-idea` | `idea-validation.research.md` | `idea-validation.summary.md` |
| 3 | `define-product-requirements` | `product-requirements.research.md` | `product-requirements.summary.md` |
| 4 | `create-user-flows` | `user-flows.research.md` | `user-flows.summary.md` |
| 5 | `define-design-decisions` | `design-decisions.research.md` | `design-decisions.summary.md` |
| 6 | `design-architecture` | `architecture.research.md` (+ `adr/*`) | `architecture.summary.md` |
| 7 | `design-dev-architecture` | `dev-architecture.research.md` (+ `adr/*`) | `dev-architecture.summary.md` |

All under `.dev-skills/project-spec/`. Step 1 (`gather-context`) interviews the user to turn their short
brief into a rich discovery brief that every later phase reads as settled intent. Each phase
researches and reviews itself — there is no separate review step to offer, and the review never
becomes a file.

**If the repo already has code,** nothing about the pipeline changes: each phase reads what it needs
from the code at its own intake, tells the user what it found, and confirms instead of re-asking —
differences the user wants become a `## Divergences (code vs intended)` section in that phase's doc.
There is no separate mode, no extra phase, and no setting for it. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill follows the same
rule on its own, so the whole pipeline speaks the user's language consistently.

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Two setup choices (ask once, up front)

Before step 1, settle two settings and persist them to `.dev-skills/project-spec/.spec-config.md` so
every sub-skill inherits them. Use one `AskUserQuestion` (defaults pre-selected). Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

1. **`mode`** — `interactive` (default): pause at each fork and at each phase's hard gate for your
   approval. `autopilot`: the AI resolves every fork itself, logging each choice in the doc's
   Forks / Decisions log, and runs phases back-to-back without stopping (still does research +
   review + dual output for every phase).
2. **`final_summary`** — `true` (default): at the end, build one combined human-readable
   `.dev-skills/project-spec/summary.md`. `false`: skip it.

Write the file (create `.dev-skills/project-spec/` if needed — everything there is committed project
documentation; the pipeline writes no transient files, so the directory needs no `.gitignore`):

```
# Spec pipeline config

- mode: <interactive | autopilot>
- final_summary: <true | false>
```

## Procedure

```
- [ ] Step 0: Detect progress + settle the two settings → write .spec-config.md + seed the project CLAUDE.md map
- [ ] Step 1: gather-context                  → gate (interactive) / auto-advance (autopilot)
- [ ] Step 2: validate-idea (may self-skip on an existing product) → gate / auto-advance
- [ ] Step 3: define-product-requirements      → gate / auto-advance
- [ ] Step 4: create-user-flows                → gate / auto-advance
- [ ] Step 5: define-design-decisions           → gate / auto-advance
- [ ] Step 6: design-architecture              → gate / auto-advance
- [ ] Step 7: design-dev-architecture          → gate / auto-advance
- [ ] Done: build summary.md (if final_summary) + refresh the project CLAUDE.md map + summarize the documentation set
```

### Step 0: Detect progress, settle settings
List `.dev-skills/project-spec/`. If artifacts already exist, tell the user and propose resuming from the
first missing step; honor an explicit `--from <step>`. Never silently redo a completed step — ask
before overwriting.

Then settle the two settings and write `.spec-config.md` (above). If it already exists, reuse it
unless the user asks to change a setting.

Then **seed the project documentation map** in the project's root `CLAUDE.md` — the marker-delimited
block that orients any coding agent to where the spec/backlog/setup docs live and the order to read
them. At this point most artifacts are still *planned*; render them as such. Spec, format, and marker
discipline (idempotent, non-destructive): **`../_shared/agent-guide.md`**. This is orchestrator
housekeeping (like writing `.spec-config.md` / `summary.md`), not a phase — keep it to the shared
block and never touch content outside the markers.

### Steps 1–7: Run each sub-skill, then advance
For each step in order (step 1 is `gather-context` — the discovery interview that produces the
project brief; steps 2–7 are the phases that read it):

**If the repo already has code,** each phase handles it on its own — reading the code at its intake,
reporting what it found, and confirming rather than re-asking. You pass no flag and add no step. One
thing to honor: `validate-idea` may **self-skip** when the product already exists and there are no new
bets to test — allow the skip and record it; it is not the unavailable-skill stop condition below.

1. **Announce** the step and the sub-skill you are about to invoke.
2. **Invoke the sub-skill** via the Skill tool. It reads `.spec-config.md`, runs its internal
   pipeline to completion (elicit, budgeted research, draft, review → the reviewer returns findings,
   fix → applies them in place, and the dual output: detailed `*.research.md` + human
   `*.summary.md`), and stops at its own gate per the mode.
3. **Advance by mode:**
   - **interactive — Hard gate.** Present the two artifact paths and STOP for explicit approval:
     > "Step N (<sub-skill>) finished → <noun>.research.md (detail), <noun>.summary.md (for you).
     > Approve to continue to step N+1, or tell me what to change."
     Do NOT auto-advance. On change requests, loop back into that step's sub-skill.
   - **autopilot — Auto-advance.** Do not stop. Note in your running progress which must-answer
     forks the phase surfaced (from its `*.summary.md`), and continue to the next step.

A sub-skill not yet available in this collection is a stop condition regardless of mode: report it
and let the user decide whether to skip the step or build the skill first.

### Done: final summary + handoff
When the last available step completes:

1. **If `final_summary: true`,** build `.dev-skills/project-spec/summary.md` — one human-readable
   document combining each phase's `*.summary.md` essence + a consolidated list of every
   still-open fork (every `Needs human confirm? = yes`) across all phases + consolidated open
   risks. Do not re-derive — concatenate and roll up. Format:
   **`../_shared/spec-pipeline/output-format.md`** (section 4).
2. **Refresh the project documentation map** in the root `CLAUDE.md` — re-render the marker block so
   the now-real `.dev-skills/project-spec/` artifacts (and `summary.md`) show as present. Spec + marker
   discipline: **`../_shared/agent-guide.md`** (idempotent — replace the block in place).
3. **Summarize the documentation set** (paths + one-line status each) and hand off: the project is
   ready for implementation. In autopilot, point the user at `summary.md` first and list the
   must-answer forks they still own.

## Rules

1. **Conduct, don't duplicate.** Never re-implement a phase's questions, research, review, or
   template — invoke its sub-skill. Each phase owns its own research + review.
2. **Respect the mode.** interactive: one approval per step, never chain two without it.
   autopilot: never stop for forks/gates, but every phase still researches, reviews, and writes
   its two files, and every auto-resolved fork is logged.
3. **Resume, don't restart.** Reuse existing artifacts; only redo a step on explicit request.
4. **Settings are set once and shared.** Write `.spec-config.md` before step 1 so standalone and
   orchestrated runs behave identically.
