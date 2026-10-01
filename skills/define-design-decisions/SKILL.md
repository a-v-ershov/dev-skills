---
name: define-design-decisions
description: "Decide the design direction that shapes scope and architecture: design system or none, which UI kit, icon set and theming, key screens, responsive behaviour, target platforms, offline and the WCAG target — no layouts, colours or mockups. Use after create-user-flows, before design-architecture. Writes design-decisions.research.md + summary."
---

# Define Design Decisions Skill

You are a product designer / design-system lead. From the committed features, personas and flows you
make the **design decisions that shape scope and architecture** — the choices that would force a costly
rebuild if wrong. Pixels wait for **implementation**, where the cheapest mockup is real code.

> **Downstream.** You are the **decide** rung of *decide → systematize → render*; you produce no tokens
> or design system. In the build phase **`setup-dev-environment`** writes the committed root
> `DESIGN.md` (tokens + rules) and **`generate-mockups`** renders disposable UI options against it. This
> phase's hard gate still hands off to `/design-architecture`.

Scope:
- **Decisions, not pixels** — no layouts, color values, components, copy or mockups.
- **Only what changes architecture or scope** — media-heaviness (→ storage/CDN), offline (→
  sync/conflicts), realtime UI (→ realtime infra), target platforms (→ the whole stack); cosmetic
  choices wait for implementation.
- **Experience layer, never the technical HOW** — no stack, APIs or schemas (`design-architecture`).
- **Inherit, don't redefine** — features/personas from `product-requirements.research.md`, flows and
  screen states from `user-flows.research.md`; every key screen traces to a flow; reuse the domain
  glossary's names; never add features or flows.

## Outputs in `.dev-skills/project-spec/` (two kept files)

- **`design-decisions.research.md`** — the detailed, source-cited design decisions.
- **`design-decisions.summary.md`** — the short human summary (essence + forks to answer).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths (design-system, platform and tool names stay as-is).
Commit messages are always English. **One branch — the current one** (normally `main`): never branch,
switch or open a worktree unless the user explicitly asked in this session —
**`../_shared/git-workflow.md`**. Pass both rules to every agent you spawn.

## Modes (read this first)

Read `mode` (`interactive` | `autopilot`) and `final_summary` from
`.dev-skills/project-spec/.spec-config.md`; if absent, ask once (default **interactive** +
**final_summary: true**) and write the file (**`../_shared/spec-pipeline/pipeline-config.md`**).

- **interactive** — ask at each fork; stop at the fix stage's 🔴 and at the hard gate.
- **autopilot** — decide from flows + requirements + judgment, logging each material choice in the
  Forks / Decisions log with rationale and confidence; resolve 🔴 yourself; never prompt or stop. Still
  push back on cost without payoff and on missing accessibility.

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
`.dev-skills/project-spec/user-flows.research.md` (plus, if present,
`.dev-skills/project-spec/project-brief.research.md` — settled intent and preferences as soft priors).
List features, personas, flows and the key screens they imply. A required file missing → offer
`/create-user-flows` (or `/define-product-requirements`) first. Read the mode.

### Stage 1: Elicitation
Work the dimensions in **`references/elicitation-topics.md`**: design direction and system (including
**which UI kit**, chosen on component coverage against the key screens), icon set and theming, the
key-screen inventory, responsive/viewport behaviour, target platforms and their conventions,
media-heaviness, offline expectations, accessibility target. Technique:
**`../_shared/spec-pipeline/elicitation-method.md`**.

What is settled here becomes **frozen** once `setup-dev-environment` writes `DESIGN.md`: no later skill
re-opens a colour, ratio or scale on its own (**`../_shared/build-pipeline/design-freeze.md`**). Say so
when recording decisions, and record every **deliberately accepted trade-off** (a contrast ratio chosen
below its target, say) alongside, so later audits don't rediscover it as a bug.

Interactive: one dimension at a time; never jump to pixels.

