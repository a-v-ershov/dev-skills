# Existing-project mode (shared — spec pipeline)

How any spec phase behaves when it is specifying an **already-built** codebase instead of a
greenfield idea. The greenfield pipeline elicits the spec from the user's head; existing-project
mode **reconstructs it from the code**, then uses the user only to supply the intent the code can't
show. This is the single source of truth for that behavior — every phase carries a thin
`## Existing-project mode` section that points here, the way `## Amend mode` sections point at
`propagation-method.md`. Nothing here is restated in a `SKILL.md`.

## When it applies

A phase runs in existing-project mode when **both** hold:

- `.dev-skills/project-spec/.spec-config.md` has `project_type: existing` (see `pipeline-config.md`), and
- `.dev-skills/project-spec/codebase-map.research.md` exists — the as-is facts charted by `map-codebase`,
  the brownfield front phase that runs before `gather-context`.

If `project_type` is absent or `greenfield`, every phase runs exactly as before — this doc is inert
and the new drift columns (below) stay blank. Full back-compat.

## The core idea: AS-IS vs TARGET

The codebase map records **what is built** (AS-IS). The spec records **what is intended** (TARGET).
Existing-project mode is the disciplined reconciliation of the two:

- Where AS-IS already matches intent, the spec ratifies it (and `plan-development` marks it done).
- Where they diverge, that gap is **drift**, logged explicitly, and becomes build work later.

The phase's output doc describes the **TARGET** state (per the pipeline's drift-semantics decision:
the spec is the target; the gap becomes tasks). The AS-IS facts live in the codebase map; the
*divergence* between them lives in this phase's `## Forks / Decisions log`.

## The five-step contract (every phase runs this)

1. **Read the map (+ the brief).** At intake, in addition to the prior phase's research doc, read
   the section of `codebase-map.research.md` this phase consumes (table below) and the user's intent
   from `project-brief.research.md`. Treat map facts marked **observed** as settled; **claimed** and
   **unknown** as things to confirm.
2. **Draft inferred AS-IS answers first.** Pre-fill this phase's own dimensions *from the code*
   before asking the user anything — features from implemented surfaces, flows from routing,
   components from the realized structure, and so on. This is the elicitation method's "self-answer
   from evidence before asking" applied to a codebase. Never make the user narrate their own code.
3. **Interview to confirm + capture intent + set TARGET + flag drift.** Run the phase's normal
   elicit loop, but mirror each AS-IS inference back as a target question: *"the code does X — is X
   the intended target, or drift you want changed?"* Record one of three outcomes per item:
   - **keep** — AS-IS = TARGET (no drift; ratified).
   - **change** — TARGET differs from AS-IS (drift; becomes a `rework` task later).
   - **remove** — AS-IS exists but isn't wanted (drift; becomes a removal/non-goal — destructive).
   Intent the code doesn't yet realize is captured as **TARGET-only** (a new feature later).
4. **Write the artifact oriented to TARGET; log every divergence.** The `.research.md` describes the
   intended state. Each keep-with-no-drift needs no log entry; each **change / remove / TARGET-only**
   is logged in `## Forks / Decisions log` using the drift columns (below) so `plan-development` can
   diff TARGET against AS-IS mechanically.
5. **Same dual output + review.** Research doc + human summary; adversarial review merged then
   deleted — unchanged. In existing mode the reviewer gets one extra job: **verify AS-IS claims
   against the map** — flag any place the spec says a thing is "already built" when the map shows no
   such surface, or vice versa.

## Drift-log convention

Existing mode adds three **optional** columns to the standard `## Forks / Decisions log` table (see
`output-format.md`): `AS-IS`, `TARGET`, and `Drift?`. They are filled only for forks that involve a
keep/change/remove decision or a TARGET-only addition; left blank otherwise (and entirely absent in
greenfield). Drift values: `no` (keep) · `change` · `remove` · `new` (TARGET-only). `plan-development`
delta mode reads exactly this to decide each task's fate (see `../build-pipeline/planning-method.md`).

## What each phase extracts from the map, and what changes

| Phase | Reads from the map | What's different in existing mode |
|-------|--------------------|-----------------------------------|
| `gather-context` | the whole map (it runs right after) | reframes the intake interview from "what do you want to build?" to "here's what you've built — what's the intended direction, what's drift you want fixed, what's deliberate?" — self-answering from the map |
| `validate-idea` | observations & risks | validates the **go-forward**, not existence — see below |
| `define-product-requirements` | surfaces/routes → features; ORM/migrations/types → domain model + glossary | pre-fills the committed feature set from implemented surfaces; reconciles the domain model to the code's real vocabulary; acceptance criteria written for TARGET |
| `create-user-flows` | routing + navigation + auth touchpoints | draws the de-facto AS-IS flows first, then marks each step keep/change/remove and adds TARGET flows |
| `define-design-decisions` | UI deps + design system + platforms as present | records the realized design direction, then sets TARGET; an AS-IS choice to be swapped is drift + an architecture input |
| `design-architecture` | structure + deps → realized component map & stack | still elicits quality-attribute scenarios **first**, then documents AS-IS as one option and weighs keep-as-is vs change per component; ADR status `adopted` ratifies existing decisions |
| `design-dev-architecture` | build/run/CI/test/env as present | designs the inner loop around what already runs; does **not** re-open the stack (settled by adopted ADRs); gaps become TARGET items |

## The naming default

The code's de-facto glossary (table names, model classes, route names) will often disagree with the
clean vocabulary `define-product-requirements` would invent. **Default: keep the code's existing
names** — it's cheaper and produces less drift. A rename is opt-in: if the user wants one, it is
itself drift (`change`) and becomes a refactor task later, not a silent spec relabel.

## The awkward phase: `validate-idea`

Adversarially asking "should this exist?" about a product that already exists is theater. In
existing mode `validate-idea` **validates the go-forward, not the existence**: verdicts shift to
`continue | shrink-the-target | pivot | sunset`. It pressure-tests the *new intent* and the
*unbuilt TARGET delta*, using the map's observations as adversarial fuel (e.g. "the code has zero
usage instrumentation — you can't claim traction"). For a pure "document what exists so we can
extend it" run with no new bets, it **self-skips with a one-line logged rationale** (the same
self-skip the amend contract uses); the orchestrator allows the skip in existing mode and does not
treat it as a stop. A `sunset` or `pivot` verdict on a live product is heavier than a greenfield
`kill` — word it so an autopilot run can never recommend one quietly (see autopilot rule below).

## Adopted-done is provisional

`map-codebase` reads code; it does not run it. A surface that exists may still be broken. So a
feature ratified as AS-IS = TARGET is "adopted-done" only **provisionally** — `plan-development`
delta mode pairs each one with a verification task so `verify-feature` proves it against its
acceptance criteria before it is truly trusted. Phases write acceptance criteria for matching
features too, precisely so that regression net exists.

## Autopilot

Existing mode is orthogonal to `mode` (interactive | autopilot) and stacks with it:

- **interactive** — every keep/change/remove decision and every drift call is a fork the user
  confirms at the phase's gates. This is the safe default; brownfield decisions carry the most
  downside.
- **autopilot** — the AI resolves keep/change/remove itself from the map + brief + best judgment and
  logs each in the Forks / Decisions log. **Anything that discards or rewrites working code**
  (`change` of a substantial component, any `remove`, a `sunset`/`pivot` verdict) is marked
  `Needs human confirm? = yes` so it surfaces loudly in the human summary — the brownfield analog of
  a destructive backlog delta. Autopilot changes *who answers*, never *whether it's recorded*.
