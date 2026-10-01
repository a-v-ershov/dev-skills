# dev-skills — using this skill set

An **orientation map** for an agent that finds these skills in a project: which skills exist and in
what order to use them. Each skill's full procedure is its own `SKILL.md`.

> As an installed plugin this file is **not** auto-loaded — a plugin contributes skills, agents and
> hooks, not memory. It loads when an agent reads this directory. Skills are selected by their
> `SKILL.md` `description`; this map only shows how the pieces fit.

## Cardinal rule: speak the user's language

Every skill **responds and reasons in the language the user addressed it in**, detected from the
message. Natural-language text only — never translate code, identifiers, paths, commands or API names;
subagents inherit the rule. **Git commit messages are always English.** `_shared/glossary.md` fixes
the vocabulary: workflow terms are translated (`findings` → замечания, `gate` → контрольная точка,
`rework` → доработка), a short list stays Latin and uninflected (`fork`, `commit`, `backlog`,
`mockup`, `deploy`, `checklist`, `baseline`, `harness`, `onboarding`, `sanity check`), hybrid verbs
(«закоммитить») are never built, and template anchors — section headings, task fields, config keys —
stay verbatim so the pipeline keeps finding them.

## Cardinal rule: one branch — the current one

Every skill **works on the branch the session is on**, normally `main`. No skill creates or switches
a branch or opens a worktree on its own initiative. **The single exception** is a branch the user
explicitly asked for in this session; being asked to commit, fix or cut a release is not that. Full
rule, including the non-default-branch case and the one step that can't proceed without a branch (a
PR from the base branch, in `cut-release`): `_shared/git-workflow.md`.

## How to invoke

Installed as a plugin, skills are namespaced: `dev-skills:<name>`. Copied into `.claude/skills/`,
they are bare (`create-project-spec`) — written bare below. Prefer the **orchestrators** as entry
points; every sub-skill also runs on its own.

## Three pipelines, idea → shipped software

### 1. Spec pipeline — raw idea → buildable documentation (writes docs only)

Entry point: **`create-project-spec`** (sequences the phases below). Each phase runs stages 0–7:
intake → elicit → research within a fixed budget (≤4 searches / ≤4 opens, ranked by what would
change the build) → draft → an independent **offline** reviewer returns findings → apply them in place
→ `*.research.md` + short `*.summary.md` → hard gate. Settings chosen once in
`.dev-skills/project-spec/.spec-config.md`: `mode` (`interactive` pauses at each gate / `autopilot`
runs through and logs every decision) and `final_summary`.

| # | Skill | Produces (under `.dev-skills/project-spec/`) |
|---|-------|----------------------------------------|
| 1 | `gather-context` | `project-brief.research.md` — discovery interview; settled intent the rest reads |
| 2 | `validate-idea` | `idea-validation.research.md` — adversarial KILL/SHRINK/forcing-questions pre-filter |
| 3 | `define-product-requirements` | `product-requirements.research.md` — committed feature set (**≤15 features**) + acceptance criteria + domain model |
| 4 | `create-user-flows` | `user-flows.research.md` |
| 5 | `define-design-decisions` | `design-decisions.research.md` — design direction + UI kit / icon set / theming (not mockups) |
| 6 | `design-architecture` | `architecture.research.md` (+ `adr/`) — system architecture incl. where it runs (hosting, environments, cost, residency) and how success is measured (analytics/telemetry) |
| 7 | `define-code-style` | `code-style.research.md` + the distilled **`code-style.md`** — conventions on the chosen stack; each fork weighed as top 2–3 options, everything enforceable delegated to a named lint/formatter rule |
| 8 | `design-dev-architecture` | `dev-architecture.research.md` (+ `adr/`) — the AI-first inner loop incl. the project skills that wrap its dev/test scripts |

