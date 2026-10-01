# Output format (shared — spec pipeline)

Per phase: **two files, both kept** — a detailed AI-facing `<artifact>.research.md` and a compressed,
decisions-first human report `<artifact>.summary.md`. The reviewer writes no file; the phase applies
its findings to the research doc in place (see `review-method.md`).

## 1. Detailed research doc — `<artifact>.research.md`

The phase's detailed artifact (e.g. `idea-validation.research.md`). The persona's template defines
the body; the research/review wrapper adds two sections:

### `## Sources`

Every source consulted, numbered, title + link, cited inline as `[S1]`, `[S2]`, … next to the fact.
"No reliable data" findings are listed too, marked as such.

```
## Sources
- [S1] <title> — <url>
- [S2] <title> — <url>
- [S3] <claim> — no reliable source found
```

### `## Forks / Decisions log`

Every decision point the phase hit, **whoever resolved it** — non-negotiable in both modes (autopilot:
keeps the AI's choices auditable; interactive: records the human's choice). The fix stage also logs
the review findings it applied here — the review's only lasting trace.

```
## Forks / Decisions log
| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] or — | yes \| no |
```

- **By** = `AI` (autopilot, or AI-proposed) or `human` (interactive answer).
- **Needs human confirm?** = `yes` for anything the AI decided at medium/low confidence, or any fork
  with material downside if wrong. The human summary surfaces these.

### `## Divergences (code vs intended)` — only when the repo already has code

When existing code differs from the intent, one extra section — a plain list, no special vocabulary,
no extra columns elsewhere:

```
## Divergences (code vs intended)
| # | What the code does now | What's intended | Kind |
|---|------------------------|-----------------|------|
| 1 | <observed behavior / structure> | <what the user wants> | change \| remove \| not built yet |
```

`plan-development` reads exactly this to decide what work exists. In an empty repo the section is
absent — no placeholder.


## 2. Human report — `<artifact>.summary.md`

The **only** artifact for the human; all detail stays in `.research.md`. **Maximally compressed and
decisions-first** — no tables, citations, jargon or process narration; well under half a page.

Three sections, in this fixed order (see `summary-template.md`):

```
# <Phase> — report

> Detail (for the AI): <artifact>.research.md · Mode: interactive | autopilot · <YYYY-MM-DD>

## Decide — what I need from you
- **<question>** — AI chose **<X>** (confidence: low | med). <one line: why; what breaks if wrong>
<only "Needs human confirm? = yes" forks; if none: "Nothing — all decided.">

## Risks
- <each unresolved risk the review couldn't close, one line. If none: "None outstanding.">

## Key facts
- <≤5 plain-language bullets: the essence. The rigor stays in the research doc.>
```

**Decide** first — the only part needing the human's action. **Key facts** names at most a few
concepts; the domain model, glossary, acceptance criteria and schemas stay in the research doc.
Anything from the review that matters to the human lands in Risks or in the research doc's Forks /
Decisions log + Open questions.

## 3. There is no third file

The reviewer returns its findings in its final message (format: `review-format.md`); the fix stage
applies them to `<artifact>.research.md` and logs them in the Forks / Decisions log. Nothing
transient is written, so nothing needs deleting or gitignoring. Everything under
`.dev-skills/project-spec/` is committed project documentation.

## 4. Final combined summary — `.dev-skills/project-spec/summary.md` (orchestrator only)

Built by `create-project-spec` at the end of a run when `final_summary: true`. **Decisions-first,
maximally compressed** — one short document the human reads after the whole pipeline:

```
# <Product> — spec report

> <date> · Mode: interactive | autopilot
> Detail (for the AI): project-brief · idea-validation · product-requirements · user-flows ·
> design-decisions · architecture · code-style · dev-architecture (.research.md, under
> .dev-skills/project-spec/)

## Decide — what I need from you
<Consolidated across all phases: every "Needs human confirm? = yes" fork, one line each, grouped by
phase. This is the action list. If none: "Nothing outstanding.">

## Risks
<Consolidated unresolved risks across phases, one line each.>

## What it is
<2–4 plain-language bullets: what the product is and where the spec landed. The per-phase detail
lives in each .research.md.>
```

It re-derives nothing — it rolls up the per-phase **Decide** + **Risks** and adds a 2–4 bullet gist.

## Every phase closes with «What you should do»

A phase's **last block**: the numbered, imperative list of what the human has to do — one line each,
in their language, free of this skill set's vocabulary; "nothing" is a valid one-line answer. Full
rule, including timings: **`../build-pipeline/report-format.md`**.
