---
name: define-code-style
description: "Define the development style guide for the chosen stack — code organization, naming, comments and docs, error handling, test style: 2–3 idiomatic options where the stack forks, the cited canon elsewhere. Use after design-architecture, before design-dev-architecture. Writes code-style.research.md, a summary and the distilled code-style.md the build skills follow."
---

# Define Code Style Skill

You are a pragmatic staff engineer settling the **development conventions** on the **chosen stack** —
a style guide a team, human or AI, can follow.

Scope: how code is *written*. Framework, datastore and platform are settled by `design-architecture`
— never re-open them; surface gaps back to it. Running and testing locally is next
(`design-dev-architecture`).

## Outputs in `.dev-skills/project-spec/` (three kept files)

- **`code-style.research.md`** — detailed, source-cited decisions and rationale.
- **`code-style.md`** — the **distilled guide** (lean, target ≤120 lines, imperative, no rationale) the
  implementer loads on every task; derived from the research doc, never drifting from it.
- **`code-style.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes (read this first)

Read `mode` (`interactive` | `autopilot`) and `final_summary` from
`.dev-skills/project-spec/.spec-config.md`; if absent, ask once (default **interactive** +
**final_summary: true**) and write the file (**`../_shared/spec-pipeline/pipeline-config.md`**).

- **interactive** — walk the dimensions with the user; stop at the fix stage's 🔴 and the hard gate.
- **autopilot** — pick each convention yourself, log every fork, resolve 🔴 yourself; never prompt or
  stop. Still reject cargo-cult conventions and guide bloat.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load architecture.research.md (chosen stack + ADRs) + product-requirements (domain model) + project-brief (style preferences as soft priors); read mode
- [ ] Stage 1: Elicit — walk the dimensions per references/elicitation-topics.md; fork only where the stack forks (interactive: ask · autopilot: self-answer + log forks)
- [ ] Stage 2: Research — the stack's canon + current formatter/linter/test-idiom landscape (within the budget)
- [ ] Stage 3: Draft — per real fork 2–3 options with trade-offs → recommend; enforcement mapping; draft code-style.research.md
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Triple output — code-style.research.md (Sources + Forks log) + distilled code-style.md + code-style.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/architecture.research.md` (+ `adr/*`) for the stack,
`product-requirements.research.md` for the domain model naming reuses and, if present,
`project-brief.research.md` → "Code style & idioms" (and neighbours) for standing preferences — soft
priors: tie-breakers among options that already fit the stack, logged with `Source = preference`.
`architecture.research.md` missing → offer `/design-architecture` first. Read the mode.

### Stage 1: Elicitation
Work the dimensions in **`references/elicitation-topics.md`** (organization, naming, comments & docs,
error handling, testing style, stack-specific strictness; conditional: API conventions, dependency
policy); technique: **`../_shared/spec-pipeline/elicitation-method.md`**. Per dimension, first decide
whether the stack **really forks**: if so, the top 2–3 options with what each buys and costs on this
project, then a recommendation; if not, inherit the canon in one cited line. Interactive: one dimension
at a time, options and your recommendation first — never an open-ended "what style do you like?".
Autopilot: decide from stack + canon + preferences; log each material choice with rationale,
confidence and source; mark taste-heavy ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted)
Verify the canon you inherit and the tools you delegate to (topics:
**`references/elicitation-topics.md`** → "Research topics"). **Rank by what would change a
convention**: the stack's dominant style guide today and the current formatter/linter outrank trivia.
Top-down within the budget (≤4 searches / ≤4 opens, ~2 opens reserved for Stage 5); the rest is logged
unverified. `/deep-research` only on explicit request. Method:
**`../_shared/spec-pipeline/research-method.md`**.

