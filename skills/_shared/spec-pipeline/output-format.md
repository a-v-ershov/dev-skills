# Output format (shared — spec pipeline)

Every phase keeps **two** documents and produces them from the merged result: a detailed
AI-facing **research** doc and a maximally compressed, decisions-first **human report**
(`<artifact>.summary.md`). The reviewer's `.review.md` is a
**working artifact only** — the merge stage applies it and then **deletes it**, so it does not
survive into the final spec.

So per phase, after the merge: **two files remain** — `<artifact>.research.md` and
`<artifact>.summary.md`.

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
human chose. It is also where the merge stage records the review findings it applied (so the
deleted `.review.md` leaves a trace).

```
## Forks / Decisions log
| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] or — | yes \| no |
```

- **By** = `AI` (autopilot, or AI-proposed) or `human` (interactive answer).
- **Needs human confirm?** = `yes` for anything the AI decided at medium/low confidence, or any
  fork with material downside if wrong. These are what the human summary surfaces.

**Existing-project mode adds three optional columns** — `AS-IS`, `TARGET`, `Drift?` — appended after
`Source`, filled only for forks that reconcile built code against intent (see
`existing-project-mode.md`). They are **blank or absent in greenfield** (the default). When present:

```
| # | Fork | Options | Decision | By | Rationale | Confidence | Source | AS-IS | TARGET | Drift? | Needs human confirm? |
|---|------|---------|----------|----|-----------|-----------|--------|-------|--------|--------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI\|human | <why> | high\|med\|low | [S2] or — | <what the code does> | <what's intended> | no\|change\|remove\|new | yes\|no |
```

- **AS-IS** = what `map-codebase` found in the code · **TARGET** = the intended state · **Drift?** =
  `no` (keep — AS-IS already matches) · `change` (built but divergent) · `remove` (built, not wanted)
  · `new` (intended, not yet built). `plan-development` delta mode reads this column to decide each
  task's fate.

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
stay in the research doc — name at most a few concepts here). Because the `.review.md` is deleted
after merge, anything from the review that matters to the human lands here (Risks) or in the research
doc's Forks / Decisions log + Open questions.

## 3. The review doc is transient — `<artifact>.review.md`

The reviewer writes it (format in `review-template.md`); the merge stage applies its corrections
into `<artifact>.research.md` (and logs them in the Forks / Decisions log), then **deletes the
file**. It is never a deliverable and is not referenced by later phases. Delete it in both modes,
after the merge — its content is fully absorbed into the research doc.

As a belt-and-suspenders guard against an aborted run leaving a stray review behind, the pipeline
also keeps a local `.dev-skills/project-spec/.gitignore` containing `*.review.md`, created alongside the
directory (see `pipeline-config.md`). Everything else under `.dev-skills/project-spec/` is committed.

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
