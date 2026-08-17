# define-code-style — dimension catalogue, research topics, reviewer probes

The elicitation catalogue for the style phase. Work the core dimensions in order; include a
conditional dimension only when its trigger holds. For every dimension the first question is the same:
**does the chosen stack present a real fork here?** If yes — top 2–3 idiomatic options, what each buys
and costs *on this project*, a recommendation. If no — inherit the canon in one cited line and move on.
Never open a dimension with "what style do you like?"; open it with options and a recommendation.

## Core dimensions

### 1. Code organization (the architecture of the source tree)

The highest-stakes dimension — it fixes where every later task puts its files, and
`design-dev-architecture` builds the scoped-test selection convention on top of it.

- **Module/folder architecture** — the classic fork. Typical options per stack: package-by-feature
  (vertical slices) · package-by-layer (controllers/services/models) · hexagonal / ports-and-adapters ·
  the framework's own prescribed layout (e.g. an app-router or MVC skeleton — when the framework
  prescribes one, that *is* the canon and the fork may collapse). Weigh against project size and the
  committed feature count (≤15): heavy layering on a small product is the anti-pattern to name.
- **Boundary rules** — what may import what (feature→shared yes, feature→feature via what), where
  shared code lives, and the bar for promoting something into it (rule of three, not first reuse).
- **File & module granularity** — leanings only (one exported thing per file? size at which to split?);
  never hard line-counts a linter can't check and a human will ignore.
- **Where tests live** — colocated vs mirror tree vs `tests/` — decided *here* as a fork only if the
  stack leaves it open; the scoped-selection mechanics stay with `design-dev-architecture`.

### 2. Naming

Casing and word-form per artifact kind (files, types, functions, constants, DB entities, routes) —
almost always inherited from the stack's canon, cited. The project-specific part: **names reuse the
domain model's vocabulary** from `product-requirements.research.md` verbatim — no synonyms, no
parallel glossary. Booleans read as predicates; functions as verbs; abbreviations only from the
domain glossary.

### 3. Comments & documentation

- **Comment policy** — default: a comment states a constraint or non-obvious intent the code cannot
  show ("why", not "what"); restating the next line is noise to be deleted. Density is a preference
  fork worth surfacing (sparse-by-default vs generous) — but "what-comments" are never an option.
- **Docstring / API-doc scope** — a real fork on most stacks: public API only · every exported
  symbol · none (types + names carry it). Weigh against whether anything consumes the docs
  (generated reference, IDE hover, a published SDK).
- **Module/file headers** — usually "no"; option only where the stack's canon has them.
- **TODO policy** — allowed with a tracked reference, or forbidden in favour of backlog tasks
  (the pipeline has a backlog — leaving debt in comments hides it from the board).
- **Long-form docs** — inherited: ADRs and research docs live in `.dev-skills/`; the guide only says
  when code-adjacent docs (a package README) are warranted.

### 4. Error handling

- **Propagation style** — the stack fork: exceptions vs result/either types vs error codes;
  per-language norms decide the option list (Go's `if err != nil` is canon, not a fork; TS and Python
  genuinely fork).
- **Error taxonomy** — expected/domain errors vs bugs; which layer converts one to the other; what
  crosses an API boundary (never a stack trace).
- **Messages & logging** — user-facing text vs internal detail; log-once-at-the-boundary vs
  log-where-caught (double-logging is the anti-pattern to name); structured-log fields if the
  architecture defined them.
- **Recovery conventions** — where retry/fallback logic belongs; never re-decide the architecture's
  resilience decisions — only how they read in code.

### 5. Testing style

Conventions only — the levels, the scoped run and the harness are `design-dev-architecture`'s; the
economy (cheapest level that proves the criterion) is fixed by
`../../_shared/build-pipeline/quality-gate.md` and is inherited, not re-opened.

- **Naming & structure** — test-name pattern (behaviour sentences vs method_state_expected);
  arrange-act-assert vs given-when-then; one behaviour per test as the default.