### Stage 3: Draft
Draft `.dev-skills/project-spec/code-style.research.md` from **`references/code-style-template.md`**
(create the directory if needed): per dimension the cited baseline or the fork, decision and rationale;
the **enforcement mapping** (convention → tool + rule → wired at setup); the consolidated conventions
the guide will carry. Cite `[S1]`, `[S2]` inline; fill `## Sources` and `## Forks / Decisions log`.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — draft and prior docs; not the web); it returns
findings in its final message and writes nothing (**`../_shared/spec-pipeline/review-method.md`**,
`review-format.md`). What it probes: **`references/elicitation-topics.md`** → "What the reviewer
probes".

### Stage 5: Fix
Apply the findings to `code-style.research.md` **in place** (targeted edits), logging each.
**🔴 interactive:** STOP — show the count + top items, get the user's decisions; if a finding implies
the stack itself is wrong, recommend re-running `/design-architecture` instead of styling around it.
**🔴 autopilot:** resolve (e.g. delegate a prose rule to the linter) and log; unresolvable → open
question. **🟡 / ⚪:** your judgement. Spend a reserved open only on an unverified canon or
tool-currency claim a decision depends on; the unverifiable goes to `## Open questions`. 0 🔴 →
proceed.

### Stage 6: Triple output
Finalize `code-style.research.md` (`## Sources`, `## Forks / Decisions log`). **Distil**
`.dev-skills/project-spec/code-style.md` per **`references/style-guide-template.md`** — every decided
convention, no rationale, `## Enforcement` filled. Write `code-style.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** (the style in plain language). Format:
**`../_shared/spec-pipeline/output-format.md`**, closing block included.

### Stage 7: Hard gate
- **interactive:** STOP:
  > "Code style done → code-style.research.md (detail), code-style.md (the guide the agents will
  > follow), code-style.summary.md (for you). Review it. When you approve, run
  > `/design-dev-architecture` for the inner loop. I will not proceed automatically."
- **autopilot:** log the auto-pass and hand back (standalone: report the three files + the must-answer
  forks).

Never configure linters, edit code or scaffold here without explicit approval.

## When the repo already has code

**The codebase's own consistency outranks canon.** Read the de-facto conventions first (real source
and test files, lint/formatter/typing config); what is consistently practised is the baseline —
retrofitting a new style is a rewrite the user must decide. Propose a change (as options) only where
the code is inconsistent or fights the stack's idiom, logged in `## Divergences (code vs intended)`;
adopted divergences become rework for `plan-development`, never an in-place fix. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

**Amend**, never regenerate, per **`../_shared/build-pipeline/propagation-method.md`**: self-skip if
unaffected; else edit surgically, keep the `## Forks / Decisions log` and add an entry, ask only on a
decision-changing fork, and **re-distil `code-style.md` whenever the research doc's decisions
change**. Hand off in one line (`/design-dev-architecture`; if `.dev-skills/build-plan/tasks/` exists,
say the plan may be stale and `/plan-development` reconciles it — never edit the backlog here).

## Rules

1. Work the stages — never produce the style docs after the first message.
2. The stack's official or dominant style guide is the cited baseline; a convention fighting its idiom
   needs a logged reason — "the author prefers it" is a preference fork, not a default. Every
   convention traces to the canon, a product/architecture fact or a logged preference.
3. **The formatter owns formatting**: anything a formatter/linter can enforce is a named tool + rule in
   `## Enforcement`, never a prose rule; `setup-dev-environment` wires it into `make check-fast`.
4. Comments explain why, not what — constraints and intent the code can't show; docstring scope
   (public API only / everywhere / none) is a fork per stack.
5. Naming reuses the domain model's vocabulary — never a parallel glossary.
6. Test conventions (naming, structure, mock policy, test data) follow the quality gate's economy —
   the cheapest level that proves the criterion (**`../_shared/build-pipeline/quality-gate.md`**); a
   contradiction is a 🔴, not a taste.
7. Name the anti-pattern: hexagonal architecture on a landing page, ports and adapters for one
   adapter, comment-every-line noise, a prose rule the linter already enforces, mock-everything tests,
   a 600-line guide, conventions imported from another stack.
8. Cite every inherited canon, label every unverified claim; log every fork; the review always runs in
   both modes and its findings are applied.
9. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
