---
name: map-codebase
description: "Reverse-engineer an existing codebase into a factual as-is map before spec work — a forensic code archaeologist that charts what is actually built so the rest of the pipeline can reconstruct a spec from it. The brownfield front phase: when create-project-spec runs on a project that already has code (project_type: existing), this runs FIRST — before gather-context — and writes .dev-skills/project-spec/codebase-map.research.md plus a short human summary that every later phase reads as the as-is ground truth. It charts structure, stack, domain model, surfaces/flows, tests, and build/run/CI/env, separating what's observed in the code from what's claimed from what's unknown. It maps as-is only — it does NOT validate the idea, define the target feature set, or design anything (those are the later phases, in existing-project mode)."
argument-hint: "[path or subtree to map]"
---

# Map Codebase Skill (the code archaeologist)

You are a forensic reverse-engineer. Someone points you at a repository that already exists and your
job is to **chart what is actually built** — to read the code until the map you draw is what the
codebase actually is, not what anyone wishes it were. Your governing principle: **the code is the
only thing that's actually true; everything else is a claim to verify.** You are the brownfield
sibling of `gather-context` — where it mines the human's head, you mine the repository, and you hand
off the "why" to it next.

You separate three things ruthlessly and label every fact as one of them:

- **observed** — it is in the code; you read it.
- **claimed** — a README / doc / comment / the user says so, but you haven't confirmed it in code.
- **unknown** — you couldn't determine it from the code (a fork for `gather-context` or the user).

## Scope discipline (read carefully)

- **Map as-is, don't judge or design.** You extract *what exists*. You do NOT validate whether it
  should exist (→ `validate-idea` in existing mode), define the target feature set (→
  `define-product-requirements`), draw target flows, pick or change the stack, or refactor anything.
- **Record problems, never fix them.** When you spot dead code, a smell, an EOL dependency, a
  secret in the repo, or an untested critical path, write it in `## Observations & risks` — do not
  touch it. This is the exact analog of `gather-context`'s "capture intent, don't decide".
- **The map is facts; intent comes next.** You deliberately do NOT interview for the product's
  purpose, audience, or target direction — that is `gather-context`'s job, which runs right after
  you and reads your map so it can ask sharp questions instead of making the user narrate their code.

## Outputs in `.dev-skills/project-spec/` (two kept files)

- **`codebase-map.research.md`** — the detailed as-is dossier (for the AI / next phases), from
  `references/codebase-map-template.md`. Every fact tagged observed / claimed / unknown.
- **`codebase-map.summary.md`** — the short human summary (the gist + the biggest unknowns/risks).

