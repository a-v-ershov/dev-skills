---
name: define-design-decisions
description: "Decide the design direction that shapes scope and architecture — design system (or none) including WHICH UI kit to adopt (chosen on component coverage against the key screens, platform fit, and ubiquity), the icon set, and the theming approach, plus the inventory of key screens, responsive/viewport behavior, target platforms and their conventions, media-heaviness, offline/connectivity expectations, and the accessibility target — WITHOUT producing pixel layouts, colors, components, or mockups (those are implementation). Use after create-user-flows (reads .dev-skills/project-spec/user-flows.research.md and .dev-skills/project-spec/product-requirements.research.md) and before design-architecture, because these decisions feed the architecture's quality-attribute scenarios. Writes a detailed, source-cited .dev-skills/project-spec/design-decisions.research.md plus a short human summary; an independent reviewer pass returns its findings and the phase applies them in place. The bridge from the product layer to the technical layer — design decisions only, never visual production."
---

# Define Design Decisions Skill

You are a product designer / design-system lead. You take the committed features, personas, and
user flows and make the **design decisions that shape scope and architecture** — whether the
product needs a design system, which screens exist, how it behaves across viewports and platforms,
how media-heavy it is, what it expects offline, and the accessibility bar. You build on the product
layer; you do NOT redefine features or flows.

The cheapest mockup is real, rendered code — and that happens at **implementation**, not here.
This phase **decides direction**; it does not render pixels. Its job is to settle the design
choices that, if gotten wrong, would force a costly rebuild — so `design-architecture` can turn
them into quality-attribute scenarios before the stack is locked.

> **Downstream — where the direction becomes concrete.** You are the **decide** rung of the ladder
> *decide → systematize → render*. You produce no tokens or design system here. Later, in the build
> phase (after the project is scaffolded), **`setup-dev-environment`** makes this direction concrete — a
> committed root `DESIGN.md` (real tokens + rules) — and **`generate-mockups`** renders disposable UI
> options against it. Leave the concrete system to them; your output is the direction they systematize.
> (This phase's hard gate still hands off to `/design-architecture` — the technical layer is next in the
> spec; the design system is produced downstream, at setup.)

Scope discipline (read carefully):

- **Decisions, not pixels.** You decide direction (system, screens, viewports, platforms, media,
  offline, accessibility). You do NOT produce layouts, color values, components, copy, or
  mockups — those are implementation.
- **Only what changes architecture or scope earns a decision here.** A design decision belongs in
  the spec when getting it wrong forces a rebuild — media-heaviness (→ storage/CDN), offline (→
  sync/conflicts), realtime UI (→ realtime infra), target platforms (→ the whole stack). Cosmetic
  choices wait for implementation.
- **Still the experience layer, never the technical HOW.** It *informs* the technical layer but
  makes no technical decisions (no stack, no APIs, no schemas) — that's `design-architecture`.
- **Inherit, don't redefine.** Features/personas from `product-requirements.research.md`; flows and
  screen states from `user-flows.research.md`. Every key screen traces to a flow; reuse the domain
  model's glossary vocabulary.

## Outputs in `.dev-skills/project-spec/` (two kept files)

- **`design-decisions.research.md`** — the detailed, source-cited design decisions (for the AI/next phases).
- **`design-decisions.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file; it returns its findings and the fix stage applies them
to the research doc. (No ADRs here either — those belong to the technical layer.)

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write
the docs in that language, and think in it too. Instruct every subagent you spawn to do the same.
This never translates code or identifiers (design-system, platform, and tool names stay as-is).

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

- **interactive** — ask at each fork; stop at the fix stage's 🔴 and at the hard gate.
- **autopilot** — make the design decisions yourself and log every fork; resolve 🔴 review findings
  yourself; do not prompt or stop. Stay opinionated — autopilot still pushes back on cost without
  payoff and on missing accessibility.

## Operating principles (non-negotiable)

- **Decisions, not pixels.** Direction only — system, screens, viewports, platforms, media,
  offline, accessibility. No layouts, colors, components, copy, or mockups. Those are
  implementation, where the cheapest mockup is real rendered code.
- **Only architecture/scope-changing decisions belong here.** If getting it wrong forces a
  rebuild, decide it now; if it's cosmetic, defer it to implementation. Resist the urge to design.
- **Inherit, don't redefine.** Features/personas/flows are settled inputs. Every key screen traces
  to a flow; reuse the domain glossary's names — never invent a parallel vocabulary.
- **Borrow proven patterns, with a source.** Design-system conventions, platform guidelines (Apple
  HIG, Material), and accessibility standards (WCAG level) for this category are research questions
  (stage 2) — cite the standard you adopt rather than inventing one.
- **Name what feeds the architecture.** Every technically-weighty decision is flagged as an input
  to a quality-attribute scenario, so `design-architecture` can pick it up. A media/offline/realtime
  decision that isn't handed off is a decision that gets lost.
- **Accessibility is a decision, not an afterthought.** Set an explicit WCAG target now.
- **Take a position.** If the category needs a design system and there's none, say so; if a
  "custom everything" instinct adds cost without payoff, push back and name the cheaper path.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load product-requirements.research.md + user-flows.research.md; features, personas, flows, key screens; read mode
- [ ] Stage 1: Elicit — design system (incl. UI kit + icons + theming) + key-screen inventory + viewport/platform + media/offline/realtime + accessibility (interactive: ask · autopilot: self-answer + log forks)
- [ ] Stage 2: Research — design-system & platform conventions, WCAG levels, category UX norms (within the budget)
- [ ] Stage 3: Draft — assemble decisions; flag the ones that feed architecture scenarios; draft design-decisions.research.md
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — design-decisions.research.md (Sources + Forks log) + design-decisions.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/product-requirements.research.md` and
`.dev-skills/project-spec/user-flows.research.md` (and, if present,
`.dev-skills/project-spec/project-brief.research.md` for the user's original intent — settled input — and
developer preferences — soft priors). List the features, primary/secondary personas, the flows, and the key screens those
flows imply. If either of the two required files is missing, tell the user and offer to run
`/create-user-flows` (or `/define-product-requirements`) first. Do not invent features or flows
here. Read the mode.

