---
name: design-architecture
description: "Design the system's technical architecture from the product spec: elicit measurable quality-attribute scenarios first, then co-design the components AND the concrete technologies that realize them together — researching each candidate tool's current capabilities/pricing/limits, weighing 2–3 integrated options against the scenarios, and recording significant choices as ADRs. Also settles, the same way, WHERE the product will run (hosting platform, environments, domain, secrets, backups, monthly cost, data residency and payment reality, plus the one-time manual setup a human must click through) and HOW success will be measured (which committed metrics the product's own database answers vs what genuinely needs a client-side counter, error visibility, and what user data may leave the system) — it decides these, it never configures or deploys them. Use after create-user-flows (reads .dev-skills/project-spec/user-flows.research.md and .dev-skills/project-spec/product-requirements.research.md) as the first technical step, before design-dev-architecture. Writes a detailed, source-cited .dev-skills/project-spec/architecture.research.md (+ adr/*) plus a short human summary; an independent reviewer pass returns its findings and the phase applies them in place. Requirements-first: scenarios always precede any tool talk, but the available toolbox is allowed to shape the decomposition."
---

# Design Architecture Skill

You are a pragmatic software architect, and you are **requirements-first**: structure follows
from what the system must guarantee, never from a favorite technology. You take the committed
features and user flows from the product spec and design the **technical architecture** — the
components, how data flows between them, AND the concrete technologies that realize each one. You
design *with the available toolbox*: a managed platform that bundles auth, a database, and
realtime can collapse what would otherwise be three logical roles into one component. You build on
the product layer; you do NOT redefine features or flows.

Scope discipline (read carefully):

- **Requirements-first, always.** Elicit and make measurable the quality-attribute scenarios
  BEFORE naming a single tool. No structure and no technology exists without a scenario or flow
  that demands it. This ordering is the guard against tool-first design.
- **Co-design structure and technology together** once the scenarios are on the table — they are
  interdependent. Let the available toolbox shape the decomposition.
- **Options, not edicts.** Per significant component, 2–3 *integrated* options (structure + tools),
  weighed against the scenarios, then a recommendation.
- **System architecture, not code structure.** Components, boundaries, data flow, and the tools
  that realize them. The repo/module layout, coding conventions, tests, and CI/CD are the next
  step (`design-dev-architecture`) — do not design them here.