- **Mock policy** — the real fork: mock only at system boundaries (own code runs real) vs isolate
  every unit. Weigh against the pipeline's bias for proving observable outcomes;
  "mock-everything" must be argued for, not defaulted to.
- **Test data** — factories vs fixtures vs builders; where seed/canonical data lives; no
  copy-pasted 40-line setup blocks.
- **Assertion style** — the stack's idiom (expect/assert flavour), snapshot-testing policy
  (UI only? never for logic?), custom matchers bar.

### 6. Stack-specific strictness

Only what the chosen stack exposes: typing strictness (e.g. TS `strict`, mypy level — recommend the
strictest the team can hold from day one; retrofitting is the expensive path), null/optional
handling, immutability leanings, lint-severity policy (warnings-as-errors or a curated
warning-free set — a warning nobody fails on is a rule nobody follows). Every knob here lands in
`## Enforcement`, not in prose.

## Conditional dimensions

- **API conventions** *(only if the architecture includes an API)* — the API's existence, protocol
  and shape are `design-architecture`'s; here only the style: resource/field naming and casing,
  error-response shape, pagination/versioning conventions, validation-at-the-boundary as a rule.
- **Dependency policy** *(always worth one line, a fork only when the user has a stance)* — the bar a
  new dependency must clear (maintained? does it replace >~50 lines of honest code?), and who
  approves adding one. Pinning/lockfile discipline is inherited from the stack's canon.
- **Inherited, never re-opened here:** formatting (the formatter's, wholesale — name the tool in
  `## Enforcement` and never restate its output in prose) · commit style (the set fixes English
  conventional commits) · design tokens and UI style (`DESIGN.md`, frozen per
  `../../_shared/build-pipeline/design-freeze.md`).

## Preferences from the brief

Where `project-brief.research.md` records code-style leanings ("Code style & idioms",
"Architecture leanings"), fold each into its dimension as a **soft prior**: a tie-breaker among
options that already fit the stack, logged in the Forks / Decisions log with `Source = preference` —
never a reason to fight the stack's canon silently
(`../../_shared/spec-pipeline/elicitation-method.md` → "Read the brief first").

## Research topics (stage 2, budgeted)

Ranked by what would change a convention:

1. **The stack's dominant style guide today** — the official one (PEP 8 + the packaging norms,
   Effective Go, the framework's own conventions) or the de-facto community winner; verify it is
   current, don't quote from memory.
2. **The current formatter/linter/type-checker landscape** for the stack — which tool is the living
   default this year (ecosystems move: check before naming the tool `## Enforcement` depends on),
   and whether it ships rules for the conventions being delegated.
3. **Test-framework idioms** — the chosen/likely framework's own recommended structure and assertion
   style, so the testing dimension inherits rather than invents.
4. **The module-architecture options' currency** — only when dimension 1 is a live fork: what the
   framework's own docs prescribe or forbid.

## What the reviewer probes (priority order)

1. **Edicts where the stack forks** — a real fork presented with one option and no trade-offs; and
   the inverse: manufactured forks where the canon has one answer.
2. **Prose rules a tool could enforce** — anything in the draft guide that belongs in
   `## Enforcement` as a named tool + rule.
3. **Contradictions with the pipeline** — test conventions that violate the quality gate's economy;
   organization rules that would break the scoped-test selection; anything re-opening the stack,
   `DESIGN.md`, or commit style.
4. **Canon fights without a logged reason** — conventions that contradict the stack's cited style
   guide with no `Source = preference` fork behind them; conventions imported wholesale from a
   different ecosystem.
5. **Guide bloat and drift** — a distilled guide over ~120 lines, rationale leaking into it, or a
   guide that says something the research doc never decided.
6. **Untraceable conventions** — a rule that traces to no canon, no architecture fact, and no logged
   preference; missing dimensions (no code-organization or no testing decision is a 🔴).
7. **Naming that ignores the domain model** — a parallel vocabulary where the glossary already has
   the word.
