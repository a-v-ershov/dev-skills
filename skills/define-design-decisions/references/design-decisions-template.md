# Design Decisions — <Product name>

> Status: Draft | Date: <YYYY-MM-DD>
> Source: .dev-skills/project-spec/product-requirements.research.md, .dev-skills/project-spec/user-flows.research.md
> Scope: design direction that shapes scope & architecture — NOT pixel layouts, colors, or mockups.

## Summary

<2–3 sentences: the design direction in plain language — system or not, platforms, the few
decisions that matter most for what gets built.>

## Design system

- **Needed?** <yes / no — and why, for this category.>
- **Direction (if yes):** <type scale, color approach, spacing system, motion stance — intent, not
  concrete tokens.>
- **Component strategy:** <adopt an existing library (which) / bespoke / hybrid — and why.>

## Key screens (inventory)

> Drawn from the flows. Structure and purpose, not layout. Every screen traces to a flow.

| Screen / surface | Serves (flow) | Its job | Notes |
|------------------|---------------|---------|-------|
| <name> | <flow from user-flows.research.md> | <one line> | <structure, not layout> |

## Viewport & platform behavior

- **Target platforms:** <web responsive / iOS / Android / desktop …>
- **Per-viewport intent (key screens):** <how the experience adapts; what's primary on small vs
  large.>
- **Platform conventions honored:** <HIG / Material / web norms — cite [S#].>

## Media & connectivity (architecture inputs)

- **Media-heaviness:** <images / video / audio + scale> → feeds a quality-attribute scenario.
- **Offline / connectivity:** <expectations> → feeds a quality-attribute scenario.
- **Realtime / live updates:** <needs> → feeds a quality-attribute scenario.

## Accessibility

- **WCAG target:** <A / AA / AAA + any specific requirements> (cite [S#]).

## Architecture-feeding decisions (handoff)

> The decisions `design-architecture` must turn into measurable quality-attribute scenarios.

| Decision | Implies scenario (for design-architecture) |
|----------|--------------------------------------------|
| <e.g. video-heavy, 4K uploads> | <object storage + CDN + transcoding; cost/perf scenario> |
| <e.g. usable offline> | <local-first / sync + conflict handling; reliability scenario> |

## Sources

<Every source consulted (design-system conventions, platform guidelines, WCAG level, category UX
norms), referenced inline above as [S1], [S2], … See _shared/spec-pipeline/output-format.md.>

- [S1] <title> — <url>
- [S2] <claim> — no reliable source found

## Forks / Decisions log

<Every decision point this phase hit and who resolved it. Required in both modes.>

| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] or — | yes \| no |

## Open questions

- <Unresolved design question carried into the design-architecture step.>