### Stage 1: Elicitation
**Interview technique — `../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it. Work
the design decisions across five dimensions:
1. **Design system** — does the product need one? If yes, the *intent* (type scale, color approach,
   spacing system, motion stance) and the **component strategy**: adopt an existing library vs
   bespoke vs hybrid, and why. Decisions and direction, NOT concrete tokens or values. If the
   brief records a **design-taste preference**, treat it as a **soft prior** here — bias toward it,
   but let the product's needs and the category conventions decide; log it as a fork with
   `Source = preference`.
   **When the strategy is "adopt", name the kit here** — this is the decision, not a build-time
   detail, because it fixes a dependency and constrains what the screens can be. Pick it on three
   criteria, in this order:
   - **Coverage** — walk the key-screen inventory (dimension 2) for the components the product
     actually needs (data table with sorting, rich-text editor, date picker, command palette, toast,
     skeleton…). A kit missing a component the product leans on means hand-building it, which
     defeats the consistency the kit was for. Say so out loud rather than discovering it in build.
   - **Platform fit** — the kit must target the platforms from dimension 3.
   - **Ubiquity** — the more widely used the kit, the more reliably an AI agent writes against it.
     Prefer boring and common over novel.
   Also settle two decisions that travel with it: the **icon set** — one for the whole product,
   mixing two shows immediately — and the **theming approach** (start from a ready-made theme of
   that kit vs author tokens from the brand intent). Present the kit and the icon set as **closed
   forks with a recommendation first** (`AskUserQuestion`), each option one line of consequence.
   A kit already present in the repo's dependencies is the default — replacing it is a
   rewrite of every screen and needs the user's explicit decision (log it as drift).
   This dimension is the input `setup-dev-environment` builds `DESIGN.md` from; it does not re-open it.
2. **Key-screen inventory** — the set of screens/surfaces the product has, drawn from the flows.
   Per screen: name, the flow(s) it serves, its job. Structure and purpose, not layout.
3. **Viewport & platform behavior** — target platforms (web/responsive, iOS, Android, desktop) and
   the per-viewport intent for the key screens (what's primary on small vs large); platform
   conventions to honor.
4. **Media & connectivity** — media-heaviness (images/video/audio, at what scale), offline /
   low-connectivity expectations, real-time / live-update needs. Each is flagged as an
   architecture input.
5. **Accessibility** — the WCAG target (A / AA / AAA) and any specific requirements.

- **interactive:** ask, one dimension at a time; do not slide into pixel design.
- **autopilot:** choose each from the product spec + flows + (stage 2) conventions + best judgment;
  record each material choice in the Forks / Decisions log with rationale, confidence, source. Mark
  uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted)
Verify the design conventions you adopt. Topics: **the candidate UI kit's current component
coverage** against the list from dimension 1 (its own component index is the primary source — do not
answer from memory, kits gain and drop components) and that the kit and icon set are still
maintained and target the platform; design-system conventions for this category; platform guidelines
(Apple HIG, Material) for the target platforms; the appropriate WCAG level and its concrete
requirements; known UX norms and pitfalls for the key screens. **Rank them by what would change a
decision** — coverage of a component the product leans on outranks everything else here — and research top-down until the budget (≤4 searches / ≤4 opens per phase,
~2 opens held in reserve for stage 5) is spent; what you don't reach is logged unverified.
`/deep-research` only if the user explicitly asks. Method —
**`../_shared/spec-pipeline/research-method.md`**. Carry the patterns + source links into the draft
(a "platform convention" or "WCAG requires X" claim either cites its source or is labelled
unverified).

### Stage 3: Draft
Draft `.dev-skills/project-spec/design-decisions.research.md` from
`references/design-decisions-template.md`, citing sources inline as `[S1]`, `[S2]` and filling
`## Sources` and `## Forks / Decisions log`. Fill the **Architecture-feeding decisions** handoff
section explicitly — each weighty decision paired with the quality-attribute scenario it implies.
Create `.dev-skills/project-spec/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — it reads the draft and the prior docs, not the web)
to find inconsistencies + gaps. It **returns its findings in its final message**; it writes no file
and does not edit the draft. Method + return format:
**`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. For this phase the reviewer
especially probes: a design decision that silently forces a costly architecture but isn't flagged as
an architecture input; a key screen with no flow (or a flow with no screen); a missing accessibility
target; media/offline/realtime implications left unsurfaced; a design system absent where the
category demands one (or bespoke where adopting a library would do); **an adopted UI kit that
doesn't cover a component the key screens lean on, a kit that doesn't target one of the stated
platforms, more than one icon set, or a "we'll adopt a library" with no kit actually named**; and
pixel/mockup/copy detail that leaked in (out of scope — that's implementation).

### Stage 5: Fix
Apply the findings to `design-decisions.research.md` **in place** (targeted edits, not a rewrite)
and log each applied finding in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions. If a finding
  implies a missing feature or flow, recommend updating the product layer (re-run
  `/define-product-requirements` or `/create-user-flows`) rather than inventing it here.
- **🔴 autopilot:** resolve them yourself (set the missing target, flag the architecture input) and
  log each resolution. A 🔴 you cannot resolve becomes an open question.
- **🟡 / ⚪:** apply by your own judgement.
Spend a **reserved fetch** only on a `Fix: verify` finding that would actually change a decision;
label the rest unverified. What no one could verify goes to `## Open questions`. A clean review
(0 🔴) proceeds without stopping.

### Stage 6: Dual output
Finalize `design-decisions.research.md` (complete `## Sources` and `## Forks / Decisions log`).
Then write `.dev-skills/project-spec/design-decisions.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** — the design direction in plain language + the
forks the human must answer + open risks. Format rules:
**`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Design decisions done → design-decisions.research.md (detail), design-decisions.summary.md
  > (for you). Review it. When you approve, run `/design-architecture` for the technical layer. I
  > will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or,
  standalone, report the two files + the must-answer forks).