### Stage 2: Research (budgeted)
Topics: **the candidate UI kit's current component coverage** against the dimension-1 list (its own
component index is the source — never memory; kits gain and drop components) and whether kit and icon
set are maintained and target the platform; category design-system conventions; platform guidelines
(Apple HIG, Material); the appropriate WCAG level and its concrete requirements; UX norms and pitfalls
for the key screens. Rank by what would change a decision — coverage of a component the product leans
on outranks everything — and work top-down within the budget (≤4 searches / ≤4 opens per phase, ~2
opens reserved for Stage 5); the rest is logged unverified. `/deep-research` only on explicit request.
Method: **`../_shared/spec-pipeline/research-method.md`**. Adopt a cited standard rather than invent
one; a "platform convention" or "WCAG requires X" claim cites its source or is labelled unverified.

### Stage 3: Draft
Draft `.dev-skills/project-spec/design-decisions.research.md` from
**`references/design-decisions-template.md`**, citing sources inline as `[S1]`, `[S2]` and filling
`## Sources` and `## Forks / Decisions log`. Fill the **Architecture-feeding decisions** handoff
section explicitly — each weighty decision paired with the quality-attribute scenario it implies.
Create the directory if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline). It returns findings in its final message and writes
nothing (**`../_shared/spec-pipeline/review-method.md`**, `review-format.md`). What it probes:
**`references/elicitation-topics.md`** → "What the reviewer probes".

### Stage 5: Fix
Apply the findings **in place** (targeted edits) and log each in the Forks / Decisions log.
**🔴 interactive:** STOP — show the count + top items, get the user's decisions; a finding implying a
missing feature or flow → recommend re-running `/define-product-requirements` or `/create-user-flows`,
never invent it here. **🔴 autopilot:** resolve (set the missing target, flag the architecture input)
and log; an unresolvable 🔴 becomes an open question. **🟡 / ⚪:** your judgement. Spend a reserved
fetch only on a `Fix: verify` finding that would change a decision; the unverifiable goes to
`## Open questions`. 0 🔴 → proceed.

### Stage 6: Dual output
Finalize the research doc (`## Sources`, `## Forks / Decisions log`). Write
`.dev-skills/project-spec/design-decisions.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`**: the direction in plain language + must-answer forks
+ open risks. Format: **`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP:
  > "Design decisions done → design-decisions.research.md (detail), design-decisions.summary.md
  > (for you). Review it. When you approve, run `/design-architecture` for the technical layer. I
  > will not proceed automatically."
- **autopilot:** log the auto-pass and hand back to the orchestrator (standalone: report the two
  files + the must-answer forks).

Never start architecture work, produce mockups or write UI code in this session without explicit
approval.

## When the repo already has code

Read the realized direction from the repo (UI kit and icon set in the dependencies, theme/token files,
platforms, viewport behaviour) and treat it as the default — **replacing an installed UI kit rewrites
every screen and needs the user's explicit decision**. Confirm or change it in the interview; a swap is
both a divergence and an input to `design-architecture`'s scenarios. Log differences in
`## Divergences (code vs intended)`. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

On an existing document, **amend** rather than regenerate, per
**`../_shared/build-pipeline/propagation-method.md`**: assess impact and self-skip if unaffected;
otherwise edit surgically (plus `design-decisions.summary.md` if the essence changed), preserve the
`## Forks / Decisions log` and add an entry, ask only on a decision-changing fork, hand off in one line
(`/design-architecture`; if `.dev-skills/build-plan/tasks/` exists, say the plan may be stale and
`/plan-development` reconciles it — never edit the backlog here).

## Rules

1. Load the upstream docs and work the stages — never produce the doc after the first message.
2. Flag every technically-weighty decision (media, offline, realtime, platforms) as an input to a
   `design-architecture` quality-attribute scenario — an unflagged one gets lost.
3. Set an explicit accessibility (WCAG) target.
4. Take a position: the category needs a design system and there is none → say so; "custom
   everything" adds cost without payoff → name the cheaper path.
5. Verified standards are cited, unverified ones labelled; every fork is logged; the review always runs
   (both modes) and its findings are applied.
6. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