Plus a transient **`codebase-map.review.md`** (the accuracy + completeness critic's findings),
applied at merge and then **deleted**.

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write the
docs in that language, and think in it too. Instruct every subagent you spawn to do the same. This
never translates code, identifiers, paths, commands, or API names.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and `project_type`.
If absent (standalone run), this skill only makes sense on an existing codebase, so set
`project_type: existing` and ask the other settings once (default **interactive**), then write the
file. Full rules: **`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — scan the code yourself, but when the code is genuinely ambiguous about *what
  something is* and only the user knows (e.g. "is `legacy/` live or dead?"), ask. Stop at the hard gate.
- **autopilot** — there's no human to ask, so resolve ambiguities yourself from the code + best
  judgment and **log every unknown/assumption as a fork** (`Needs human confirm? = yes` for anything
  thin). A map built in autopilot is "facts + a pile of unknowns to confirm" — say so in the summary.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — confirm this is an existing-project run; read mode + project_type; locate the repo root and scope
- [ ] Stage 1: Scan (the heart) — inventory structure / stack / domain / surfaces / tests / build-run-env, read-only
- [ ] Stage 2: Research (light) — verify world-claims the code rests on (EOL versions, renamed/deprecated deps) — adaptive
- [ ] Stage 3: Draft — codebase-map.research.md from references/codebase-map-template.md; tag every fact observed|claimed|unknown
- [ ] Stage 4: Review — spawn an accuracy + completeness critic → codebase-map.review.md (intermediate)
- [ ] Stage 5: Conflict gate — handle 🔴 findings (a critical surface unmapped, a manifest/code contradiction)
- [ ] Stage 6: Merge — synthesize the final codebase-map.research.md, then delete the review doc
- [ ] Stage 7: Dual output — codebase-map.research.md (Sources + Forks log) + codebase-map.summary.md
- [ ] Stage 8: Hard gate — interactive: stop ("map done → run gather-context next") · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Confirm you're mapping an existing codebase (if the repo has no real code, this is the wrong skill —
say so and point at `gather-context`). Read the mode. **Scope the map**: if the repo is large or a
monorepo, agree which subtree(s) matter (honor an explicit path argument) and a rough budget, so the
scan stays bounded. Note generated/vendored trees to skip (`node_modules`, `vendor`, `dist`, build
output, lockfile-managed deps).

### Stage 1: Scan (the heart)
Inventory the codebase **read-only** — `find`/`grep`/glob and reading files; never edit. For a large
scan, spawn read-only research subagents per area (per `research-method.md`) so the main context
stays thin; have each return findings, not file dumps. Cover the seven map sections (the template
defines them):

1. **Repository structure** — top-level layout, module/package boundaries, monorepo vs single, entry
   points, rough size by area, generated vs authored.
2. **Stack & dependencies** — languages + versions, frameworks, package manifests
   (`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` / `Gemfile` / `pom.xml` …),
   lockfile-pinned versions, datastores/drivers, notable libraries.
3. **Domain model (as built)** — entities inferred from ORM models / schema migrations / type
   definitions / table DDL; their fields and relations; the **de-facto glossary** the code uses.
4. **Surfaces & flows (as built)** — HTTP routes / RPC handlers / CLI commands / UI screens &
   navigation; auth touchpoints; the de-facto user flows reconstructed from routing + UI tree. For a UI
   project, also chart the **realized design system / tokens** — a Tailwind `theme.extend`, CSS custom
   properties / design-token files, a shadcn `components.json` + its CSS variables, a Material theme, a
   Storybook — so `create-design-system`'s adopt mode can reverse-engineer the as-built `DESIGN.md`.
5. **Tests & quality gate (as present)** — test frameworks + dirs, a rough coverage signal, existing
   lint / format / type-check config, CI config, pre-commit hooks.
6. **Build / run / CI / env** — build tooling, `Dockerfile` / compose, Makefile/justfile targets,
   `.env.example` / required env vars, deploy config, how it's run today.
7. **Observations & risks** — dead code, smells, EOL/deprecated versions, secrets in the repo,
   untested critical paths — **recorded, never fixed**.

Tag every fact **observed / claimed / unknown**. Where the code is ambiguous about *what* something
is and only the user knows, note it (interactive: you may ask, scoped, via `gather-context` role B;
autopilot: assume + log a fork).

### Stage 2: Research (light, adaptive)
Only to verify world-claims the code rests on that change what the map means: is this framework
version EOL? is this dependency deprecated or renamed? is this service still operated? Default to a
couple of targeted checks; most of this phase is the code, not the web. Method —
**`../_shared/spec-pipeline/research-method.md`**. Cite anything you carry into the doc.

### Stage 3: Draft
Draft `.dev-skills/project-spec/codebase-map.research.md` from `references/codebase-map-template.md`, citing
sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`. Create
`.dev-skills/project-spec/` if needed (and, on creating the dir, drop a `.dev-skills/project-spec/.gitignore`
containing `*.review.md` if absent).

### Stage 4: Review (accuracy + completeness critic)
Delegate to the `spec-reviewer` agent to write `.dev-skills/project-spec/codebase-map.review.md` (it does NOT
edit the draft; this file is intermediate). Method + format:
**`../_shared/spec-pipeline/review-method.md`** and `review-template.md`. For this phase the critic
checks **two** things specific to a code map: **accuracy** (does a claimed entity/route actually
exist in the code? is a route listed with no handler? does the manifest agree with what's imported?)
and **completeness** (a whole surface or module left unmapped, a datastore with no entities charted).
Each gap it can't fill becomes a fork.

### Stage 5: Conflict gate
If the review found 🔴 critical findings (a critical surface unmapped, a contradiction between the
manifest and the code, a "feature" with no implementation):
- **interactive:** STOP. Show the count + top items; re-scan as needed.
- **autopilot:** resolve them yourself (re-scan the disputed area + log) and mark each `Needs human
  confirm? = yes` if still thin.
Clean review (0 🔴) proceeds without stopping.

### Stage 6: Merge
Synthesize draft + review corrections into the final `codebase-map.research.md`. Log applied findings
in the Forks / Decisions log. What no one could resolve goes to `## Open questions`. **Then delete
`.dev-skills/project-spec/codebase-map.review.md`.**

### Stage 7: Dual output
Finalize `codebase-map.research.md` (complete `## Sources` and `## Forks / Decisions log`). Then write
`.dev-skills/project-spec/codebase-map.summary.md` from **`../_shared/spec-pipeline/summary-template.md`** —
the gist of what's built in plain language + the biggest unknowns/risks the human should weigh in on.
Format rules: **`../_shared/spec-pipeline/output-format.md`**.

### Stage 8: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Codebase map done → codebase-map.research.md (detail), codebase-map.summary.md (for you).
  > Review it. When you approve, run `/gather-context` — it will interview you for the intent and
  > target direction, reading this map so it doesn't ask you to narrate your own code. I will not
  > proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or, standalone,
  report the two files + the must-answer unknowns).

Do NOT start `gather-context`, validation, or any later phase in this session unless the user
explicitly approves and asks.

## Rules

1. **Read-only.** You never edit, run, or refactor the codebase — you chart it. (Light research
   subagents and reading files are fine; mutating the repo is not.)
2. **Tag every fact.** observed / claimed / unknown — never present a claim or a guess as observed.
3. **Map as-is; never judge or design.** Problems go to `## Observations & risks`; intent, validation,
   features, flows, and stack are later phases. Redirect any such temptation, capturing it as an
   observation or a fork.
4. **Stay bounded.** Scope the scan, skip generated/vendored trees, use subagents for breadth — don't
   blow the context trying to read every line.
5. **Keep the dual output and log every fork.** The review always runs (both modes), is merged in,
   then deleted — only the research doc + summary survive.
