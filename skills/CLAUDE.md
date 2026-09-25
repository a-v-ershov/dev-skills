# dev-skills — using this skill set

This directory holds the **dev-skills** set: opinionated, reusable coding-workflow skills for
Claude Code. This file is an **orientation map** for an agent that finds these skills available in a
project — it points at the skills and the order to use them; it does not duplicate their logic. Each
skill carries its own full procedure in its `SKILL.md`.

> Loading note: as an installed plugin this file is **not** auto-loaded into a project's context — a
> plugin contributes skills/commands/agents/hooks, not memory. It loads on demand when an agent reads
> files under this directory, and serves as human-readable documentation. Skills are selected by their
> `SKILL.md` `description`; this map just tells you how the pieces fit.

## Cardinal rule: speak the user's language

Every skill here **responds in, and reasons in, the language the user addressed it in** — Russian in,
Russian out; English in, English out. Detect it from the user's message; nothing to configure. This
applies to natural-language text only — never translate code, identifiers, paths, commands, or API
names. When a skill spawns subagents, it tells them the same rule. **One fixed exception:** git commit
messages are always written in English.

**Which words to translate is not left to taste** — `_shared/glossary.md` fixes it: the workflow
vocabulary is translated (`findings` → замечания, `gate` → контрольная точка, `rework` → доработка),
a short list of terms stays in Latin script and uninflected (`fork`, `commit`, `backlog`, `mockup`,
`deploy`, `checklist`, `baseline`, `harness`, `onboarding`, `sanity check`), hybrid verbs
(«закоммитить», «отскаффолдить») are never built, and the templates' structural anchors — section
headings, task fields, config keys — stay verbatim so the pipeline keeps finding them.

## Cardinal rule: one branch — the current one

Every skill here **works on the branch the session is already on**, normally `main`. No skill creates a
branch, switches branches, or opens a worktree on its own initiative — not per task, not per release,
not "to keep `main` clean". **The single exception** is a branch the user explicitly asked for in this
session; then the skill uses the name they gave (or confirms one), says which branch the work is on,
and stays there. Being asked to commit, to fix, or to cut a release is not being asked to branch.

The full rule — including what to do when the session already starts on a non-default branch, and the
one case that genuinely can't proceed without a branch (a PR from the base branch, in `cut-release`) —
is `_shared/git-workflow.md`; every skill carries a compact copy in its `## Git workflow` section and
passes it down to the agents it spawns.

## How to invoke

Installed as a plugin, the skills are namespaced — invoke them as `dev-skills:<name>`
(e.g. `dev-skills:create-project-spec`). If the directory was copied straight into
`.claude/skills/`, the names are bare (`create-project-spec`). Below they are written bare. Prefer the
**orchestrators** as entry points; every sub-skill is also runnable on its own.

## What the set does: three pipelines, idea → shipped software

### 1. Spec pipeline — raw idea → buildable project documentation (writes docs only)

Entry point: **`create-project-spec`** (a thin conductor that sequences the phases below). Each phase
runs eight stages (0–7): intake → elicit → research **within a fixed network budget** (≤4 searches /
≤4 opens, ranked by what would change the build) → draft → an independent, **offline** reviewer
returns findings → apply them in place → emit a detailed `*.research.md` + a short `*.summary.md` →
hard gate. Two run settings, chosen once (`mode`: `interactive` pauses at each gate / `autopilot`
runs through and logs every decision; `final_summary`); config in
`.dev-skills/project-spec/.spec-config.md`.

| # | Skill | Produces (under `.dev-skills/project-spec/`) |
|---|-------|----------------------------------------|
| 1 | `gather-context` | `project-brief.research.md` — discovery interview; settled intent the rest reads |
| 2 | `validate-idea` | `idea-validation.research.md` — adversarial KILL/SHRINK/forcing-questions pre-filter |
| 3 | `define-product-requirements` | `product-requirements.research.md` — full committed feature set (**≤15 features**) + acceptance criteria + domain model |
| 4 | `create-user-flows` | `user-flows.research.md` |
| 5 | `define-design-decisions` | `design-decisions.research.md` — the product→technical bridge (design direction + which UI kit / icon set / theming approach, not mockups) |
| 6 | `design-architecture` | `architecture.research.md` (+ `adr/`) — requirements-first system architecture, incl. where it runs (hosting, environments, cost, residency, manual setup) and how success is measured (analytics/telemetry) |
| 7 | `define-code-style` | `code-style.research.md` + the distilled **`code-style.md`** guide — the development conventions on the chosen stack (code organization, naming, comments, error handling, test style): each real fork weighed as top 2–3 options with trade-offs, everything enforceable delegated to a named lint/formatter rule |
| 8 | `design-dev-architecture` | `dev-architecture.research.md` (+ `adr/`) — the AI-first inner loop, incl. the custom project skills to author that wrap its dev/test scripts |

