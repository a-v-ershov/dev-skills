# Template — code-style.md (the distilled guide)

The file `implement-feature`, `verify-feature`, `refactor` and `write-tests` load on every task — so
it is **lean (target ≤120 lines), imperative, and rationale-free**. Every line is a decided rule from
`code-style.research.md`; nothing appears here that the research doc didn't decide, and nothing the
formatter/linter enforces is restated as prose. Written in the user's language; headings verbatim.
Re-distil this file whenever the research doc's decisions change — the two never drift.

```markdown
# Code style — <project name>

> Decided by define-code-style; rationale and options live in code-style.research.md. The enforced
> subset lives in the lint/formatter config (see Enforcement) — this file never restates it.

## Code organization
- <the chosen module architecture, in one line — e.g. "package by feature: features/<name>/ holds
  route + logic + tests for that feature">
- <boundary rule(s): what may import what>
- <where shared code lives + the promotion bar>
- <where tests live>

## Naming
- <casing per artifact kind — only the lines the linter does NOT already enforce>
- Domain terms come verbatim from the domain model (product-requirements) — no synonyms.
- <booleans-as-predicates / verbs-for-functions, if decided>

## Comments & documentation
- Comments state constraints and non-obvious intent — never what the next line does.
- <docstring scope decision — e.g. "docstrings on public API only">
- <TODO policy>

## Error handling
- <propagation style — e.g. "domain errors as Result types; exceptions only for bugs">
- <boundary rule — what converts where, what crosses the API>
- <logging rule — e.g. "log once, at the boundary, structured">

## Testing
- <test-name pattern + structure — e.g. "behaviour sentences, arrange-act-assert">
- <mock policy — e.g. "mock at system boundaries only; own code runs real">
- <test-data convention>
- <assertion/snapshot policy>
- Test levels & selection: per the quality gate — cheapest level that proves the criterion.

## Stack specifics
- <typing/strictness rules that are conventions of use, not compiler flags>
- <null/immutability leanings>
- <API conventions, if an API exists — field casing, error shape, pagination>
- <dependency bar — one line>

## Enforcement
> Wired into `make check-fast` by setup-dev-environment; the tools below are the source of truth for
> everything they check.
- <formatter + config> — formatting, wholesale
- <linter + named rules/plugins> — <which conventions above>
- <type-checker + level> — <which>
```
