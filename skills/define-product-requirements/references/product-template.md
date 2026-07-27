# Product Definition — <Product name>

> Status: Draft | Date: <YYYY-MM-DD>
> Source: .dev-skills/project-spec/idea-validation.research.md (<verdict>)

## Summary

<2–3 sentences: what the product is, who it serves, and the core value — distilled from the
validated idea.>

## Audience

### Primary persona
<Role, context, and the job they hire this product to do.>

### Segments
- **Primary:** <who>
- **Secondary:** <who>
- **Not the audience:** <who this is explicitly not for>

### Jobs-to-be-done
- <Core job, in the user's words.>

## Features (committed scope)

> The full set of features being built. No tiers, no prioritization — everything here ships.
> Each feature carries ≥1 behavioral acceptance criterion (Given/When/Then or EARS) — an
> observable outcome, the feature's definition of done, never implementation detail.

### <Capability area>
| Feature | What it does | Serves (validated need) | Acceptance criteria (behavioral, testable) |
|---------|--------------|-------------------------|--------------------------------------------|
| <name>  | <one line>   | <problem / audience need from validation> | <Given/When/Then or EARS — one per line> |

### <Capability area>
| Feature | What it does | Serves (validated need) | Acceptance criteria (behavioral, testable) |
|---------|--------------|-------------------------|--------------------------------------------|
| <name>  | <one line>   | <need> | <Given/When/Then or EARS — one per line> |

## Domain model & glossary

> The conceptual model — product concepts, NOT a database schema (that's design-architecture).
> One canonical vocabulary; every later phase (flows, architecture) reuses these names.

### Entities
| Entity | What it represents | Owns (key data) | Key relationships |
|--------|--------------------|-----------------|-------------------|
| <name> | <one line>         | <fields it owns> | <e.g. Owner 1—* Document> |

### Glossary
| Term | Definition (one line, canonical for this product) |
|------|---------------------------------------------------|
| <term> | <meaning> |

## Success metrics

| Goal | Signal | Target | How measured |
|------|--------|--------|--------------|
| <goal> | <what we observe> | <number> | <method> |

## Product constraints

- **Budget / timeline / team:** <...>
- **Platforms / devices:** <...>
- **Compliance / legal:** <...>
- **Hard non-negotiables:** <...>
- **Key assumptions:** <...>
- **Raw technical expectations** (carried to architecture phase, not decided here): <e.g. "must
  feel instant", "handle N users", "data stays in EU">

## Non-goals (scope boundaries)

- <What this product deliberately does NOT try to be. Not a deferred-feature list.>

## Sources

<Every source consulted during research (comparable products, table-stakes features, category
norms), referenced inline above as [S1], [S2], … See _shared/spec-pipeline/output-format.md.>

- [S1] <title> — <url>
- [S2] <claim> — no reliable source found

## Forks / Decisions log

<Every decision point this phase hit and who resolved it. Required in both modes.>

| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] or — | yes \| no |

## Open questions

- <Unresolved question carried into the create-user-flows / design-architecture steps.>