**When the repo already has code:** no separate mode and no extra phase — each phase reads the code
at its own intake, reports what it found, and confirms instead of re-asking; anything the user wants
different lands in that doc's `## Divergences (code vs intended)` section, which `plan-development`
turns into work. Method: `_shared/spec-pipeline/elicitation-method.md` → "When the repo already has code".


### 2. Build pipeline — spec → working software (mutates the repo)

Entry point: **`build-tasks`** (conducts the build loop). Unlike the spec phase, this one scaffolds,
runs commands, and writes code. **Sequential**: one task at a time, single working tree, no parallelism.
Config in `.dev-skills/build-plan/.build-config.md`.

| # | Skill | Role |
|---|-------|------|
| 1 | `setup-dev-environment` | Execute the documented inner loop; stand up the enforced quality gate (`make check-fast` / `make test-scoped` / `make check` + hooks); for a UI project install the spec's UI kit + icon set and write the root `DESIGN.md` from the spec |
| 2 | `plan-development` | Turn the spec into a kanban backlog under `.dev-skills/build-plan/tasks/` (one file per task) — coarse tasks, **at most 15 open, a ceiling every task-filing skill shares**. Re-run later = amend mode (task deltas), or `consolidate` to merge an overgrown backlog back under the ceiling |
| 3 | `run-task` | **One task, end to end** — the whole cycle for a single task; also takes a free-form request (`origin: adhoc`), and a **quick lane** for a small, provably bounded change (it drops the separate verifier and nothing else) |
| — | `implement-feature` | The implementer agent's procedure: build one task into code, UI against `DESIGN.md` |
| — | `verify-feature` | The verifier agent's procedure: a **separate, unbiased** agent authoring adversarial tests, proving observable outcomes |

`build-tasks` picks the lowest-id `ready` task (status `todo` with all `blocked_by` `done`) and hands
it to `run-task`, which runs the fixed short cycle — build once, verify once in a separate agent,
**one** fix round, quality gate, then human acceptance (or `review: auto` when nothing is
hand-checkable) and a spec catch-up edit if the product changed — then sets it `done` with a
checkpoint commit. **The gate in that loop is the static checks plus the task's own scoped test
selection** — the build phase never runs the whole suite, and tests are written at the cheapest level
that proves the criterion (e2e is the exception, at most one per task); the full suite runs in the
release pipeline (`_shared/build-pipeline/quality-gate.md`). Anything the fix round leaves open goes to `needs_human`; there is no iteration
counter. `build-tasks` stops after **8 tasks** per run (context fills with diffs) and asks for a
`/compact`, and refuses to start when the spec has moved ahead of the plan. Resumable — the backlog is
the source of truth.

Two things make a long run legible and safe to share. Each task carries a **`claim`** — holder, current
stage and a heartbeat, written **before** any agent is spawned — so `board.md` can answer "what is it
doing, and since when?" at any moment, and a **second session** on the same repository skips a task
somebody else holds instead of redoing it. And the implementer **writes its journal into the task file
as it goes**, so an agent killed after fifty minutes is resumed from that journal rather than rebuilt
from zero.

The design ladder is **decide → systematize → render**: `define-design-decisions` (spec) decides the
direction (including the UI kit), `setup-dev-environment` (build) systematizes it into `DESIGN.md`, and `generate-mockups`
(on demand) renders disposable stub UI variants against it to compare before building.

### 3. Release pipeline — working software → cut release (clean, prove, then ship)

Entry point: **`release-product`** (conducts the release). It cleans the tree, closes the test gaps,
proves the **system-level** properties no single task could — the counterpart of `verify-feature` at the
scale of the whole product — briefs the human on what only a person can judge, and then cuts the
release. Config in `.dev-skills/release/.release-config.md`.

The chain has two halves. Steps 1–2 **change the repository**, so they run **sequentially and alone** —
each inside its own preloading agent (`refactorer`, spawned twice around the human's plan approval,
then `test-writer`), so the two longest autonomous runs don't fill the conductor's context.
Steps 3–7 are **read-only**, so (uniquely here) they **fan out in parallel**; steps 8–9 then write the
handover document and brief the human. **This is also where the
whole test suite is run** — `refactor` around its steps, `write-tests` at the end, `cut-release` before
the cut — because the build loop only ever ran each task's own selection. Findings are **filed as
coarse `rework` tasks (one per coherent fix, never one per finding), never fixed in place**; the audits also **never install or configure anything** —
tooling is `setup-dev-environment`'s job, production capabilities are `setup-production-environment`'s.

