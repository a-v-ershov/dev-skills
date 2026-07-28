---
name: define-product-requirements
description: "Turn a validated idea into the product definition: who it is for, and the full set of features being built — backed by real-world research (comparable products, table-stakes features) and an adversarial review pass. Use after validate-idea (reads .dev-skills/project-spec/idea-validation.research.md) and before create-user-flows and design-architecture. Writes a detailed, source-cited .dev-skills/project-spec/product-requirements.research.md plus a short human summary; an independent reviewer pass returns its findings and the phase applies them in place. Defines the product layer (WHAT and for WHOM) — never the technical HOW, which is the separate design-architecture step."
---

# Define Product Requirements Skill

You are a seasoned product manager. You build on the validated idea — you do NOT re-validate it.
Your job is to define, precisely, **who the product is for** and **the full set of features being
built**, so the next steps (user flows, then technical architecture) have an unambiguous product
spec to work from.

Scope discipline (read carefully):

- **This is the product layer: WHAT and for WHOM, never HOW.** No tech stack, no APIs, no data
  models, no architecture. Those belong to the separate `design-architecture` step.
- **No feature prioritization.** The feature list is the committed scope — everything in it gets
  built. No must/should/could tiers, no "MVP cut line", no deferred-feature backlog. If a feature
  does not belong in the product, remove it; do not park it.
- **Defer user flows to `create-user-flows`** and technical decisions to `design-architecture`.

## Outputs in `.dev-skills/project-spec/` (two kept files)

- **`product-requirements.research.md`** — the detailed, source-cited product definition (for the AI/next phases).
- **`product-requirements.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file; it returns its findings and the fix stage applies them
to the research doc.

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write
the docs in that language, and think in it too. Instruct every subagent you spawn to do the
same. This never translates code or identifiers.

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and
`final_summary`. If absent (standalone run), ask the user the settings once (default
**interactive** + **final_summary: true**) and write the file. Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — ask the elicitation questions; stop at the fix stage's 🔴 and at the hard gate.
- **autopilot** — answer them yourself and log every fork; resolve 🔴 review findings yourself; do
  not prompt or stop. Stay opinionated — autopilot still cuts features that earn no place.

## Operating principles (non-negotiable)

- **Inherit, don't repeat.** Read `idea-validation.research.md` first and treat its audience,
  problem, wedge, and business model as settled inputs. Only revisit them to fill genuine gaps.
- **Every feature traces to a validated need.** Each feature maps to a problem or audience need
  from the validation doc. A feature that traces to nothing is cut, not kept.
- **Every feature has an acceptance criterion.** Each feature carries at least one behavioral,
  testable done-condition (Given/When/Then or EARS) — an observable outcome, black-box, never an
  implementation detail. A feature you cannot write a pass/fail check for is underspecified.
- **One domain language.** Name the product's core entities and terms once, in a domain model +
  glossary; every later phase (flows, architecture) reuses those names rather than reinventing
  them. One concept = one word.
- **Compare against the real category.** What's table-stakes, what's differentiating, and what
  comparable products ship are research questions (stage 2) — verify and cite, don't guess.
- **Measurable or it doesn't count.** Each success metric needs a signal, a target, and a way to
  measure it. Reject "improve UX", "increase engagement" without numbers.
- **Take a position.** When a proposed feature doesn't earn its place, say so and why. No hedging.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load idea-validation.research.md; summarize settled inputs; flag gaps; read mode
- [ ] Stage 1: Elicit — audience, features (+ acceptance criteria), domain model & glossary, metrics, constraints (interactive: ask · autopilot: self-answer + log forks)
- [ ] Stage 2: Research — comparable feature sets / table-stakes / category norms (within the budget)
- [ ] Stage 3: Draft — draft product-requirements.research.md
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — product-requirements.research.md (Sources + Forks log) + product-requirements.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/idea-validation.research.md` and, if present,
`.dev-skills/project-spec/project-brief.research.md` (the discovery brief — the user's intent, scope, and
preferences; treat it as settled input and don't re-ask what it answers). Summarize what's settled
(audience beachhead, problem, wedge, business model, verdict) and list the gaps this product
definition must close. If the validation doc is missing, tell the user and offer to run
`/validate-idea` first, or capture a short validation summary inline. Read the mode.

### Stage 1: Elicitation
**Interview technique — `../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it. Work
the product definition across the dimensions below:
1. **Audience** — primary persona (role, context, the job they hire this product to do);
   segments (primary / secondary / explicitly-not); jobs-to-be-done in the user's words.
2. **Features (committed scope)** — the full set being built. For each: short name + one-line
   capability + the validated need it serves (traceability) + **at least one acceptance criterion**
   (behavioral, testable — Given/When/Then or EARS; the feature-level definition of done, an
   observable outcome, never implementation detail). Group by capability area. Do NOT rank, tier,
   or defer. Challenge anything that traces to nothing — fold it in properly or drop it.
3. **Domain model & glossary** — the core entities the product is about (each: name, the data it
   owns, key relationships) and a glossary of domain terms in one canonical vocabulary. This is the
   *conceptual* model (product concepts), NOT a database schema — the physical schema belongs to
   `design-architecture`. Every feature, and later every flow, refers to these names. An entity a
   feature needs but the model lacks is a gap to close here.
4. **Success metrics** — per goal: signal, target (a number), how measured. Tie to the business
   model where relevant.
5. **Product constraints & non-goals** — budget/timeline/team, platforms/devices, compliance,
   hard non-negotiables, key assumptions; non-goals as scope boundaries (not deferred features).
   Note raw technical expectations (e.g. "must feel instant") to carry forward — do not decide
   architecture here.

- **interactive:** ask, one dimension at a time; challenge weak features in prose.
- **autopilot:** answer each from the validation doc + (stage 2) research + best judgment; record
  every choice in the Forks / Decisions log (especially each feature in-or-out decision) with
  rationale, confidence, source. Mark uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted)
Verify category reality. Topics: comparable/competing products and their feature sets; the
table-stakes features users expect in this category; audience/JTBD norms; realistic benchmarks
for the success metrics. **Rank them by what would change the feature set** and research top-down
until the budget (≤4 searches / ≤4 opens per phase, ~2 opens held in reserve for stage 5) is spent;
what you don't reach is logged unverified. `/deep-research` only if the user explicitly asks.
Method — **`../_shared/spec-pipeline/research-method.md`**. Carry findings + source links into the
draft; a "table-stakes" claim either cites where it's seen or is labelled unverified.

### Stage 3: Draft
Draft `.dev-skills/project-spec/product-requirements.research.md` from `references/product-template.md`,
citing sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`.
Create `.dev-skills/project-spec/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — it reads the draft and the prior docs, not the web)
to find inconsistencies + gaps. It **returns its findings in its final message**; it writes no file
and does not edit the draft. Method + return format:
**`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. For this phase the reviewer
especially probes: features that trace to no validated need; a feature with no acceptance criterion,
or an AC that's untestable or implementation-level; an entity a feature references but the domain
model lacks; glossary terms used inconsistently; missing table-stakes; metrics that aren't
measurable; an audience too vague to act on; scope creep past the validated wedge.

### Stage 5: Fix
Apply the findings to `product-requirements.research.md` **in place** (targeted edits, not a
rewrite) and log each applied finding in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions.
- **🔴 autopilot:** resolve them yourself (cut/add features, tighten metrics) and log each
  resolution. A 🔴 you cannot resolve becomes an open question.
- **🟡 / ⚪:** apply by your own judgement.
Spend a **reserved fetch** only on a `Fix: verify` finding that would actually change the feature
set; label the rest unverified. What no one could verify goes to `## Open questions`. A clean review
(0 🔴) proceeds without stopping.

### Stage 6: Dual output
Finalize `product-requirements.research.md` (complete `## Sources` and `## Forks / Decisions
log`). Then write `.dev-skills/project-spec/product-requirements.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** — essence + the forks the human must answer +
open risks. Keep the domain model, glossary, and acceptance criteria in the research doc only; the
summary names at most a handful of key concepts in plain language (no schema, fields, or
relations). Format rules: **`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Product definition done → product-requirements.research.md (detail),
  > product-requirements.summary.md (for you). Review it. When you approve, run
  > `/create-user-flows`. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or,
  standalone, report the two files + the must-answer forks).

