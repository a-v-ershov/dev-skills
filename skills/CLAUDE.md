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

## How to invoke

Installed as a plugin, the skills are namespaced — invoke them as `dev-skills:<name>`
(e.g. `dev-skills:create-project-spec`). If the directory was copied straight into
`.claude/skills/`, the names are bare (`create-project-spec`). Below they are written bare. Prefer the
**orchestrators** as entry points; every sub-skill is also runnable on its own.

## What the set does: three pipelines, idea → shipped software

### 1. Spec pipeline — raw idea → buildable project documentation (writes docs only)

Entry point: **`create-project-spec`** (a thin conductor that sequences the phases below). Each phase
elicits → researches real-world facts → drafts → runs an adversarial self-review → merges → emits a
detailed `*.research.md` + a short `*.summary.md`. Run settings chosen once (`mode`: `interactive`
pauses at each gate / `autopilot` runs through and logs every decision; `final_summary`;
`project_type`: `greenfield` / `existing`); config in `.dev-skills/project-spec/.spec-config.md`.

| # | Skill | Produces (under `.dev-skills/project-spec/`) |
|---|-------|----------------------------------------|
| 0 | `map-codebase` *(existing projects only)* | `codebase-map.research.md` — reverse-engineered as-is facts (structure, stack, domain, surfaces) |
| 1 | `gather-context` | `project-brief.research.md` — discovery interview; settled intent the rest reads |
| 2 | `validate-idea` | `idea-validation.research.md` — adversarial KILL/SHRINK/forcing-questions pre-filter |
| 3 | `define-product-requirements` | `product-requirements.research.md` — full committed feature set + acceptance criteria + domain model |
| 4 | `create-user-flows` | `user-flows.research.md` |
| 5 | `define-design-decisions` | `design-decisions.research.md` — the product→technical bridge (design direction, not mockups) |
| 6 | `design-architecture` | `architecture.research.md` (+ `adr/`) — requirements-first system architecture |
| 7 | `design-dev-architecture` | `dev-architecture.research.md` (+ `adr/`) — the AI-first inner loop, incl. the custom project skills to author that wrap its dev/test scripts |

**Existing project (brownfield):** with `project_type: existing`, `map-codebase` runs first to chart the
as-is code, then phases 1–7 run in **existing-project mode** — reconstructing a *target* spec from the map
+ the user's intent and logging drift (built-but-divergent / unwanted / not-yet-built). Output is the same
artifacts, so the build pipeline runs unchanged. Method: `_shared/spec-pipeline/existing-project-mode.md`.

### 2. Build pipeline — spec → working software (mutates the repo)

Entry point: **`build-product`** (conducts the build loop). Unlike the spec phase, this one scaffolds,
runs commands, and writes code. **Sequential**: one task at a time, single working tree, no parallelism.
Config in `.dev-skills/build-plan/.build-config.md`.

