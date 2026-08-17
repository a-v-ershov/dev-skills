# Project Brief — <Product / Idea name>

> Status: Draft · Discovery brief (settled *intent*, not validated truth) · Date: <YYYY-MM-DD>
> This is the shared understanding captured before validation. `validate-idea` pressure-tests it;
> `define-product-requirements` formalizes features. Later phases read this as the user's intent.

## One-sentence product

<The product restated in a single concrete sentence the human confirmed.>

## Why now / the real goal

<What triggered this. The underlying outcome the human wants — what changes for them if it exists.
Not the feature; the goal behind it.>

## Who it's for

<The people in the human's head — kept loose here (validate-idea and the PRD sharpen it). Note any
specific person/role/company the human named.>

## The job / the pain

<What someone is trying to get done, and the painful status-quo workaround as the human sees it.
Capture a concrete recent example if one was given.>

## Shape & scope

- **In:** <what the human clearly wants in.>
- **Out (explicitly):** <what they ruled out — scope boundaries, not deferred features.>
- **Size they imagine:** <weekend tool · side project · serious product · platform.>
- **"Done" / success to them:** <what the human would call success, in their words.>

## Constraints & context the human carries

<Budget, timeline & deadlines, team + the human's own role/skill, target platforms/devices,
existing systems/accounts/licenses, hard requirements, compliance. Facts about the human's world
that bound later decisions.>

## Preferences & taste (soft priors)

The developer's standing leanings — what they like to reach for by default. Captured here as **soft
priors**, NOT decided: each biases the relevant later phase's fork but never overrides a requirement
(see `_shared/spec-pipeline/elicitation-method.md` → "Read the brief first"). Record any the human
stated, with refusals ("never X"); leave a sub-area out entirely if they have no leaning there.

- **Stack & libraries** *(→ design-architecture)*: <preferred languages, frameworks, libraries,
  datastores; refusals.>
- **Code style & idioms** *(→ define-code-style, distilled into code-style.md)*:
  <naming, formatting, patterns, testing style.>
- **Design taste** *(→ define-design-decisions)*: <design systems / component libraries / aesthetic
  they admire or hate, "like X but Y".>
- **Dev tooling** *(→ design-dev-architecture)*: <MCP servers, Claude Code plugins/skills, other
  agents, CI habits.>
- **Architecture leanings** *(→ design-architecture)*: <monolith vs services, sync vs async, "fewest
  moving parts", and similar standing biases.>

## Unknowns & assumptions

<What the human is unsure about; what they're quietly assuming. These feed the forks below and the
later phases' questions.>

## Sources

<Any source consulted during the light research, referenced inline above as [S1], [S2], … See
_shared/spec-pipeline/output-format.md. Most of this doc comes from the human, not the web.>

- [S1] <title> — <url>

## Forks / Decisions log

<Every decision point the interview hit and who resolved it. Required in both modes. In autopilot,
this is the list of assumptions the human must confirm.>

| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S1] or — | yes \| no |

## Open questions

- <Unresolved unknown carried into validate-idea / define-product-requirements.>