| # | Skill | Does / proves against |
|---|-------|------------------------|
| 1 | `refactor` | Structure without behaviour change: duplication, dead code, size, suppression debt; plan → approval, small steps, green before and after → `.dev-skills/release/refactor.md` |
| 2 | `write-tests` | Maps the coverage gaps (none / happy-path-only / hollow, mutation-tested) and closes the risky ones **red-first**; a real bug becomes a task and the test stays red → `.dev-skills/release/test-gaps.md` |
| 3 | `audit-security` | the STRIDE-lite threat model + the production surfaces (caps, RLS, prod config) → `.dev-skills/release/security-audit.md` |
| 4 | `audit-performance` | the quality-attribute scenarios → `.dev-skills/release/performance-audit.md` |
| 5 | `audit-product` | the user flows end-to-end (cross-feature) **and** the WCAG target on the same journeys → `.dev-skills/release/qa-report.md` |
| 6 | `audit-dependencies` | the dependency manifests + lockfiles vs the ecosystems' advisory databases — vulnerabilities ranked by reachability, unmaintained/unused/undeclared packages, lockfile drift → `.dev-skills/release/dependency-audit.md` |
| 7 | `simplify-product` | the after-build SHRINK — numbered proposals to drop / merge / simplify features, flow steps, speculative code generality and the product's wording (KPI: easier to understand, easier to use); **proposals, not findings** — filed as rework only on the human's pick, never blocking → `.dev-skills/release/simplification-proposals.md` |
| 8 | `write-readme` | The handover document — the verified clone→run path, what deploying actually takes today, what the receiver must bring, how to reach a clean state → `README.md` |
| 9 | `manual-test` | Read-only briefing for the human's hands-on pass — starting with everything accepted as `review: auto` → `.dev-skills/release/manual-test-brief.md` |
| — | `cut-release` | clean tree + no open 🔴 → docs + version bump + changelog + tag/commit/PR (always confirmed; stops before production) |

`release-product` runs the chain, ranks findings by severity, files 🔴/🟡 as `rework` tasks, drives
**one** `build-tasks` run to fix them and re-runs only the affected audits **once**; anything still open
then is `needs_human` — there is no iteration counter. When no 🔴 remains it invokes `cut-release`. Only
a 🔴 blocks the cut; the cut is the one outward-facing step and always confirms. `simplify-product`'s
proposals sit outside severity entirely: only the ones the human picks become rework tasks, and none
of them ever block.

**Putting the product live is not part of this run.** `setup-production-environment` is invoked by hand.

### Production environment — the outward-facing sibling of `setup-dev-environment`

**`setup-production-environment`** (manual, never auto-run) executes the architecture's **Deployment &
environments** and **Analytics & telemetry** decisions: platform and release channel, the production
database with migrations and backups, configuration and secrets in the target environment, hard spending
caps, analytics events and error tracking, optional CI. Every gap is sorted into three groups before
anything happens — **① repo · ② an authorized provider CLI, one explicit yes per action · ③ only the
human, in a dashboard** — and it ends by **deploying and smoke-testing the live version**, then writing
`.dev-skills/project-setup/production-setup.md` (done / your turn / open) and
`production-runbook.md` ("how to ship", in plain language). This is where everything production-related
lives, so the audits can stay pure audits.

## Standalone skills

- **`commit`** — analyze uncommitted changes, group by logic, create well-structured commits (English messages).
- **`audit-skills`** — *(by hand, never auto-run)* the set's own retrospective: it reads this session's
  transcript (`scan_session.py`) plus the artifacts the run produced, works out how the skills and agents
  that ran actually behaved — wrong or skipped steps, silent gates, repeated work, broken invariants of
  the set, output that misses its template — and reports **numbered edit proposals** against the file
  that owns each rule (`SKILL.md`, an agent, or a `_shared/*.md` method). It proposes only: nothing is
  applied until the caller names numbers, and even then it can write nothing but skill/agent/command
  files (write-scope guard). Not a release audit — it audits the tooling, not the product, and
  `release-product` never invokes it.
- **`optimize-dev`** — *(by hand, time to time)* the periodic development-hygiene pass: a thin
  conductor that invokes `groom-backlog` and then `audit-tests`, passes `autopilot` through, and merges
  the two reports into one; a half whose subject is absent (no backlog / no tests) is skipped with a
  one-line announcement. `[backlog | tests]` narrows it to one half.
- **`groom-backlog`** — sizes every open task (S/M/L/XL) and merges small or same-cause `todo` tasks
  into coherent larger ones per `planning-method.md`'s consolidation rules (only `todo`, nothing lost,
  blockers recomputed, ≤15 open); merge plan confirmed before writing in both modes unless invoked
  with `autopilot`. Merges only — never plans, splits, or builds.
