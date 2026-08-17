# Template — code-style.research.md

Copy this structure. Write it in the user's language (structural anchors — the headings below — stay
verbatim; see `../../_shared/glossary.md`). Cite sources inline as `[S1]`, `[S2]`. Per dimension:
name the baseline canon (cited), then either the fork (options table + decision) or one inheritance
line. Keep option tables to 2–3 rows — a longer list means the shortlist wasn't done.

```markdown
# Code style — research

> Inputs: architecture.research.md (<stack in one line>), product-requirements.research.md (domain
> model), project-brief.research.md (<present? which preference sections>). Mode: <interactive |
> autopilot>. Date: <date>.

## Stack context

<3–6 lines: language(s), framework, test framework if already settled, API surface yes/no — only
what the conventions below hang on. No re-litigation of the architecture.>

## Dimensions

### Code organization
- **Baseline (canon):** <what the stack/framework prescribes, cited [S#] — or "no prescription,
  live fork">
- **Fork:** <name it, or "none — inherited">
  | Option | What it buys here | What it costs here |
  |--------|-------------------|--------------------|
  | <top option> | <...> | <...> |
  | <second> | <...> | <...> |
- **Decision:** <chosen option> — <2–3 lines of rationale tied to this project's size/features>.
- **Boundary rules:** <what imports what; where shared code lives; promotion bar>
- **Tests live:** <colocated | mirror | tests/> — <one-line reason>

### Naming
<Canon line (cited) + the domain-vocabulary rule + any project-specific decisions. Table only if a
real fork existed.>

### Comments & documentation
<Comment policy (why-not-what default + decided density) · docstring scope decision (with the fork
table if it was live) · TODO policy · when code-adjacent docs are warranted.>

### Error handling
<Propagation style (fork table if live) · taxonomy + boundary conversion · message/logging
conventions · where recovery logic belongs.>

### Testing style
<Naming & structure · mock policy (this fork is almost always live — table) · test data · assertion
style. One line acknowledging the inherited gate economy (quality-gate.md).>

### Stack-specific strictness
<Typing level, null handling, lint-severity policy — each as decision + where it is enforced.>

### API conventions *(omit if no API)*
<Field naming/casing, error-response shape, pagination/versioning, boundary validation.>

### Dependency policy
<The bar a new dependency clears; who approves.>

## Enforcement mapping

| Convention | Tool + rule | Wired at |
|------------|-------------|----------|
| <e.g. formatting, wholesale> | <formatter, config name> | setup-dev-environment → make check-fast |
| <e.g. import boundaries> | <lint rule / plugin> | setup-dev-environment → make check-fast |
| <e.g. typing level> | <type-checker flag> | setup-dev-environment → make check-fast |

<Every enforceable convention appears here; what remains prose-only in the guide is exactly what no
tool can check.>

## Divergences (code vs intended) *(existing-code runs only)*

<De-facto convention found → intended convention → user's decision (keep / migrate via rework task).>

## Open questions

<What nobody could settle or verify.>

## Sources

<[S1] … — one line each: what it is, what it supported, date accessed. Unverified claims are
labelled where they appear.>

## Forks / Decisions log

<One row per fork: dimension · options considered · chosen · rationale · Source = canon | analysis |
preference · Confidence · Needs human confirm? — per ../../_shared/spec-pipeline/output-format.md.>
```
