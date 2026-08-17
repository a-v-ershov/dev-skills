# Project documentation map (agent guide) — shared

A small, navigational section that lives in the **target project's root `CLAUDE.md`** (the product
repo being specced/built — not this plugin). It orients any coding agent to where the project's own
documentation lives — the spec, the backlog, the setup contract, and the release audits — and the
order to read it in before touching code. It is a **map, not a copy**: it points at the artifacts, it
never restates them.

This is shared methodology: several skills write or refresh the **same** section, each at a natural
moment, all from this one spec — so the behavior is defined once and never duplicated.

## Who writes / refreshes it, and when

- **`create-project-spec`** — *seeds* it at the start of a run (a skeleton describing the spec to
  come) and *finalizes* it at the end (pointing at the real `.dev-skills/project-spec/` artifacts).
- **`setup-dev-environment`** — writes/refreshes it inside the project `CLAUDE.md` it scaffolds in
  the build phase, next to its stack notes + commands (which live **outside** the markers).
- **`plan-development`** — refreshes it after writing the backlog, so `.dev-skills/build-plan/` shows up.
- **`release-product`** — refreshes it after the release audits run (it always runs in the release
  phase, so this is the release phase's primary refresh), so `.dev-skills/release/` shows up.
- **`cut-release`** — refreshes it when finalizing a standalone cut, keeping `.dev-skills/release/` current.

Any of these can also run standalone. The operation is **idempotent** — re-running re-renders the
block in place and never duplicates it.

## Marker discipline (non-destructive — read carefully)

The section is delimited by HTML-comment markers and is the ONLY thing these writers touch:

```
<!-- dev-skills:project-map:start -->
…rendered map…
<!-- dev-skills:project-map:end -->
```

- **Markers present** → replace everything between them; leave the rest of `CLAUDE.md` untouched.
- **No markers but the file exists** → append the block after the top-of-file title/intro; never
  edit, reorder, or delete the user's existing content.
- **No `CLAUDE.md`** → create it with a one-line title + the block.
- Everything **outside** the markers — the user's own notes, `setup-dev-environment`'s
  stack/commands — is owned by someone else. Never rewrite it. (No `.bak` is needed when you only
  replace between the markers.)

## What to map (scan, mark present vs planned)

Scan `.dev-skills/project-spec/`, `.dev-skills/build-plan/`, `.dev-skills/project-setup/`, `.dev-skills/release/`, and the **root
`DESIGN.md`** (UI projects). Emit one row per known artifact, pointing at it. If a file is not there yet (e.g. an early seed before the spec exists),
still list it but mark it **planned** — so the map describes the intended shape from day one. Never
invent artifacts the pipeline does not produce.

Known artifacts (the `.research.md` files are the depth; each has a short `.summary.md` human pair):

- `.dev-skills/project-spec/summary.md` — combined human summary (read first).
- `.dev-skills/project-spec/project-brief.research.md` — the discovery brief (the user's original intent, scope, constraints).
- `.dev-skills/project-spec/idea-validation.research.md` — why this exists (validation).
- `.dev-skills/project-spec/product-requirements.research.md` — features, acceptance criteria, domain model.
- `.dev-skills/project-spec/user-flows.research.md` — the user flows.
- `.dev-skills/project-spec/design-decisions.research.md` — design direction.
- `.dev-skills/project-spec/architecture.research.md` (+ `adr/`) — system architecture + decisions.
- `.dev-skills/project-spec/code-style.md` — the distilled style guide (organization, naming, comments,
  errors, tests) code is written against; its `code-style.research.md` pair holds the rationale.
- `.dev-skills/project-spec/dev-architecture.research.md` — inner loop (local run, testing, AI tooling).
- `.dev-skills/build-plan/board.md` (+ `tasks/*.md`) — the backlog (what to build next).
- `.dev-skills/project-setup/verification.md` — run / drive / prove commands.
- `.dev-skills/project-setup/setup-log.md` — what the env provides + manual TODOs.
- `DESIGN.md` *(repo root, UI projects)* — the committed design system (tokens + rules) UI code is built against.
- `.dev-skills/project-setup/design-system.md` — *(UI projects)* how the design system was chosen (the *why* behind `DESIGN.md`).
- `.dev-skills/release/release-summary.md` — release readiness + what shipped (the verdict).
- `.dev-skills/release/*.md` — the release phase's findings: `refactor.md`, `test-gaps.md`, the per-audit
  docs (security, performance, product+accessibility), and `manual-test-brief.md` — the audit trail.

## Rendered template (emit this between the markers)

Set each `Status` from what exists at write time: `✓` present · `◦` planned. Keep the block short —
it is a map, not a summary. Drop rows for trees that will never exist if you know they won't (rare).

```markdown
<!-- dev-skills:project-map:start -->
## Project documentation map

This project is specced and planned with dev-skills. The docs under `.dev-skills/` are the source of
truth for *what* to build and *why* — read them before changing code, and flag (don't silently
absorb) any place where the code and the docs disagree; propagate real changes with
`plan-development` amend mode.

**Read in this order before implementing:**
1. `.dev-skills/project-spec/summary.md` — the whole project in one read.
2. The task you're on under `.dev-skills/build-plan/` — its `## Description`, acceptance criteria, `traces_to`.
3. The spec sections it traces to (the rows below).
4. `.dev-skills/project-setup/verification.md` — how to run it and prove the change works.
5. `.dev-skills/project-spec/code-style.md` — the style guide code and tests are written against.
6. For UI work, the root `DESIGN.md` — the design system (tokens + rules) to build against.

**Map** — Status: `✓` present · `◦` planned

| Status | Doc | What it is |
|--------|-----|------------|
| ✓ | `.dev-skills/project-spec/summary.md` | Combined human summary — start here |
| ✓ | `.dev-skills/project-spec/product-requirements.research.md` | Features, acceptance criteria, domain model |
| ✓ | `.dev-skills/project-spec/user-flows.research.md` | User flows |
| ✓ | `.dev-skills/project-spec/design-decisions.research.md` | Design direction |
| ✓ | `.dev-skills/project-spec/architecture.research.md` (+ `adr/`) | System architecture + decisions |
| ✓ | `.dev-skills/project-spec/code-style.md` | Style guide — organization, naming, comments, errors, tests |
| ✓ | `.dev-skills/project-spec/dev-architecture.research.md` | Local run, testing, AI tooling |
| ◦ | `.dev-skills/build-plan/board.md` (+ `tasks/*.md`) | Backlog — what to build next |
| ◦ | `.dev-skills/project-setup/verification.md` | Run / drive / prove commands |
| ◦ | `DESIGN.md` (root) | Design system — tokens + rules UI is built against *(UI projects)* |
| ◦ | `.dev-skills/release/release-summary.md` | Release readiness + what shipped |
| ◦ | `.dev-skills/release/*-audit.md` | Per-audit findings (the audit trail) |
<!-- dev-skills:project-map:end -->
```

## Language

Render the prose in the user's language, like every skill — but keep file paths, identifiers, the
markers, and the acceptance keywords verbatim. Never translate them.

**Terms.** How the workflow vocabulary is rendered is governed by `glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.
