---
name: create-project-spec
description: "Produce a project's initial documentation end to end, from a raw idea to a buildable spec. Use when starting a new project (or a major new initiative) and you want the full guided flow rather than running each step by hand. Orchestrates the pipeline — gather-context → validate-idea → define-product-requirements → create-user-flows → define-design-decisions → design-architecture → design-dev-architecture — where each phase researches real-world facts, runs an adversarial review (merged in, then removed), and emits a detailed research doc + a short human summary. Opens with gather-context, which interviews the user to turn a short brief into a rich shared understanding the whole pipeline builds on. Works for a NEW (greenfield) project or an EXISTING codebase: for an existing project (project_type: existing) it runs map-codebase first to reverse-engineer the as-is facts, then every phase reconstructs a target spec from them. Asks three setup choices up front (interactive vs autopilot; final combined summary; greenfield vs existing project) and can finish with one human-readable spec summary. A thin conductor: it sequences the focused sub-skills, it does not duplicate their logic."
argument-hint: "[--from <step>]"
---

# Create Project Spec Skill (orchestrator)

You are the conductor of the project-documentation pipeline. You do not do the work of each
phase yourself — you invoke the focused sub-skill for each step (via the Skill tool), let it run
its own internal pipeline (research → draft → adversarial review → merge → dual output), and move
on according to the chosen mode.

The pipeline produces, in order — each phase keeping **two** files (the reviewer's `*.review.md`
is intermediate: applied at merge, then deleted):

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
researches and reviews itself — there is no separate review step to offer, and no review file
survives into the final spec.

**For an existing project (`project_type: existing`),** an extra phase 0 runs first — `map-codebase`
→ `codebase-map.research.md` — to reverse-engineer the as-is facts from the code; then every phase
runs in **existing-project mode** (reconstruct a TARGET spec from the map + the user's intent, logging
drift). The order becomes: `map-codebase → gather-context → validate-idea*  → … → design-dev-architecture`
(`*` `validate-idea` may self-skip in existing mode). Full method:
**`../_shared/spec-pipeline/existing-project-mode.md`**.

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill follows the same
rule on its own, so the whole pipeline speaks the user's language consistently.

## Three setup choices (ask once, up front)

Before step 1, settle three settings and persist them to `.dev-skills/project-spec/.spec-config.md` so
every sub-skill inherits them. Use one `AskUserQuestion` (defaults pre-selected). Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

1. **`mode`** — `interactive` (default): pause at each fork and at each phase's hard gate for your
   approval. `autopilot`: the AI resolves every fork itself, logging each choice in the doc's
   Forks / Decisions log, and runs phases back-to-back without stopping (still does research +
   review + dual output for every phase).
2. **`final_summary`** — `true` (default): at the end, build one combined human-readable
   `.dev-skills/project-spec/summary.md`. `false`: skip it.
3. **`project_type`** — `greenfield` (default) | `existing`. **Detect first, then confirm**: probe
   the repo (Step 0) for non-trivial existing code; pre-select the detected value and let the user
   override. `existing` inserts the `map-codebase` phase 0 and runs every phase in existing-project
   mode (see `../_shared/spec-pipeline/existing-project-mode.md`).

Write the file (create `.dev-skills/project-spec/` if needed; when creating the directory, also drop a
`.dev-skills/project-spec/.gitignore` containing `*.review.md` if absent — everything else there is
committed project documentation):

```
# Spec pipeline config

- mode: <interactive | autopilot>
- final_summary: <true | false>
- project_type: <greenfield | existing>
```

## Procedure

```
- [ ] Step 0: Detect progress + project_type + settle the three settings → write .spec-config.md + seed the project CLAUDE.md map
- [ ] Step 0b: map-codebase   (existing only) → gate / auto-advance
- [ ] Step 1: gather-context                  → gate (interactive) / auto-advance (autopilot)
- [ ] Step 2: validate-idea (may self-skip if existing) → gate / auto-advance
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

**Detect `project_type`.** Probe the repo (read-only) for non-trivial existing **code**: a
dependency manifest (`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` / `Gemfile` /
`pom.xml` …) **and** source files outside `docs/`, `.claude/`, and config. (A `.dev-skills/project-spec/`
from a prior spec run does NOT count as code.) Pre-select the detected value (`existing` if code is
present, else `greenfield`); the heuristic is fuzzy (vendored/generated trees, a docs-only repo), so
**always confirm it with the user** rather than trusting it. Then settle all three settings and write
`.spec-config.md` (above). If it already exists, reuse it unless the user asks to change a setting.

### Step 0b: map-codebase (existing projects only)
If `project_type: existing`, invoke `map-codebase` (via the Skill tool) **before** `gather-context`.
It reverse-engineers `.dev-skills/project-spec/codebase-map.research.md` (the as-is facts) that
`gather-context` and every later phase read. Advance per the mode, exactly like the steps below. In
`greenfield`, skip this step entirely.

Then **seed the project documentation map** in the project's root `CLAUDE.md` — the marker-delimited
block that orients any coding agent to where the spec/backlog/setup docs live and the order to read
them. At this point most artifacts are still *planned*; render them as such. Spec, format, and marker
discipline (idempotent, non-destructive): **`../_shared/agent-guide.md`**. This is orchestrator
housekeeping (like writing `.spec-config.md` / `summary.md`), not a phase — keep it to the shared
block and never touch content outside the markers.

### Steps 1–7: Run each sub-skill, then advance
For each step in order (step 1 is `gather-context` — the discovery interview that produces the
project brief; steps 2–7 are the phases that read it):

**In existing mode** (`project_type: existing`), `map-codebase` (step 0b) has already written the
codebase map. Each phase reads `.spec-config.md`, sees `project_type: existing`, and **self-selects
its existing-project mode** — you pass no flag. One difference to honor: `validate-idea` may
**self-skip** in existing mode (a pure "document what exists" run with no new bets) — allow the skip
and record it; do **not** treat it as the unavailable-skill stop condition below.

1. **Announce** the step and the sub-skill you are about to invoke.
2. **Invoke the sub-skill** via the Skill tool. It reads `.spec-config.md`, runs its internal
   pipeline to completion (research, draft, review → `*.review.md`, merge → applies the review and
   **deletes** it, and the dual output: detailed `*.research.md` + human `*.summary.md`), and
   stops at its own gate per the mode.
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