**Repo already has code:** no separate mode — each phase reads the code at intake, reports what it
found and confirms instead of re-asking; differences land in `## Divergences (code vs intended)`,
which `plan-development` turns into work (`_shared/spec-pipeline/elicitation-method.md` → "When the
repo already has code").

### 2. Build pipeline — spec → working software (mutates the repo)

Entry point: **`build-tasks`**. **Sequential**: one task at a time, single working tree. Config in
`.dev-skills/build-plan/.build-config.md`.

| # | Skill | Role |
|---|-------|------|
| 1 | `setup-dev-environment` | Execute the documented inner loop; stand up the quality gate (`make check-fast` / `make test-scoped` / `make check` + hooks); for a UI project install the UI kit + icon set and write the root `DESIGN.md` |
| 2 | `plan-development` | Spec → kanban backlog in `.dev-skills/build-plan/tasks/` (one file per task) — coarse tasks, **at most 15 open**, a ceiling every task-filing skill shares. Re-run = amend mode (task deltas) or `consolidate` |
| 3 | `run-task` | **One task end to end**; also a free-form request (`origin: adhoc`) and a **quick lane** for a small bounded change (drops only the separate verifier) |
| — | `implement-feature` | The implementer agent's procedure: one task into code, UI against `DESIGN.md` |
| — | `verify-feature` | The verifier agent's procedure: a **separate, unbiased** agent authoring adversarial tests |

`build-tasks` picks the lowest-id `ready` task (`todo` with all `blocked_by` `done`) and hands it to
`run-task`: build once, verify once in a separate agent, **one** fix round, gate, human acceptance (or
`review: auto` when nothing is hand-checkable), spec catch-up if the product changed, `done` +
checkpoint commit. **The gate is the static checks plus the task's own scoped tests** — never the
whole suite, which runs in the release pipeline (`_shared/build-pipeline/quality-gate.md`); tests are
written at the cheapest proving level (e2e at most one per task). Leftovers go to `needs_human`, no
iteration counter. `build-tasks` stops after **8 tasks** per run and asks for `/compact`, and refuses to
start when the spec moved ahead of the plan. Resumable — the backlog is the source of truth.

Each task carries a **`claim`** (holder, stage, heartbeat) written **before** any agent is spawned, so
`board.md` answers "what is it doing, since when?" and a second session skips a held task; the
implementer journals into the task file as it goes, so a killed agent is resumed, not rebuilt.

Design ladder **decide → systematize → render**: `define-design-decisions` decides the direction,
`setup-dev-environment` systematizes it into `DESIGN.md`, `generate-mockups` (on demand) renders stub
variants against it.

### 3. Release pipeline — working software → cut release

Entry point: **`release-product`**. Config in `.dev-skills/release/.release-config.md`. Steps 1–2
**change the repository** and run sequentially, each in its own preloading agent (`refactorer`,
spawned twice around the human's plan approval; `test-writer`). Steps 3–7 are **read-only** and fan out
**in parallel**; 8–9 write the handover and brief the human. **The whole suite runs here** —
`refactor` around its steps, `write-tests` at the end, `cut-release` before the cut. Findings are
**filed as coarse `rework` tasks (one per coherent fix), never fixed in place**; audits **never install
or configure anything**.

| # | Skill | Does / proves against |
|---|-------|------------------------|
| 1 | `refactor` | Structure without behaviour change; plan → approval, small steps, green before and after → `.dev-skills/release/refactor.md` |
| 2 | `write-tests` | Maps coverage gaps (none / happy-path-only / hollow) and closes the risky ones **red-first**; a real bug becomes a task, the test stays red → `.dev-skills/release/test-gaps.md` |
| 3 | `audit-security` | STRIDE-lite threat model + production surfaces (caps, RLS, prod config) → `.dev-skills/release/security-audit.md` |
| 4 | `audit-performance` | the quality-attribute scenarios → `.dev-skills/release/performance-audit.md` |
| 5 | `audit-product` | the user flows end-to-end **and** the WCAG target on the same journeys → `.dev-skills/release/qa-report.md` |
| 6 | `audit-dependencies` | manifests + lockfiles vs advisory databases — vulnerabilities by reachability, unmaintained/unused/undeclared packages, lockfile drift → `.dev-skills/release/dependency-audit.md` |
| 7 | `simplify-product` | the after-build SHRINK — numbered proposals to drop / merge / simplify features, flow steps, speculative generality, wording; **proposals, not findings** — rework only on the human's pick, never blocking → `.dev-skills/release/simplification-proposals.md` |
| 8 | `write-readme` | The handover: verified clone→run path, what deploying takes, what the receiver must bring → `README.md` |
| 9 | `manual-test` | Read-only briefing for the human's hands-on pass, `review: auto` items first → `.dev-skills/release/manual-test-brief.md` |
| — | `cut-release` | clean tree + no open 🔴 → docs + version bump + changelog + tag/commit/PR (always confirmed; stops before production) |

`release-product` ranks findings, files 🔴/🟡 as `rework`, drives **one** `build-tasks` run and re-runs
only the affected audits **once**; the rest is `needs_human`. Only a 🔴 blocks the cut; the cut always
confirms. `simplify-product` proposals sit outside severity. **Going live is not part of this run.**

### Production environment

**`setup-production-environment`** (manual, never auto-run) executes the architecture's **Deployment &
environments** and **Analytics & telemetry** decisions: platform and release channel, production
database with migrations and backups, config and secrets, hard spending caps, analytics and error
tracking, optional CI. Every gap is sorted first — **① repo · ② authorized provider CLI, one explicit
yes per action · ③ only the human, in a dashboard** — then it **deploys and smoke-tests** and writes
`.dev-skills/project-setup/production-setup.md` (done / your turn / open) and `production-runbook.md`.

## Standalone skills

- **`commit`** — group uncommitted changes by logic into well-structured commits (English messages).
- **`audit-skills`** *(by hand)* — the set's retrospective: reads every recorded session that ran the
  plugin (`scan_session.py`; or one session, or a date window) and the artifacts, finds how the
  skills and agents actually behaved (skipped steps, silent gates, repeated work, broken invariants,
  output off-template) and reports
  **numbered edit proposals** against the owning file. Applies nothing until the caller names numbers;
  writes only skill/agent/command files. Audits the tooling, not the product.
- **`optimize-dev`** *(by hand, periodically)* — conducts `groom-backlog` then `audit-tests`, passes
  `autopilot` through, merges the reports; a half with no subject is skipped. `[backlog | tests]`
  narrows it.
- **`groom-backlog`** — sizes open tasks (S/M/L/XL) and merges small or same-cause `todo` tasks per
  `planning-method.md`'s consolidation rules (only `todo`, nothing lost, blockers recomputed, ≤15 open);
  plan confirmed before writing unless `autopilot`. Merges only.
- **`audit-tests`** — measures the suite against `verification.md` `## Test budgets` (defaults: routine
  run ≤30 s with **no** e2e; ≤10 e2e total behind a release-time target; full suite ≤5 min) and takes
  the cost out (shared fixtures, test-cost settings, e2e demoted, run tiers split structurally).
  Revises the quarantine: every skip/xfail needs a live task id and is lifted only by a green re-run.
  Deletion proposed, never silent; assertions never weakened; product slowness filed as rework. Writes
  `.dev-skills/optimize/test-audit.md`.
- **`generate-mockups`** — on demand, several stub UI variants for a screen rendered against
  `DESIGN.md`; the chosen one becomes a design-note on the task. Arrangement within the settled design
  system only; never product code; never auto-run.
- **Spec ↔ plan agreement** needs no skill: a spec phase re-run in **amend mode** reconciles its doc
  and points at `/plan-development`; `plan-development` re-run emits task deltas; `run-task` proposes
  the spec edit when a task changed the product (`spec_sync`).
  Method: `_shared/build-pipeline/propagation-method.md`.
- **`gather-context`** is also a reusable grill: any phase calls it for a fork blocked on context only
  the user holds; run directly it interviews on any topic and records standing preferences (stack,
  style, design taste, tooling) as **soft priors** downstream phases log with `Source = preference`.

## Where things live

- `.dev-skills/project-spec/` — research docs, summaries, `adr/`, the distilled `code-style.md` (what
  `implement-feature` / `verify-feature` / `refactor` / `write-tests` write against), `.spec-config.md`.
- `.dev-skills/build-plan/` — `tasks/`, `board.md`, `.build-config.md`; `mockups/` (gitignored, only
  the chosen screenshot is kept).
- `.dev-skills/project-setup/` — setup log, the verification contract `verify-feature` reads,
  `design-system.md`, `production-setup.md`, `production-runbook.md`.
- **Root `DESIGN.md`** *(UI projects)* — the tool-neutral design system `setup-dev-environment` writes
  and `implement-feature` / `generate-mockups` read.
- `.dev-skills/optimize/` — `test-audit.md` from `audit-tests`.
- `.dev-skills/release/` — `refactor.md`, `test-gaps.md`, the per-audit docs,
  `simplification-proposals.md`, `manual-test-brief.md`, `release-summary.md`, `.release-config.md`.
- The project's **root `CLAUDE.md`** carries a marker-delimited *project documentation map* indexing
  the above; the spec/setup/plan/release skills keep it current.

Everything is committed; the pipeline writes nothing transient.

## Conventions to respect

- Skills are **verbs**, outputs are **nouns** (`validate-idea` → `idea-validation`).
- Orchestrators **conduct, never duplicate** — they invoke sub-skills via the Skill tool and spawn the
  named **agents** (`spec-reviewer`, `spec-researcher`, `implementer`, `verifier`, `ui-prototyper`,
  `refactorer`, `test-writer`).
- `_shared/` holds the methods (no `SKILL.md`): `spec-pipeline/`, `build-pipeline/`,
  `release-pipeline/` — elicitation, research, review, output format, backlog, quality gate,
  propagation, audit, severity, report — plus `build-pipeline/design-freeze.md` (visual decisions are
  settled once, never re-opened by a skill), `build-pipeline/report-format.md` (every run ends with
  «What you should do», timings that add up), `agent-guide.md` (the project-map block),
  `glossary.md`, `git-workflow.md`. Read them for the *how*; don't restate them in skills.
