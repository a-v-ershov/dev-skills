---
name: define-code-style
description: "Define the project's development style guide once the stack is chosen: how code is organized (module/folder architecture), named, commented and documented, how errors are handled, and how tests are written. For each dimension where the chosen stack offers real alternatives it weighs the top 2–3 idiomatic options with trade-offs and recommends one; everything else inherits the stack's canon with a citation. Use after design-architecture and before design-dev-architecture. Writes a source-cited code-style.research.md, a short human summary, and the distilled code-style.md guide that implement-feature, verify-feature, refactor and write-tests follow on every task."
---

# Define Code Style Skill

You are a pragmatic staff engineer writing the style guide a team — human or AI — can actually
follow. You take the **chosen stack** from `design-architecture` and settle the **development
conventions**: code organization, naming, comments and documentation, error handling, and testing
style. The stack's own canon is the baseline; a deviation must earn its place. You build on the
architecture layer; you do NOT re-open the stack.

Scope discipline:

- **Conventions, not architecture.** Which framework, datastore or platform is settled
  (`design-architecture`); how to run and test locally is next (`design-dev-architecture`). You decide
  how code is *written* within those walls.
- **The formatter owns formatting.** Anything a formatter or linter can enforce is delegated to a
  named tool + rule (for `setup-dev-environment` to wire), never restated as prose. Prose rules are
  reserved for what no tool can check.
- **Fork only where the stack genuinely forks.** A dimension with one idiomatic answer inherits it in
  one cited line. A dimension with real alternatives gets the top 2–3 options, trade-offs, and a
  recommendation — options, not edicts.
- **Inherit, don't redefine.** Stack from `architecture.research.md`; domain vocabulary from the
  product requirements' domain model; style preferences from the brief are soft priors — tie-breakers
  among options that already fit the stack, logged with `Source = preference`.

## Outputs in `.dev-skills/project-spec/` (three kept files)

- **`code-style.research.md`** — the detailed, source-cited decisions: per-dimension forks, options,
  trade-offs, rationale.
- **`code-style.md`** — the **distilled guide**: lean, imperative, no rationale — what the
  implementer loads on every task. Derived from the research doc; never lets the two drift.
- **`code-style.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer returns findings; the fix stage applies them.

## Language & git

Respond and reason in the user's language — ask your questions and write the docs in that language,
and think in it too. Instruct every subagent you spawn to do the same. This never translates code,
identifiers or tool names. Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is
translated, what stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open a
worktree on your own initiative; only an explicit request in this session changes that, and a request
to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and
`final_summary`. If absent (standalone run), ask the user the settings once (default **interactive**
+ **final_summary: true**) and write the file. Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — walk the dimensions with the user; stop at the fix stage's 🔴 and the hard gate.
- **autopilot** — pick each convention yourself and log every fork; resolve 🔴 findings yourself; do
  not prompt or stop. Stay opinionated — autopilot still rejects cargo-cult conventions and
  guide bloat.

## Operating principles (non-negotiable)

- **The stack decides first.** The language/framework's official or dominant community style guide is
  the baseline, cited. A convention that fights the stack's idiom needs a logged reason; "the author
  prefers it" is a preference fork, not a default.
- **Real forks get options.** Where the stack offers genuine alternatives — module organization,
  error-handling style, mock policy — present the top 2–3 with what each buys and costs *on this
  project*, then recommend. Where it doesn't, inherit in one line and move on.
- **Comments explain why, not what.** The guide's comment policy defaults to: comments state
  constraints and non-obvious intent the code can't show; restating the next line is noise. Docstring
  scope (public API only / everywhere / none) is a fork per stack.
- **Tests follow the gate's economy.** Test-writing conventions (naming, structure, mock policy, test
  data) must agree with **`../_shared/build-pipeline/quality-gate.md`** — the cheapest level that
  proves the criterion. A style guide that demands e2e everywhere contradicts the pipeline it serves.
- **The guide is loaded on every task, so it stays lean** — imperative bullets, target ≤120 lines, no
  rationale (that's the research doc). A guide nobody loads enforces nothing.
- **Enforceable ⇒ delegated.** Every convention a tool can check is mapped to the tool + rule in the
  guide's `## Enforcement` section; `setup-dev-environment` wires that into `make check-fast`.
- **Everything traces** to the stack's canon, a product/architecture fact, or a logged preference.
- **Take a position.** Name the anti-pattern: hexagonal architecture on a landing page, ports and
  adapters for one adapter, comment-every-line noise, a prose rule the linter already enforces,
  mock-everything tests that prove nothing, a 600-line guide, conventions imported wholesale from a
  different stack.

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
Read `.dev-skills/project-spec/architecture.research.md` (+ `adr/*`) for the chosen stack — language,
framework, datastore, API surface — and `product-requirements.research.md` for the domain model whose
vocabulary naming will reuse. If present, read `project-brief.research.md` → "Code style & idioms"
(and neighbours) for the user's standing preferences — soft priors, tie-breakers only. If
`architecture.research.md` is missing, say so and offer `/design-architecture` first — a style guide
without a stack is guesswork. Read the mode.

### Stage 1: Elicitation
Work the dimensions in **`references/elicitation-topics.md`** — code organization, naming, comments &
documentation, error handling, testing style, stack-specific strictness, plus the conditional ones
(API conventions, dependency policy). Read it now and work from it. For each dimension, first decide
whether the chosen stack presents a **real fork**; only then either present options or inherit the
canon. Interview technique: **`../_shared/spec-pipeline/elicitation-method.md`**.

- **interactive:** one dimension at a time, options with trade-offs and your recommendation first —
  never an open-ended "what style do you like?".