- **`audit-tests`** — measures the suite against the budgets in `verification.md` `## Test budgets`
  (defaults: routine run ≤30 s with **no** e2e; ≤10 e2e total, one per journey, behind an explicit
  release-time target; full suite ≤5 min) and takes the cost out: shared fixtures instead of per-test
  resource creation, test-cost settings for slow-by-design primitives, e2e demoted to the cheapest
  proving level, run tiers split so the budgets are structural (scripts / Makefile / CI). It also
  revises the quarantine: every skip/xfail marker needs a live task id, and a marker is lifted only by
  re-running its test green. Deletion proposed never silent; assertions never weakened; product
  slowness is filed as rework, not patched. Writes `.dev-skills/optimize/test-audit.md`.
- **`generate-mockups`** — on demand, generate several stub UI variants (no logic) for a screen and
  render them against the `DESIGN.md` so you can compare and choose; records the chosen one as a
  design-note on the task. It explores arrangement within the settled design system — never alternative systems.
  Never writes product code (write-scope guard); never auto-run in the build loop.
- **Keeping the spec and the plan in agreement** needs no skill of its own: a spec phase re-run in
  **amend mode** reconciles its own doc and points at `/plan-development`; `plan-development` re-run
  against an existing backlog emits task deltas; `run-task` proposes the spec edit when a task changed
  the product (`spec_sync`). Method: `_shared/build-pipeline/propagation-method.md`.

- **`gather-context`** is also a reusable grill: any phase can call it for a fork blocked on context
  only the user holds, and the user can run it directly to be interviewed on any topic (including
  just their stack/style preferences). It captures the developer's standing preferences (stack, code
  style, design taste, tooling, architecture leanings) as **soft priors** in the brief; downstream
  phases consume them as overridable tie-breakers, logged in their Forks / Decisions log with
  `Source = preference`.

## Where things live

- `.dev-skills/project-spec/` — spec research docs, summaries, `adr/`, the distilled `code-style.md`
  guide (what `implement-feature` / `verify-feature` / `refactor` / `write-tests` write code and tests
  against), `.spec-config.md` (all committed; the pipeline writes nothing transient).
- `.dev-skills/build-plan/` — backlog (`tasks/`), `board.md`, `.build-config.md` (committed); plus
  `mockups/` — throwaway stub UI variants from `generate-mockups` (gitignored; only the chosen
  screenshot is kept).
- `.dev-skills/project-setup/` — setup log + the verification contract `verify-feature` reads + the
  `design-system.md` record, plus `production-setup.md` and `production-runbook.md` from
  `setup-production-environment` (all committed).
- **Root `DESIGN.md`** *(UI projects)* — the committed, tool-neutral design system (tokens + rules)
  `setup-dev-environment` writes and `implement-feature` / `generate-mockups` read.
- `.dev-skills/optimize/` — the periodic hygiene pass's findings (`test-audit.md` from `audit-tests`);
  committed like the rest.
- `.dev-skills/release/` — the release phase's findings (`refactor.md`, `test-gaps.md`, the per-audit
  docs, `simplification-proposals.md`, `manual-test-brief.md`) + `release-summary.md` +
  `.release-config.md` (committed); the audit trail of why a release was, or wasn't, cut.
- The project's **root `CLAUDE.md`** carries a marker-delimited *project documentation map* indexing the
  above and the order to read them before changing code; the spec/setup/plan/release skills keep it current.

## Conventions to respect

- Skills are **verbs**; their outputs are **nouns** (`validate-idea` → `idea-validation`).
- Orchestrators **conduct, they do not duplicate** — they invoke focused sub-skills via the Skill tool
  and spawn the named **agents** (`agents/`: `spec-reviewer`, `spec-researcher`, `implementer`,
  `verifier`, `ui-prototyper`, `refactorer`, `test-writer`) for the pipelines' subagent roles.
- Shared methodology lives in `_shared/` (no `SKILL.md`): `spec-pipeline/`, `build-pipeline/`, and
  `release-pipeline/` hold the elicitation, research, review, output-format, backlog, quality-gate,
  propagation, audit, severity, and report methods — plus `build-pipeline/design-freeze.md` (the
  product's visual decisions are settled once and never re-opened by a skill) and
  `build-pipeline/report-format.md` (every run ends with «What you should do», and timings that add
  up); `agent-guide.md` defines the project-map block;
  `glossary.md` fixes how the workflow vocabulary is rendered in the user's language;
  `git-workflow.md` fixes the one-branch invariant. Read these for the *how*; don't restate them
  in skills.
