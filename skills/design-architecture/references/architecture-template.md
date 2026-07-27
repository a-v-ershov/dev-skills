# Architecture — <Product name>

> Status: Draft | Date: <YYYY-MM-DD>
> Source: .dev-skills/project-spec/user-flows.research.md, .dev-skills/project-spec/product-requirements.research.md
> Scope: quality-attribute scenarios + component design + the concrete technology realizing each.

## System overview

<One paragraph: what the system must do, distilled from the product spec.>

**Constraints that bound the choice:** <budget / timeline / platforms / compliance / raw
technical expectations from product-requirements.md, plus team skills & size and existing
investments (infra, accounts, licenses).>

## Quality-attribute scenarios

> Elicited BEFORE any tool. Each is concrete and testable: source → stimulus → environment →
> response → **measure**. These are the rubric every component and technology choice is judged against.

| # | Attribute | Scenario (source → stimulus → response) | Measure / target | Priority |
|---|-----------|------------------------------------------|------------------|----------|
| 1 | Performance | <a user opens X at peak load> | <p95 < 200 ms> | High |
| 2 | Scale | <...> | <N concurrent users / M req/s> | |
| 3 | Cost | <steady state at N users> | <≤ $X / month> | |
| 4 | Security / privacy | <...> | <...> | |
| 5 | Reliability / availability | <single-zone outage> | <recover < Y min, no data loss> | |
| 6 | Maintainability / operability | <...> | <...> | |

## Components (chosen design)

> Each component keeps its logical-role label (so a later swap stays cheap) alongside the concrete
> technology chosen to realize it. Note where one technology covers several roles.

| Component (logical role) | Responsibility | Owns (data) | Chosen technology | Satisfies scenario(s) | ADR |
|--------------------------|----------------|-------------|-------------------|-----------------------|-----|
| <accounts & auth> | <...> | <...> | <chosen tool> | <#4, #5> | adr/0001-<slug>.md |
| <core data> | <...> | <...> | <chosen tool> | <#1, #3> | adr/0002-<slug>.md |

## Options considered (per significant component)

> For each significant component, the 2–3 integrated options weighed — structure + tools together.

### <Component / capability>
- **Scenarios / constraints it must honor:** <from above.>

| Option (structure + tools) | Satisfies | Strains / cost / lock-in | Moving parts |
|----------------------------|-----------|--------------------------|--------------|
| <Managed BaaS — auth+db+realtime as one> | <...> | <vendor lock-in, RLS limits> | fewest |
| <Self-hosted — API + db + auth lib + ws> | <...> | <more code & ops> | more |
| <third candidate, if any> | <...> | <...> | <...> |

- **Recommendation:** <option> — because it best satisfies <scenario #s>. Collapses/splits: <which roles>.

### <Component / capability>
- **Scenarios / constraints it must honor:** <...>
- **Options:** <table as above>
- **Recommendation:** <...>

## Interactions & data flow

- **Component map (textual):** <how the chosen pieces connect.>
- **Key flow** (traced from user-flows.md): the path of the primary flow across the components.
- **Sync vs async boundaries:** <what is request/response, what is queued/event-driven, and why.>
- **Trust / security boundaries:** <what crosses each boundary; what is authenticated/authorized.>

## Threat model (if security-sensitive)

> Run only when the product handles money, PII/credentials, or shared/multi-tenant access. For a
> product with no such assets, write "Not applicable — no sensitive assets" and move on.
> STRIDE-lite over the component map + trust boundaries above; fold every mitigation back into the
> design and the relevant ADR.

- **Assets:** <what's worth protecting — user data, money, documents, secrets.>
- **Attack surfaces:** <auth, share links, file upload, payment, public endpoints, …>

| # | Asset / surface | Threat (STRIDE) | Mitigation | ADR / scenario |
|---|-----------------|-----------------|------------|----------------|
| 1 | <e.g. share link> | Info disclosure — guessable token | unguessable token + expiry + access log | adr/000N / #4 |

> STRIDE = Spoofing · Tampering · Repudiation · Information disclosure · Denial of service ·
> Elevation of privilege.

## Cost & risk sanity check

- **Rough steady-state cost at <N users / stated scale>:** <≈ $X / month — vs budget scenario #3.>
- **Top operational risks of this stack:** <failure modes and who can debug them.>

## Decisions (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| adr/0001-<slug>.md | <one-line summary> | Proposed / Accepted |

## Sources

<Every source consulted while verifying technology choices (current capabilities, pricing, limits,
maturity, deprecations), referenced inline above as [S1], [S2], … See
_shared/spec-pipeline/output-format.md.>

- [S1] <title> — <url>
- [S2] <claim> — no reliable source found

## Forks / Decisions log

<Every decision point this phase hit and who resolved it. Required in both modes. A significant,
hard-to-reverse fork also gets a full ADR — reference it here.>

| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source / ADR | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] / adr/0001 | yes \| no |

## Open questions / risks

- <Unresolved architectural or technology question carried into implementation planning.>