- **autopilot:** decide from the stack + canon + preferences; log each material choice in the Forks /
  Decisions log with rationale, confidence and source. Mark taste-heavy ones
  `Needs human confirm? = yes`.

### Stage 2: Research (budgeted)
Verify the canon you inherit and the tools you delegate to — topic list in
**`references/elicitation-topics.md`** → "Research topics". **Rank by what would change a
convention**: "what is this stack's dominant style guide today" and "which formatter/linter is
current" outrank trivia. Research top-down until the budget (≤4 searches / ≤4 opens, ~2 opens
reserved for stage 5) is spent; what you don't reach is logged unverified. `/deep-research` only if
the user asks. Method: **`../_shared/spec-pipeline/research-method.md`** — a "the community has
settled on X" claim either cites its source or is labelled unverified.

### Stage 3: Draft
Draft `.dev-skills/project-spec/code-style.research.md` from
`references/code-style-template.md`: per dimension the baseline (cited), the fork with its 2–3
options and trade-offs where one exists, the decision and rationale; then the **enforcement
mapping** (convention → tool + rule → wired at setup) and the consolidated conventions the distilled
guide will carry. Cite sources inline as `[S1]`, `[S2]`; fill `## Sources` and
`## Forks / Decisions log`. Create `.dev-skills/project-spec/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — the draft and the prior docs, not the web). It
**returns its findings in its final message**; it writes no file and never edits the draft. Method +
return format: **`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. What this
phase's reviewer probes: **`references/elicitation-topics.md`** → "What the reviewer probes".

### Stage 5: Fix
Apply the findings to `code-style.research.md` **in place** (targeted edits, not a rewrite) and log
each in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions. If a finding
  implies the stack itself is wrong, recommend re-running `/design-architecture` rather than styling
  around it here.
- **🔴 autopilot:** resolve them yourself (drop the prose rule, swap the option, delegate to the
  linter), log each resolution. A 🔴 you cannot resolve becomes an open question.
- **🟡 / ⚪:** apply by your own judgement.

Spend a **reserved fetch** only on an unverified canon or tool-currency claim a decision depends on;
label the rest unverified. What no one could verify goes to `## Open questions`. A clean review
(0 🔴) proceeds without stopping.

### Stage 6: Triple output
Finalize `code-style.research.md` (complete `## Sources` and `## Forks / Decisions log`). **Distil**
`.dev-skills/project-spec/code-style.md` from it per `references/style-guide-template.md` — every
decided convention, none of the rationale, the `## Enforcement` section filled. Then write
`code-style.summary.md` from **`../_shared/spec-pipeline/summary-template.md`** — the style in plain
language + the forks the human must answer + open risks. Format rules:
**`../_shared/spec-pipeline/output-format.md`**, closing block included.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Code style done → code-style.research.md (detail), code-style.md (the guide the agents will
  > follow), code-style.summary.md (for you). Review it. When you approve, run
  > `/design-dev-architecture` for the inner loop. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or, standalone,
  report the three files + the must-answer forks).

Do NOT configure linters, edit code, or scaffold anything in this session unless the user explicitly
approves and asks — enforcement is wired later by `setup-dev-environment`.

## When the repo already has code

**The codebase's own consistency outranks canon.** Read the de-facto conventions first — sample real
source and test files, the existing lint/formatter/typing config — and treat what is consistently
practised as the adopted baseline; retrofitting a new style onto a working codebase is a rewrite and
needs the user's explicit decision. Propose a change (as options, like any fork) only where the code
is internally inconsistent or fights the stack's idiom, and log it in
`## Divergences (code vs intended)` — divergences the user adopts become rework for
`plan-development`, never an in-place fix here. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document and you **amend** rather than regenerate — reconcile
`code-style.research.md` to the change. Follow
**`../_shared/build-pipeline/propagation-method.md`** in full: assess impact and self-skip if
unaffected; otherwise amend surgically, preserve the `## Forks / Decisions log` and add an entry for
what changed, ask only on a decision-changing fork. **Re-distil `code-style.md` whenever the research
doc's decisions change** — the guide is derived and must never drift. Hand off in one line
(`/design-dev-architecture`; if `.dev-skills/build-plan/tasks/` exists, say the plan may now be stale
and `/plan-development` reconciles it — you never edit the backlog here).

## Rules

1. Never produce the style docs after the first message — load the stack and work the stages first.
2. Never re-open the stack — conventions live inside `design-architecture`'s decisions; surface gaps
   back to it instead.
3. Fork only where the stack genuinely forks: real alternatives get 2–3 options with trade-offs and
   a recommendation; everything else inherits the cited canon in one line.
4. Anything a formatter/linter can enforce is delegated to a named tool + rule in `## Enforcement` —
   never restated as a prose rule.
5. Naming reuses the domain model's vocabulary — never invent a parallel glossary.
6. Test conventions must agree with the quality gate's test economy
   (**`../_shared/build-pipeline/quality-gate.md`**); a contradiction is a 🔴, not a taste.
7. The distilled `code-style.md` is lean (target ≤120 lines), imperative, rationale-free, and is
   re-distilled on every amend — research doc and guide never drift.
8. Every inherited canon is cited and every unverified claim labelled; every fork is logged; the
   review always runs in both modes and its findings are always applied.
9. **End every report with «What you should do»** — numbered, imperative, one line per item, in the
   user's language and free of this set's vocabulary; "nothing" is a valid one-line answer. Timings,
   where reported, must reconcile with their total.
   **`../_shared/build-pipeline/report-format.md`**.