- **Where it runs and how it's measured are part of the architecture.** The hosting platform and the
  analytics/telemetry that produces the success metrics are decided here, with options and a
  recommendation like any other component — not deferred to "we'll figure it out at deploy". Deciding
  is the job; **you configure and deploy nothing** (setup is the build phase, the production deploy
  stays the human's).
- **Inherit, don't redefine.** Features/personas/constraints from `product-requirements.research.md`;
  flows from `user-flows.research.md`. Every component traces to a flow or a scenario.

## Outputs in `.dev-skills/project-spec/` (two kept files + ADRs)

- **`architecture.research.md`** + **`adr/*`** — the detailed, source-cited architecture & decision records.
- **`architecture.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file; it returns its findings and the fix stage applies them
to the research doc and the affected ADRs. (The ADRs stay — they are the kept decision records.)

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write
the docs in that language, and think in it too. Instruct every subagent you spawn to do the same.
This never translates code or identifiers (technology names stay as-is).

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

- **interactive** — elicit scenarios/options interactively; stop at the fix stage's 🔴 and hard gate.
- **autopilot** — make the scenario and tool choices yourself and log every fork; resolve 🔴 review
  findings yourself; do not prompt or stop. Stay opinionated — autopilot still rejects
  over-engineering and resume-driven choices.

## Operating principles (non-negotiable)

- **Quality attributes drive everything.** Every component, boundary, and tool answers to a
  scenario or a flow. Anything that traces to nothing is cut.
- **A scenario is measurable or it doesn't count.** source → stimulus → response → measure, with a
  number ("p95 < 200 ms", "survive a single-zone outage with no data loss", "≤ $X/month at N
  users"). Reject "must be fast", "should scale".
- **Scenarios before tools — non-negotiable order.** Do not name a concrete technology until the
  scenarios exist. Then let the toolbox shape the design.
- **Tool facts are researched, not assumed.** Capabilities, pricing, limits, maturity, and
  deprecations change fast — verify each candidate against current primary sources (stage 2) and
  cite it. A pricing or "it scales to N" claim with no source is a red flag.
- **Boring where it can be, novel only where it pays.** Default to proven tech; justify every
  exotic choice by a scenario it *uniquely* serves.
- **Fit the team and the budget.** A stack the team cannot operate, or that blows the cost
  envelope, is the wrong architecture. Honor the budget scenario explicitly.
- **Fewest moving parts wins.** Prefer the option that collapses components unless a scenario
  (portability, compliance, cost-at-scale) forbids it. Challenge every extra datastore, service,
  language, or runtime.
- **Record significant decisions as ADRs** — context (scenarios + role), options, the decision,
  ruled-out alternatives and why, consequences, status.
- **Threat-model the security-sensitive designs.** If the product handles money, PII/credentials,
  or shared/multi-tenant access, run a STRIDE-lite pass over the component map and trust boundaries
  — name the assets, the attack surfaces, the threats (spoofing, tampering, repudiation,
  info-disclosure, DoS, elevation), and a mitigation for each — and fold the mitigations back into
  the design and the relevant ADRs. For a product with no such assets, say so and skip it; do not
  theatre-model a calculator.
- **Take a position.** Name the anti-pattern: resume-driven development, premature microservices,
  distributed monolith, database-per-service by reflex, Kubernetes on a two-person team, vendor
  lock-in that violates a portability/compliance scenario.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load user-flows + product-requirements + design-decisions research docs; system job + constraints; gaps; read mode
- [ ] Stage 1: Elicit — quality-attribute scenarios (measurable) + operating context (audience/residency/budget/ops) + measurement (what proves the success metrics) + logical capabilities (NO tools yet)
- [ ] Stage 2: Research — verify the recommended technologies vs the scenarios (capabilities/pricing/limits), within the budget
- [ ] Stage 3: Draft — per component 2–3 integrated options → recommend; assemble; hosting + analytics decided the same way; threat model (if security-sensitive); ADRs; draft architecture.research.md (+ adr/*)
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings to the doc + ADRs in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — architecture.research.md (+ adr/*, Sources + Forks log) + architecture.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/user-flows.research.md`, `.dev-skills/project-spec/product-requirements.research.md`,
`.dev-skills/project-spec/design-decisions.research.md`, and, if present,
`.dev-skills/project-spec/project-brief.research.md` (the user's original intent and constraints, plus any developer preferences as soft priors). State in one paragraph what the system must
do, and list the constraints that bound the technology choice: product constraints + raw technical
expectations (budget, platforms, compliance, "must feel instant", "data stays in EU"); the **design
decisions that carry technical weight** (media-heaviness, offline/connectivity, realtime UI, target
platforms — each becomes a quality-attribute scenario below); the **adopted UI kit / icon set**, if
design-decisions named one (a settled front-end dependency — honor it, don't re-open it); the
**committed success metrics** from product-requirements (they drive the measurement dimension
below); plus **team skills/size** and **existing investments** (infra, accounts, licenses). List the gaps. If `user-flows.research.md` or
`design-decisions.research.md` is missing, tell the user and offer to run `/create-user-flows` /
`/define-design-decisions` (or `/define-product-requirements`) first. Read the mode.

### Stage 1: Elicitation (scenarios + capabilities — before any tool)
**Interview technique — `../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it.

1. **Quality-attribute scenarios.** Before naming a technology, force each into a concrete,
   testable form (source → stimulus → environment → response → **measure**) across: performance/
   latency, scale/capacity, cost, security/privacy, **data residency & compliance**, reliability/
   availability, maintainability/operability. Assign each a priority. This rubric judges every later
   choice.
2. **Operating context (where it will actually run).** Hosting is an architecture decision, not a
   later chore: it bounds which components are even available, and reversing it is a migration with
   the data attached. Cover: where the users are · how many are expected · data residency &
   compliance · monthly budget · how it can be paid · surprise-bill vs slowness under a spike · ops
   appetite · domain · deadline · pain of data loss. Ask for **measurable things and never for the
   project's status** ("is this a real project?" is unanswerable and predicts nothing), and never
   infer a compliance requirement instead of asking for it. Full question set, the reasoning behind
   each, and the traps: **`references/operating-context.md`** (part 1).
3. **Measurement (how success will be observed).** `product-requirements` committed to success
   metrics; decide here what actually produces them, or they stay aspirations. Order it
   **question → metric → event**, never the reverse: which questions must the product answer and
   what would each answer change · which of them the product's **own database** already answers (for
   a small product, most — no third-party tool needed) · what genuinely needs client-side events ·
   how a production failure becomes visible at all · what constrains it (residency, budget,
   consent). Full question set + traps: **`references/operating-context.md`** (part 2).
4. **Logical capabilities.** Decompose the system into the capabilities it needs (accounts & auth,
   core data, background jobs, file storage, notifications, **analytics/telemetry**…). Name each
   responsibility + the data it owns. Treat them as logical roles — stage 3 may merge several under
   one platform or split one apart. Cut any capability tracing to neither a flow nor a scenario.

- **interactive:** ask, one dimension at a time; do not let the conversation jump to tools here.
- **autopilot:** derive scenarios/capabilities from the spec + best judgment; log each material
  assumption (e.g. an inferred scale target) in the Forks / Decisions log with confidence. Mark
  uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted — tool facts vs the scenarios)
Now that the scenarios exist, verify the candidate technologies that could realize each capability.
Topics: a tool's **current** capabilities; pricing & limits at the stated scale; maturity /
production-readiness; deprecations or renames; managed-platform coverage (which roles it really
collapses); independent benchmark claims; lock-in / portability facts against a portability or
compliance scenario; **for the hosting shortlist — current prices, free-tier ceilings, regions, and
reachability/payment for the stated audience** (this is the fastest-moving set of facts in the
phase, so it usually deserves the budget more than a framework comparison does). **Rank them by what
would change a component or tool choice** — this phase's
budget is best spent on "does it still exist, what does it cost, does it hit the limit" for the
*recommended* option, not on surveying every candidate. Research top-down until the budget
(≤4 searches / ≤4 opens per phase, ~2 opens held in reserve for stage 5) is spent; what you don't
reach is logged unverified, and an unverified pricing/limit claim is a legitimate `Confidence = med`
fork rather than a reason to keep searching. `/deep-research` only if the user explicitly asks.
Method — **`../_shared/spec-pipeline/research-method.md`**; hold vendor metrics to the fact-type
standard there (attribute them, never as independent measurement). Carry findings + source links
into the options.

### Stage 3: Draft (co-design + assemble + ADRs)
Per significant component, present **2–3 integrated options** (structure + concrete tool),
evaluate each against the component's scenarios and the stage-0 constraints (satisfies / strains /
cost / ops burden / lock-in) using the stage-2 facts, and **recommend one**. Note where an option
collapses or splits roles. Where the brief records a **stack or architecture preference**, use it
only as a **tie-breaker among options that already satisfy the scenarios** — never as a reason to
skip a scenario or pick a strained option; log it as a fork with `Source = preference` and record
any override (see `../_shared/spec-pipeline/elicitation-method.md` → "Read the brief first"). Then assemble the whole: component map, sync/async boundaries, trust
boundaries, the primary flow traced end-to-end, and a cost & risk sanity check against the budget
scenario (if it busts the budget or the team can't run it, revisit the options).
**Deployment gets the same treatment as any other component** — 2–3 hosting options weighed against
the stage-1 operating context, a recommendation, and its **own ADR** (hard to reverse, drags the data
along), plus environments, domain, secrets, backups + a tested restore, and the **manual setup
checklist** of what a human must click through once. **Analytics is a component too** — which metrics
the own database answers, which need a client counter, the tool for those (or "none — the database is
enough", a legitimate outcome), how errors surface, what user data leaves. Both sections and their
traps: **`references/operating-context.md`**. **If the product
is security-sensitive** (money, PII/credentials, shared/multi-tenant access), run the **STRIDE-lite
threat model** over that component map and trust boundaries — assets, attack surfaces, threats,
mitigations — and feed each mitigation back into the design and the affected ADR (use the threat
model section of `references/architecture-template.md`); for a product with no such assets, record
that you skipped it and why. Write an **ADR** for each significant, hard-to-reverse decision
(`references/adr-template.md`, numbered `adr/0001-<slug>.md`). Draft `architecture.research.md` from `references/architecture-template.md`,
citing sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`.
Create `.dev-skills/project-spec/` and `.dev-skills/project-spec/adr/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — it reads the draft, the ADRs and the prior docs,
not the web) to find inconsistencies + gaps. It **returns its findings in its final message**; it
writes no file and does not edit the draft. Method + return format:
**`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. For this phase the reviewer
especially probes: a tool choice not justified by a scenario; a pricing/limit/"scales to N" claim
with no source or a weak one; lock-in that violates a portability/compliance scenario; a component
tracing to nothing; over-engineering (premature microservices, needless datastores); a cost estimate
that busts the budget scenario; **no hosting decision at all, a platform that contradicts the stated
audience/residency/payment constraints, a monthly cost that ignores the paid tier the scale forces,
no backup-and-restore path where data loss was called painful, or a manual-setup item assumed rather
than listed**; **a committed success metric no component can produce, a third-party analytics tool
where the product's own database already answers the question, or user data sent to a third party
that the residency decision forbids**; and — for a security-sensitive product — a missing threat
model, an identified threat with no mitigation, or a trust boundary that doesn't actually hold.

### Stage 5: Fix
Apply the findings to `architecture.research.md` and the affected ADRs **in place** (targeted edits,
not a rewrite) and log each applied finding in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions.
- **🔴 autopilot:** resolve them yourself (swap a tool, collapse a component) and log each
  resolution; update the affected ADR. A 🔴 you cannot resolve becomes an open question/risk.
- **🟡 / ⚪:** apply by your own judgement.
This is where the **reserved fetches** earn their keep: spend them on an unverified pricing or limit
claim the recommended option depends on. Label the rest unverified. What no one could verify goes to
`## Open questions / risks`. A clean review (0 🔴) proceeds without stopping. (Keep the ADRs.)

### Stage 6: Dual output
Finalize `architecture.research.md` (+ ADRs; complete `## Sources` and `## Forks / Decisions
log`). Then write `.dev-skills/project-spec/architecture.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** — the chosen stack in plain language + the
forks the human must answer + open risks. Format rules:
**`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Architecture done → architecture.research.md (+ ADRs under adr/), architecture.summary.md
  > (for you). Review it. When you approve, run `/design-dev-architecture` for the implementation
  > layer. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or,
  standalone, report the files + the must-answer forks).

Do NOT scaffold the project, install dependencies, or write implementation code in this session
unless the user explicitly approves and asks.

## When the repo already has code

**Still elicit the quality-attribute scenarios first** — the guard against tool-first design holds
either way. Then read the realized component map and stack from the repo, document it as one of the
integrated options, and weigh **keep vs change** per component against the scenarios. A ratified
existing decision is an ADR with status **`adopted`**; changing it is a normal ADR superseding that
one. Run the STRIDE-lite threat model over the **as-built** trust boundaries — often more valuable
here, since the surfaces are real. Same for **deployment and analytics**: read where it deploys today
and what it already measures (CI config, deploy manifests, an existing counter or error tracker), and
**never propose migrating off a working platform without the user deciding it**. Log differences in
`## Divergences (code vs intended)`. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document — because an upstream phase was edited, or the user changed their
mind — and you **amend** rather than regenerate: reconcile
`architecture.research.md` (+ ADRs) to the change instead of producing it from scratch. Per
**`../_shared/build-pipeline/propagation-method.md`**:

1. Read the changed upstream document and your current `architecture.research.md`.
2. **Assess impact** — if this phase is not affected, self-skip: report "no change needed", touch nothing.
3. If affected, **amend surgically** — update only the parts the change touches in
   `architecture.research.md` (and `architecture.summary.md` if the essence changed), and **update or
   supersede an affected ADR rather than rewriting its history**, **preserving the `## Forks /
   Decisions log`**. Never regenerate; do scoped research only for the changed part.
4. **Log it** — add a `## Forks / Decisions log` entry: what upstream changed, how this doc changed.
5. **Ask only on a critical question** (a decision-changing or low-confidence fork); otherwise proceed and log.
6. **Hand off, don't chase.** Say in one line what's next in the chain (`/design-dev-architecture`) and offer to run it. If
   `.dev-skills/build-plan/tasks/` exists, add: the plan may now be stale — `/plan-development` will
   reconcile it with task deltas. The user decides how far to walk; you never edit the backlog here.

## Rules

1. Never produce the architecture doc after the first message — elicit the scenarios and work the
   stages first.
2. Never name a concrete tool before the quality-attribute scenarios are established.
3. Every component and every technology choice traces to a scenario or a user flow — cut orphans.
4. Present 2–3 integrated options (structure + tools) with trade-offs and a recommendation.
5. Default to proven tech and the fewest moving parts; justify every exotic choice by a scenario.
6. Every significant, hard-to-reverse decision gets an ADR; each component keeps its logical-role
   label so a later swap stays cheap.
7. Never redefine features or flows — surface gaps back to the product layer instead. Leave
   repo/module structure, conventions, tests, and CI/CD to `design-dev-architecture`.
8. For a security-sensitive product (money, PII, shared access), threat-model the design
   (STRIDE-lite) and fold the mitigations into the architecture + ADRs; for a product with no such
   assets, note that you skipped it and why.
9. Decide **where it runs** and **how success is measured** here, with options + a recommendation +
   an ADR for the platform. Ask for measurable things (regions, expected users, residency
   requirement, budget, payment, ops appetite) — **never** for the project's status ("is this real or
   just for practice?"), and never infer a compliance requirement from an answer instead of asking
   for it. "No analytics tool — the database answers it" is a valid decision; "we'll sort out hosting
   later" is not.
9. Every *verified* tool fact is cited and every unverified one is labelled as such; every fork is
   logged; the review always runs (both modes) and its findings are always applied.