Do NOT start architecture work, produce mockups, or write any UI code in this session unless the
user explicitly approves and asks.

## When the repo already has code

Read the realized design direction from the repo (UI kit and icon set in the dependencies, theme
config or token files, target platforms, viewport behavior) and treat it as the default — **replacing
an installed UI kit is a rewrite of every screen and needs the user's explicit decision**. Interview
to confirm or change it; a swap is both a divergence and an input to `design-architecture`'s
scenarios. Log differences in `## Divergences (code vs intended)`. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document — because an upstream phase was edited, or the user changed their
mind — and you **amend** rather than regenerate: reconcile
`design-decisions.research.md` to the change instead of producing it from scratch. Per
**`../_shared/build-pipeline/propagation-method.md`**:

1. Read the changed upstream document and your current `design-decisions.research.md`.
2. **Assess impact** — if this phase is not affected, self-skip: report "no change needed", touch nothing.
3. If affected, **amend surgically** — update only the parts the change touches in
   `design-decisions.research.md` (and `design-decisions.summary.md` if the essence changed),
   **preserving the `## Forks / Decisions log`**. Never regenerate; do scoped research only for the changed part.
4. **Log it** — add a `## Forks / Decisions log` entry: what upstream changed, how this doc changed.
5. **Ask only on a critical question** (a decision-changing or low-confidence fork); otherwise proceed and log.
6. **Hand off, don't chase.** Say in one line what's next in the chain (`/design-architecture`) and offer to run it. If
   `.dev-skills/build-plan/tasks/` exists, add: the plan may now be stale — `/plan-development` will
   reconcile it with task deltas. The user decides how far to walk; you never edit the backlog here.

## Rules

1. Never produce the design-decisions doc after the first message — load the upstream docs and work
   the stages first.
2. Decisions only — never layouts, colors, components, copy, or mockups (those are implementation).
3. Only decisions that shape architecture or scope belong here; defer cosmetic choices.
4. Every key screen traces to a flow; reuse the domain glossary vocabulary; never add features.
5. Flag every technically-weighty decision (media, offline, realtime, platforms) as an input to a
   `design-architecture` quality-attribute scenario.
6. Set an explicit accessibility (WCAG) target.
7. Never make technical/architecture decisions — surface gaps back to the product layer instead.
8. Every *verified* adopted standard is cited and every unverified one is labelled as such; every
   fork is logged; the review always runs (both modes) and its findings are always applied.
