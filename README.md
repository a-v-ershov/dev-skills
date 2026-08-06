# dev-skills

**English** · [Русский](README.ru.md)

dev-skills is a set of Claude Code skills and agents for building products.

The method is the point: every change rides a **build → verify → ship loop** where a separate agent proves the work before it advances. **[Jump to install ↓](#install)**

**Take a raw idea to a shipped release with dev-skills — one reviewed step at a time, so the AI
builds the *right* thing and proves it works instead of just saying so.**

Three gated pipelines — **spec → build → release** — installed as a plugin into any project from
GitHub. Every skill replies in the language you write to it.

---

## The 3 problems it fixes

1. **AI builds the wrong thing, fast** — it jumps from a one-line prompt straight to code, so you ship a polished version of an unvalidated idea and find out too late.
2. **AI grades its own homework** — the same agent writes the feature, declares *"it works,"* and writes tests that pass because it wrote them to pass.
3. **Quality and decisions vanish** — security holes, slow paths, and the reasoning behind choices never show up in a green unit test and are lost between sessions.

## What you get

1. **Three pipelines, one command each** — call `create-project-spec`, `build-tasks`, or `release-product` and one meta-skill conducts every phase for you; going live stays a separate, deliberate command.
2. **It interviews you before it builds** — a discovery grill pulls the maximum context out of your head, down to your stack and style preferences, one question at a time, always with a recommended answer.
3. **A separate agent always checks the work** — nothing self-certifies: a reviewer on every spec phase, plus a fresh verifier that writes adversarial tests and is hook-blocked from touching the code.
4. **A real dev loop + a release phase that hunts the AI's own bugs** — an enforced quality gate locally, then a refactor pass, a red-first test sweep, independent security / performance / product+accessibility audits, and a hands-on briefing for you, before you ship.
5. **Production in one deliberate step** — `setup-production-environment` sets up the platform, the database, the caps, and the telemetry, sorting every gap into *repo · authorized CLI with your yes · you in a dashboard*, then deploys, smoke-tests the live version, and leaves a plain-language runbook.

**Plus:** replies in your language · never touches your branches — every skill works on the branch you
are on (normally `main`) and branches only when you explicitly ask · reverse-engineers an existing
codebase into a spec (brownfield) · leaves committed project memory — docs, ADRs, backlog, a
`CLAUDE.md` map — that doesn't rot · ships as a plain Claude Code plugin, no extra runtime or MCP
server.

---

## How it works

Three pipelines, each a thin **orchestrator** that conducts focused sub-skills, plus a manually-invoked
production step; every sub-skill also runs on its own.

### 1 — Spec: idea → buildable spec

`create-project-spec` runs seven persona-driven phases; each researches the claims that would change
what you build (source-cited, on a fixed budget — the rest is labelled unverified), drafts, is
checked by an independent reviewer whose findings it applies, and emits a research doc + a short
human summary under `.dev-skills/project-spec/`.

| Step | Skill | Persona | Produces |
|------|-------|---------|----------|
| 1 | `gather-context` | Discovery interviewer | `project-brief` — interviews you until you share the same understanding |
| 2 | `validate-idea` | Founder-turned-investor | `idea-validation` — KILL / SHRINK / forcing questions |
| 3 | `define-product-requirements` | Product manager | `product-requirements` — the full feature set, each with testable criteria |
| 4 | `create-user-flows` | Product designer | `user-flows` — how users move through the product |
| 5 | `define-design-decisions` | Design-system lead | `design-decisions` — direction + which UI kit / icons / theming; the bridge to tech |
| 6 | `design-architecture` | Software architect | `architecture` + ADRs — quality scenarios first, then components + tech, where it runs, and how it's measured |
| 7 | `design-dev-architecture` | DX / platform engineer | `dev-architecture` + ADRs — the local inner loop and AI tooling |

> **Already have code?** No separate mode — every phase reads the repo at its intake, tells you what
> it found, and confirms instead of re-asking; what you want changed is recorded as a divergence and
> becomes work in the backlog.

### 2 — Build: spec → working software

`build-tasks` turns the spec into code sequentially — one task at a time, single working tree, no
parallelism — mutating the real repo.

| Step | Skill | Role |
|------|-------|------|
| 1 | `setup-dev-environment` | Scaffolds the repo, brings up the one-command stack, stands up the enforced quality gate (`make check-fast` · `make test-scoped` · `make check` + hooks), writes `DESIGN.md` for a UI project |
| 2 | `plan-development` | Emits a kanban backlog — one file per task, where `blocked_by` *is* the dependency graph. Coarse tasks: **at most 15 open**, a ceiling every task-filing skill shares |
| 3 | `run-task` | Runs **one** task end to end: implement → verify → one fix round → gate → you accept it → commit |
| — | `build-tasks` | Works through the plan: next ready task → `run-task` → repeat, up to 8 per run |

It picks the lowest-id ready task, builds it, verifies it in a separate agent, allows exactly one fix
round, then asks you to accept the work (or auto-accepts when there's nothing to check by hand) and
offers the spec edit that keeps the docs honest — all in one checkpoint commit. Anything the fix round
leaves open escalates to `needs_human`.

**The loop runs only the task's own tests** — the ones written for it plus the ones covering the files
it changed — never the whole suite; and tests are written at the cheapest level that proves the
criterion, so end-to-end is the exception rather than the default. The full suite runs at the release
boundary, where the question is actually "does all of this still work together?". `generate-mockups`
renders UI options on demand. A later spec edit needs no separate skill: re-run the phase (it amends),
then `plan-development` (it emits task deltas); a task that changed the product proposes its own spec
edit in the same commit.

### 3 — Release: working software → cut release

`release-product` cleans the tree, closes the test gaps, proves the cross-cutting properties no single
task could, and then ships. The first two steps change the repo, so they run **alone and in order**; the
audits are read-only, so they fan out in **parallel**. Nothing here fixes code in place, and **no audit
installs anything**.

| Step | Skill | Does / proves against |
|------|-------|------------------------|
| 1 | `refactor` | Structure without behaviour change — duplication, dead code, size, suppression debt; plan → your approval, small steps, green before and after |
| 2 | `write-tests` | The coverage map (nothing / happy-path-only / hollow, mutation-tested) and closes the risky gaps **red-first**; a real bug becomes a task and the test stays red |
| 3 | `audit-security` | the STRIDE-lite threat model — secrets, authz, injection, the lethal trifecta, row-level security, spend caps, production config |
| 4 | `audit-performance` | the quality-attribute scenarios — measured p95, throughput, N+1, cost |
| 5 | `audit-product` | the user flows end-to-end and cross-feature, **plus** the WCAG target on the same journeys |
| 6 | `manual-test` | The briefing for your hands-on pass — starting with everything accepted as `review: auto`, which no human has ever opened |
| — | `cut-release` | clean tree + no open 🔴 → docs, version, changelog, tag, commit, PR (always confirmed; **stops before production**) |

A blocker becomes a rework task, fixed by **one** `build-tasks` run, then **re-audited once to confirm
it closed**; anything still open is escalated to you rather than looped on.

### 4 — Production: cut release → live product

`setup-production-environment` is invoked **by hand** — no orchestrator ships anything for you. It reads
the architecture's deployment and analytics decisions and makes them real: platform and release channel,
the production database with its migrations and backups, configuration and secrets in the target
environment, **hard** spending caps, analytics events and error tracking, optional CI. Every gap is
sorted before anything happens — **① it fixes in the repo · ② it runs through an authorized provider
CLI, one explicit yes per action · ③ only you, in a dashboard** — and it finishes by deploying,
**opening the live version and walking the short path**, then writing a runbook that says which button
to press next time and how to roll back.

---

## How it compares

Most tools cover one slice of the arc; the dev-skills bet is the *full* arc plus a separate adversary
at every stage.

| Tool | What it is | Where dev-skills differs |
|------|-----------|------------------------------|
| **[GitHub Spec Kit](https://github.com/github/spec-kit)** | Spec → Plan → Tasks → Implement; templates, agent-agnostic | It stops at implement — no independent verification, no release audits, no built-in research or adversarial review. |
| **[BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)** | Agentic-agile framework, 12+ specialist agents | Plans and builds, but has no read-only release-audit phase, no harness-enforced verifier, no brownfield reverse-engineering. |
| **[Task Master](https://github.com/eyaltoledano/claude-task-master)** | PRD → task decomposition; an MCP project manager | Task management only — it doesn't validate, research, design, or audit; needs an MCP server running. |
| **[gstack](https://github.com/garrytan/gstack)** | 23 role skills for the per-PR sprint loop | Great on an existing codebase's review/ship loop, but has no idea→spec generator and no spec reconstruction. *(Our design reference.)* |
| **[SuperClaude](https://github.com/SuperClaude-Org/SuperClaude_Framework)** | ~30 commands + persona agents injected into `CLAUDE.md` | An à-la-carte command toolbox, not a sequenced, gated pipeline with research, review, and a writer/reviewer split baked in. |

---

## Install

In any project, inside Claude Code:

```
/plugin marketplace add https://github.com/a-v-ershov/dev-skills.git
/plugin install dev-skills@dev-skills
```

Skills appear namespaced as `dev-skills:<skill>`. Start a project with
**`/dev-skills:create-project-spec`** and answer the three setup questions — or run any single
skill on its own.

## Update

An install only picks up changes once the plugin's `version` is **bumped**. To update a project that
has it installed (a restart applies the update):

```
/plugin marketplace update dev-skills
/plugin update dev-skills@dev-skills
```

Or turn on auto-update once: `/plugin` → **Marketplaces** → `dev-skills` → **Enable auto-update**.

---

## Skill reference

All 25 skills, grouped by pipeline. Orchestrators are listed first in each group; every sub-skill
also runs on its own.

### Spec — idea → buildable spec

| Skill | Role | What it does | Writes |
|-------|------|--------------|--------|
| `create-project-spec` | Orchestrator | Sequences the seven spec phases from raw idea to buildable spec | the spec |
| `gather-context` | Discovery interviewer | Interviews you to turn a short brief into shared understanding | `project-brief.research.md` |
| `validate-idea` | Founder-investor | Pressure-tests demand, audience, problem, and business model | `idea-validation.research.md` |
| `define-product-requirements` | Product manager | Defines who it's for and the full committed feature set + criteria | `product-requirements.research.md` |
| `create-user-flows` | Product designer | Maps how users move through the product to get value | `user-flows.research.md` |
| `define-design-decisions` | Design-system lead | Sets the design direction — system + UI kit, key screens, platforms, a11y | `design-decisions.research.md` |
| `design-architecture` | Software architect | Quality scenarios first, then components + tech, hosting & cost, analytics | `architecture.research.md` + `adr/` |
| `design-dev-architecture` | DX / platform engineer | Designs the local inner loop, AI-drivable testing, and AI tooling | `dev-architecture.research.md` + `adr/` |

### Build — spec → working software

| Skill | Role | What it does | Writes |
|-------|------|--------------|--------|
| `build-tasks` | Orchestrator | Picks one ready task at a time and hands it to `run-task` | the build run |
| `run-task` | One-task cycle | implement → verify → one fix round → gate → acceptance → commit | a finished task |
| `setup-dev-environment` | Platform engineer | Scaffolds the repo, brings up the stack, stands up the quality gate | repo + `.dev-skills/project-setup/` |
| `plan-development` | Delivery tech lead | Turns the spec into a kanban backlog, one file per task | `.dev-skills/build-plan/` |
| `implement-feature` | Implementer | Builds one backlog task into code and gets the static gate + the task's own tests green | code |
| `verify-feature` | Independent verifier | Authors adversarial tests at the cheapest level that proves each criterion, and proves a built task's observable outcomes | tests + verdict |
| `generate-mockups` | UI prototyper | *(on demand)* Renders stub UI variants against `DESIGN.md` to compare | throwaway mockups |

### Release — working software → cut release


| Skill | Role | What it does | Writes |
|-------|------|--------------|--------|
| `release-product` | Release captain | Runs the chain, files rework, drives one fix round, re-audits once, then cuts | the release chain |
| `audit-security` | Security engineer | Proves the STRIDE-lite threat model on the running system | `security-audit.md` |
| `audit-performance` | Performance engineer | Measures the system against the quality-attribute scenarios | `performance-audit.md` |
| `audit-product` | QA lead | Drives the user flows end-to-end across features, and the same journeys keyboard-only against the WCAG target | `qa-report.md` |
| `refactor` | Staff engineer | Cleans structure without changing behaviour; measures rot, dead code, suppression debt | `refactor.md` |
| `write-tests` | Test engineer | Maps coverage gaps and closes them red-first; a real bug is filed, never patched | tests + `test-gaps.md` |
| `manual-test` | Test lead | *(read-only)* Briefs you on what only a person can judge | `manual-test-brief.md` |
| `cut-release` | Release engineer | Bumps version, changelog, tag, commit, PR — gated, stops before production | release docs + PR |

### Production — cut release → live product

| Skill | Role | What it does | Writes |
|-------|------|--------------|--------|
| `setup-production-environment` | Platform engineer | *(by hand)* Sets up the platform, database, config, caps, and telemetry in three groups, deploys, and smoke-tests the live version | `production-setup.md` + `production-runbook.md` |

### Cross-cutting — used across the pipelines

| Skill | Role | What it does | Writes |
|-------|------|--------------|--------|
| `commit` | Git helper | Splits session changes into well-structured commits (English messages) | commits |
| `audit-skills` | Skill auditor | *(by hand)* Audits how the skills and agents that ran in this session actually behaved — wrong or skipped steps, repeated work, broken invariants, artifacts that miss their template — and proposes numbered edits to their files; applies nothing until you pick numbers | proposals (edits to skill files on your pick) |

Each `*.research.md` ships with a paired `*.summary.md`; spec docs live under `.dev-skills/project-spec/`,
the release phase's findings under `.dev-skills/release/`, setup records under
`.dev-skills/project-setup/`. *(existing)* = brownfield projects only, *(UI)* = UI projects (self-skips
otherwise), *(on demand)* = not auto-run in a pipeline, *(by hand)* = never auto-run at all.
`gather-context` is also reusable on demand as a scoped grill.
