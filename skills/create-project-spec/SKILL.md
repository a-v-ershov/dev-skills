---
name: create-project-spec
description: "Take a raw idea to a buildable project spec by running gather-context, validate-idea, define-product-requirements, create-user-flows, define-design-decisions, design-architecture, define-code-style and design-dev-architecture in order. Use to start a new project or major initiative with the full guided flow; works on an empty repo or existing code."
argument-hint: "[--from <step>]"
---

# Create Project Spec Skill (orchestrator)

You conduct the project-documentation pipeline: invoke each phase's sub-skill via the Skill tool, let
it run its own pipeline, and advance per the chosen mode.

Each phase researches and reviews itself and writes **two** files (the review never becomes one); the
architecture phases add ADRs, step 7 the distilled `code-style.md` guide the build agents follow:

| Step | Sub-skill | Detailed doc | Human summary |
|------|-----------|--------------|---------------|
| 1 | `gather-context` | `project-brief.research.md` | `project-brief.summary.md` |
| 2 | `validate-idea` | `idea-validation.research.md` | `idea-validation.summary.md` |
| 3 | `define-product-requirements` | `product-requirements.research.md` | `product-requirements.summary.md` |
| 4 | `create-user-flows` | `user-flows.research.md` | `user-flows.summary.md` |
| 5 | `define-design-decisions` | `design-decisions.research.md` | `design-decisions.summary.md` |
| 6 | `design-architecture` | `architecture.research.md` (+ `adr/*`) | `architecture.summary.md` |
| 7 | `define-code-style` | `code-style.research.md` (+ the distilled `code-style.md` guide) | `code-style.summary.md` |
| 8 | `design-dev-architecture` | `dev-architecture.research.md` (+ `adr/*`) | `dev-architecture.summary.md` |

All under `.dev-skills/project-spec/`. There is no separate review step.

**If the repo already has code,** nothing changes: each phase reads the code at its own intake, says
what it found, and confirms instead of re-asking — wanted differences become a
`## Divergences (code vs intended)` section in that phase's doc. You pass no flag and add no mode,
phase or setting. Method: **`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo
already has code".

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Each sub-skill follows the same
rules on its own.

## Two setup choices (ask once, up front)

Before step 1, settle two settings and persist them to `.dev-skills/project-spec/.spec-config.md` so
every sub-skill inherits them — one `AskUserQuestion`, defaults pre-selected
(**`../_shared/spec-pipeline/pipeline-config.md`**).

1. **`mode`** — `interactive` (default): pause at each fork and each phase's hard gate for approval.
   `autopilot`: the AI resolves every fork itself, logs each choice in the doc's Forks / Decisions
   log, and runs phases back-to-back.
2. **`final_summary`** — `true` (default): build one combined `.dev-skills/project-spec/summary.md` at
   the end. `false`: skip it.

Write the file (create `.dev-skills/project-spec/` if needed — everything there is committed project
documentation; nothing transient, so no `.gitignore`):

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
- [ ] Step 7: define-code-style                → gate / auto-advance
- [ ] Step 8: design-dev-architecture          → gate / auto-advance
- [ ] Done: build summary.md (if final_summary) + refresh the project CLAUDE.md map + summarize the documentation set
```

### Step 0: Detect progress, settle settings
List `.dev-skills/project-spec/`. If artifacts exist, say so and propose resuming from the first
missing step; honor an explicit `--from <step>`; ask before overwriting a completed step. Settle the
two settings and write `.spec-config.md` (reuse an existing one unless the user changes a setting).

Then **seed the project documentation map** in the root `CLAUDE.md` — the marker-delimited block
telling any coding agent where the spec/backlog/setup docs live and the reading order; render
not-yet-written artifacts as *planned*. Spec and marker discipline (idempotent, non-destructive):
**`../_shared/agent-guide.md`**. Housekeeping, not a phase — never touch content outside the markers.

### Steps 1–8: Run each sub-skill, then advance
In order. Step 1 (`gather-context`) interviews the user into a discovery brief that steps 2–8 read as
settled intent. `validate-idea` may **self-skip** on an existing product with no new bets — allow and
record it (it is not the unavailable-skill stop below).

1. **Announce** the step and its sub-skill.
2. **Invoke the sub-skill** via the Skill tool. It reads `.spec-config.md`, runs its pipeline to
   completion (elicit, research, draft, review, fix, dual output `*.research.md` + `*.summary.md`) and
   stops at its own gate per the mode.
3. **Advance by mode:**
   - **interactive — Hard gate.** Present the two artifact paths and STOP for explicit approval:
     > "Step N (<sub-skill>) finished → <noun>.research.md (detail), <noun>.summary.md (for you).
     > Approve to continue to step N+1, or tell me what to change."
     Never auto-advance; on change requests, loop back into that step's sub-skill.
   - **autopilot — Auto-advance.** Do not stop. Note in your running progress the must-answer forks
     the phase surfaced (from its `*.summary.md`) and continue.

A sub-skill not available in this collection stops the run in either mode: report it and let the user
decide whether to skip the step or build the skill first.

### Done: final summary + handoff
When the last available step completes:

1. **If `final_summary: true`,** build `.dev-skills/project-spec/summary.md`: each phase's
   `*.summary.md` essence + every still-open fork (every `Needs human confirm? = yes`) + consolidated
   open risks. Concatenate and roll up, don't re-derive. Format:
   **`../_shared/spec-pipeline/output-format.md`** (section 4).
2. **Refresh the project documentation map** in the root `CLAUDE.md` — re-render the marker block so
   the now-real `.dev-skills/project-spec/` artifacts (and `summary.md`) show as present
   (**`../_shared/agent-guide.md`**, idempotent — replace the block in place).
3. **Summarize the documentation set** (paths + one-line status each) and hand off: the project is
   ready for implementation. In autopilot, point the user at `summary.md` first and list the
   must-answer forks they still own.

## Rules

1. **Conduct, don't duplicate.** Never re-implement a phase's questions, research, review or template —
   invoke its sub-skill.
2. **Respect the mode.** interactive: one approval per step, never chain two without it. autopilot:
   never stop for forks/gates, but every phase still researches, reviews, writes its two files and logs
   every auto-resolved fork.
3. **Resume, don't restart.** Reuse existing artifacts; redo a step only on explicit request.
4. **Settings are set once and shared** via `.spec-config.md`, so standalone and orchestrated runs
   behave identically.
5. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