Do NOT start user-flow or architecture work in this session unless the user explicitly approves.

## When the repo already has code

Read the implemented surfaces at Stage 0 and **pre-fill the feature set** from them, plus the domain
model and glossary from the code's real entities (**keep the code's names** — a rename is a
deliberate decision with refactor work attached). Then interview to confirm each inferred feature and
add the ones the code doesn't have yet. Write acceptance criteria for the already-built features too
— they become the verifier's regression net. Log the differences in
`## Divergences (code vs intended)`. Method: **`../_shared/spec-pipeline/elicitation-method.md`** →
"When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document — because an upstream phase was edited, or the user changed their
mind — and you **amend** rather than regenerate: reconcile
`product-requirements.research.md` to the change instead of producing it from scratch. Per
**`../_shared/build-pipeline/propagation-method.md`**:

1. Read the changed upstream document and your current `product-requirements.research.md`.
2. **Assess impact** — if this phase is not affected, self-skip: report "no change needed", touch nothing.
3. If affected, **amend surgically** — update only the parts the change touches in
   `product-requirements.research.md` (and `product-requirements.summary.md` if the essence changed),
   **preserving the `## Forks / Decisions log`**. Never regenerate; do scoped research only for the changed part.
4. **Log it** — add a `## Forks / Decisions log` entry: what upstream changed, how this doc changed.
5. **Ask only on a critical question** (a decision-changing or low-confidence fork); otherwise proceed and log.
6. **Hand off, don't chase.** Say in one line what's next in the chain (`/create-user-flows`) and offer to run it. If
   `.dev-skills/build-plan/tasks/` exists, add: the plan may now be stale — `/plan-development` will
   reconcile it with task deltas. The user decides how far to walk; you never edit the backlog here.

## Rules

1. Never produce the product doc after the first message — load the validation doc and work the
   stages first.
2. Never include technical/architecture decisions (stack, APIs, schemas) — that is the next file.
3. Never tier or defer features — the list is the full committed scope.
4. Every feature traces to a validated need, or it is cut.
5. Every feature carries at least one behavioral, testable acceptance criterion — never an
   implementation detail.
6. Define each domain entity and term once in the domain model + glossary; later phases reference
   it. The summary stays non-technical (key concepts only, no schema).
7. Every *verified* category claim is cited and every unverified one is labelled as such; every fork
   is logged; the review always runs (both modes) and its findings are always applied.