| # | Skill | Role |
|---|-------|------|
| 1 | `setup-dev-environment` | Execute the documented inner loop; stand up the enforced quality gate (`make check` + hooks) |
| 1b | `create-design-system` *(UI projects)* | After the scaffold is up, make the design direction concrete: a root `DESIGN.md` (Google's tool-neutral tokens+prose). Proposes several candidates, renders each via `generate-mockups`, commits the chosen one. Invoked by setup; self-skips for no-UI |
| 2 | `plan-development` | Turn the spec into a kanban backlog under `.dev-skills/build-plan/tasks/` (one file per task) |
| 3 | `implement-feature` | Build one task into code (fresh per-task agent), UI built against `DESIGN.md` |
| 4 | `verify-feature` | A **separate, unbiased** agent: authors adversarial tests, proves observable outcomes, pass/fail |

`build-product` picks the lowest-id `ready` task (status `todo` with all `blocked_by` `done`), loops
implement ↔ verify (bounded by `max_verify_iterations`; at the cap → `needs_human`), and on a green
quality gate sets it `done` and makes a checkpoint commit. Resumable — the backlog is the source of truth.
The design ladder is **decide → systematize → render**: `define-design-decisions` (spec) decides the
direction, `create-design-system` (build) systematizes it into `DESIGN.md`, and `generate-mockups`
(on demand) renders disposable stub UI variants against it to compare before building.

### 3. Release pipeline — working software → cut release (audits, then ship)

Entry point: **`release-product`** (conducts the release). It proves the **system-level** properties no
single task could — the counterpart of `verify-feature` at the scale of the whole product — then cuts
the release. The audits are **read-only**, so (uniquely here) they **fan out in parallel**; findings are
**filed as `rework` tasks, never fixed in place** (a separate `build-product` run fixes them, then the
audit re-runs). Config in `.dev-skills/release/.release-config.md`.

| # | Skill | Proves against / does |
|---|-------|------------------------|
| 1 | `audit-security` | the STRIDE-lite threat model → `.dev-skills/release/security-audit.md` |
| 2 | `audit-performance` | the quality-attribute scenarios → `.dev-skills/release/performance-audit.md` |
| 3 | `audit-product` | the user flows end-to-end (cross-feature) → `.dev-skills/release/qa-report.md` |
| 4 | `audit-code-health` | rot signals + test-suite quality → `.dev-skills/release/code-health-audit.md` |
| 5 | `audit-accessibility` | the accessibility decisions (WCAG); self-skips with no UI → `.dev-skills/release/accessibility-audit.md` |
| — | `cut-release` | clean tree + no open 🔴 → docs + version bump + changelog + tag/commit/PR (always confirmed; stops before prod deploy) |

`release-product` fans out the enabled audits, ranks findings by severity, files 🔴/🟡 as `rework`
tasks, drives `build-product` to fix them and re-audits (bounded by `max_audit_iterations`; a 🔴 at the
cap → `needs_human`), and when no 🔴 remains invokes `cut-release`. Only a 🔴 blocks the cut; the cut is
the one outward-facing step and always confirms.

## Standalone skills

- **`commit`** — analyze uncommitted changes, group by logic, create well-structured commits (English messages).
- **`generate-mockups`** — on demand, generate several stub UI variants (no logic) for a screen and
  render them against the `DESIGN.md` so you can compare and choose; records the chosen one as a
  design-note on the task. Also used by `create-design-system` (showcase mode) to render its candidates.
  Never writes product code (write-scope guard); never auto-run in the build loop.
- **`propagate-changes`** — after an upstream spec doc is edited, reconcile downstream docs + backlog
  forward, surgically; runs automatically, pauses only on critical/destructive changes. Never writes code.
- **`gather-context`** is also a reusable grill: any phase can call it for a fork blocked on context
  only the user holds, and the user can run it directly to be interviewed on any topic (including
  just their stack/style preferences). It captures the developer's standing preferences (stack, code
  style, design taste, tooling, architecture leanings) as **soft priors** in the brief; downstream
  phases consume them as overridable tie-breakers, logged in their Forks / Decisions log with
  `Source = preference`.

## Where things live

- `.dev-skills/project-spec/` — spec research docs, summaries, `adr/`, `.spec-config.md` (committed; transient
  `*.review.md` is deleted after merge and gitignored).
- `.dev-skills/build-plan/` — backlog (`tasks/`), `board.md`, `.build-config.md` (committed); plus
  `mockups/` — throwaway stub UI variants from `generate-mockups` (gitignored; only the chosen
  screenshot is kept).
- `.dev-skills/project-setup/` — setup log + the verification contract `verify-feature` reads + the
  `design-system.md` record (committed).
- **Root `DESIGN.md`** *(UI projects)* — the committed, tool-neutral design system (tokens + rules)
  `create-design-system` writes and `implement-feature` / `generate-mockups` read.
- `.dev-skills/release/` — per-audit findings docs + `release-summary.md` + `.release-config.md` (committed); the
  audit trail of why a release was, or wasn't, cut.
- The project's **root `CLAUDE.md`** carries a marker-delimited *project documentation map* indexing the
  above and the order to read them before changing code; the spec/setup/plan/release skills keep it current.

## Conventions to respect

- Skills are **verbs**; their outputs are **nouns** (`validate-idea` → `idea-validation`).
- Orchestrators **conduct, they do not duplicate** — they invoke focused sub-skills via the Skill tool
  and spawn the named **agents** (`agents/`: `spec-reviewer`, `spec-researcher`, `implementer`,
  `verifier`, `ui-prototyper`) for the pipelines' subagent roles.
- Shared methodology lives in `_shared/` (no `SKILL.md`): `spec-pipeline/`, `build-pipeline/`, and
  `release-pipeline/` hold the elicitation, research, review, output-format, backlog, quality-gate,
  propagation, audit, severity, and report methods; `agent-guide.md` defines the project-map block. Read
  these for the *how*; don't restate them in skills.
