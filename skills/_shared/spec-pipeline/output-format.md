# Output format (shared — spec pipeline)

Every phase keeps **two** documents: a detailed AI-facing **research** doc and a maximally
compressed, decisions-first **human report** (`<artifact>.summary.md`). The reviewer writes no file
at all — it returns its findings and the phase applies them to the research doc in place (see
`review-method.md`).

So per phase: **two files, both kept** — `<artifact>.research.md` and `<artifact>.summary.md`.

## 1. Detailed research doc — `<artifact>.research.md`

The phase's detailed artifact (e.g. `idea-validation.research.md`). The persona's template defines
the body; the research/review wrapper adds two sections to every one:

### `## Sources`

A numbered list of every source consulted, each with a title and a link. Reference them inline in
the body as `[S1]`, `[S2]`, … next to the fact they support. "No reliable data" findings are
listed here too, marked as such.

```
## Sources
- [S1] <title> — <url>
- [S2] <title> — <url>
- [S3] <claim> — no reliable source found
```

### `## Forks / Decisions log`

Every decision point the phase hit — **whoever resolved it**. This is non-negotiable in both
modes: in autopilot it is how the AI's choices stay auditable; in interactive it records what the
human chose. It is also where the fix stage records the review findings it applied — the review's
only lasting trace, since the reviewer writes no file.

```
## Forks / Decisions log
| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] or — | yes \| no |
```

- **By** = `AI` (autopilot, or AI-proposed) or `human` (interactive answer).
- **Needs human confirm?** = `yes` for anything the AI decided at medium/low confidence, or any
  fork with material downside if wrong. These are what the human summary surfaces.

### `## Divergences (code vs intended)` — only when the repo already has code

When the phase found existing code and the intent differs from it, the doc carries one extra section
— a plain list, no special vocabulary and no extra columns anywhere else:

```
## Divergences (code vs intended)
| # | What the code does now | What's intended | Kind |
|---|------------------------|-----------------|------|
| 1 | <observed behavior / structure> | <what the user wants> | change \| remove \| not built yet |
```

`plan-development` reads exactly this to decide what work exists. In an empty repo the section is
absent — don't write a placeholder.


## 2. Human report — `<artifact>.summary.md`

The **only** artifact written for the human — everything detailed lives in `.research.md`, which is
for the AI / next phases. It is **maximally compressed and decisions-first**: the human opens it and
immediately sees what they must answer, then the risks, then a few key facts — nothing else. No
tables, no citations, no jargon, no process narration. Target: well under half a page.

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

**Decide** comes first on purpose — it is the only part that needs the human's action, so if they
read nothing else they can still act. **Risks** are the unresolved things the review couldn't close.
**Key facts** is the compressed essence (the domain model, glossary, acceptance criteria, schemas
stay in the research doc — name at most a few concepts here). Because the review is never a file,
anything from it that matters to the human lands here (Risks) or in the research doc's Forks /
Decisions log + Open questions.

## 3. There is no third file

The reviewer returns its findings in its final message (format: `review-format.md`); the phase's fix
stage applies them to `<artifact>.research.md` and logs them in the Forks / Decisions log. Nothing
transient is written, so nothing has to be deleted or gitignored, and an aborted run can never leave
a stray artifact behind. Everything under `.dev-skills/project-spec/` is committed project
documentation.

## 4. Final combined summary — `.dev-skills/project-spec/summary.md` (orchestrator only)

Built by `create-project-spec` at the end of a run when `final_summary: true`. Same rule as the
per-phase report: **decisions-first, maximally compressed**. One short document the human reads
after the whole pipeline (especially an autopilot run):

```
# <Product> — spec report

> <date> · Mode: interactive | autopilot
> Detail (for the AI): project-brief · idea-validation · product-requirements · user-flows ·
> design-decisions · architecture · dev-architecture (.research.md, under .dev-skills/project-spec/)

## Decide — what I need from you
<Consolidated across all phases: every "Needs human confirm? = yes" fork, one line each, grouped by
phase. This is the action list. If none: "Nothing outstanding.">

## Risks
<Consolidated unresolved risks across phases, one line each.>

## What it is
<2–4 plain-language bullets: what the product is and where the spec landed. The per-phase detail
lives in each .research.md.>
```

It re-derives nothing — it rolls up the per-phase reports' **Decide** + **Risks** and adds a 2–4
bullet gist. Decisions come first so the human's action list is the first thing they see.

## Every phase closes with «What you should do»

Whatever else a phase reports, its **last block** is the numbered, imperative list of what the human
has to do — one line each, in their language, with no vocabulary from this skill set in it. Nothing is
a legitimate answer, written as one line. The full rule, including how to report timings so they add
up: **`../build-pipeline/report-format.md`**.
