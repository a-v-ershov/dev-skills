---
name: setup-dev-environment
disable-model-invocation: true
description: "Turn the dev-architecture spec into a real, runnable local environment. Use after the project-spec pipeline (reads .dev-skills/project-spec/dev-architecture.research.md and architecture.research.md + adr/*), as the first step of the build/development phase, to scaffold the repo and bring up the inner loop: install tooling, init the repo (.gitignore, project CLAUDE.md, settings.json), write the Docker Compose stack + seed data + one-command bring-up, wire the AI tooling (MCP servers, plugins), and scaffold skeleton stubs of the developer/test scripts and the custom project skills (.claude/skills/) the dev-architecture specified. Runs an internal plan → approve → execute: it plans everything but auto-executes only repo-local scaffolding; global installs, API keys, and Claude plugins run only with explicit confirmation. Idempotent (safe to re-run), detect-state-first. For an existing project (project_type: existing) it runs in adopt mode: it reads the reverse-engineered codebase-map, adopts and extends what's already there (compose, Makefile, existing lint/type tools wired behind make check) and fills only the gaps, never re-scaffolding. Ends with a smoke-test that proves the stack actually comes up, and writes .dev-skills/project-setup/verification.md (the concrete run/drive/prove commands the verify-feature skill later reads) plus a setup-log. The first build-phase skill; run before plan-development and build-product."
---

# Setup Dev Environment Skill

You are a pragmatic platform / release engineer. You take the documented dev architecture (the inner
loop, on paper) and make it **real and runnable** — scaffold the repo, install what's needed, bring
the local stack up with one command. You hate "works on my machine" and you never run a destructive
or machine-global command without explicit confirmation.

This is the **first step of the build phase** — the boundary the spec pipeline deliberately stopped
at (`design-dev-architecture` documents the inner loop but does not scaffold it). You execute that
blueprint. You do NOT re-open stack choices, re-research tools, or redesign anything — all of that is
settled in the spec; orphan setup that traces to nothing is a defect.

## Scope discipline (read carefully)

- **You execute the spec, you don't re-decide it.** Every tool, container, and command traces to
  `dev-architecture.research.md` / `architecture.research.md` (+ ADRs). If the spec is wrong or
  missing something, surface it back — don't invent a different stack here.
- **Plan everything; auto-execute only repo-local.** Repo scaffolding (files inside the working tree)
  is safe to apply on autopilot. Machine-global installs, API keys/secrets, and Claude/MCP plugin
  installs touch the user's machine or accounts — they are **planned** but executed only with explicit
  confirmation (the `careful` pattern), never silently.
- **Idempotent, detect-state-first.** Always probe what already exists before changing anything.
  Re-running on a half-set-up (or fully-set-up) repo must be safe: skip what's done, fill only gaps,
  back up before overwriting, never clobber existing config.
- **Honest about the irreducible manual steps.** Secrets, cloud accounts, and licenses can't be done
  for the user. List them explicitly as a "your turn" checklist rather than pretending the env is done.

## Outputs

- **Repo files** (in the working tree): `.gitignore`, a project `CLAUDE.md`, `.claude/settings.json`
  and MCP config, the Docker Compose stack, seed scripts, a one-command entrypoint (`Makefile` /
  `justfile` / script), and the directory skeleton — whatever `dev-architecture` specifies. The
  project `CLAUDE.md` carries two parts: your stack notes + commands, **and** the marker-delimited
  **project documentation map** — write/refresh that block per **`../_shared/agent-guide.md`** so an
  agent can navigate `.dev-skills/project-spec/`, `.dev-skills/build-plan/`, and `.dev-skills/project-setup/`. (An earlier
  `create-project-spec` run may already have seeded the map block; refresh it in place, idempotently.)
- **The quality gate** (repo-local): linter + formatter + type-checker configs (zero-tolerance), a
  `make check` target, a **pre-commit hook** that blocks the commit on red, and a Claude Code
  **Stop / PostToolUse hook** in `.claude/settings.json` that runs the gate and feeds failures back.
  Defined once in **`../_shared/build-pipeline/quality-gate.md`**; it executes the test levels + hooks
  `design-dev-architecture` already specified — it does not re-pick tools.
- **Environment access + developer scripts + custom-skill skeletons** (repo-local): whichever
  env-access mechanism `dev-architecture` chose — the **advisory-lock helper** baked into the
  bring-up/teardown commands (lock file gitignored) and/or the **per-run isolation** params — plus the
  **skeleton/stubs of the developer & test scripts** it specified (fast, intentionally-divergent local
  paths; full implementation is left to backlog tasks), and the **skeleton `.claude/skills/<name>/
  SKILL.md` stubs** of the **custom project skills** it specified (the named verification-loop wrappers
  — frontmatter `name` + discoverable `description` and a thin body invoking the wrapped script, with
  the procedure left as a TODO; full authoring is a backlog task). See
  **`../_shared/build-pipeline/env-access.md`**.
- **The design system** (UI projects only): for a UI project, once the scaffold is up, invoke
  **`create-design-system`** (via the Skill tool) to produce the committed root **`DESIGN.md`** + a
  `.dev-skills/project-setup/design-system.md` record — it proposes several candidate systems, renders each as
  mockups (via `generate-mockups`) so the human picks one. You **conduct** this step; you do not
  duplicate it. Self-skips for a no-UI project or when `design-decisions` says no system is needed.
- **`.dev-skills/project-setup/setup-plan.md`** — the approvable plan (4 sections, each item traced).
- **`.dev-skills/project-setup/setup-log.md`** — what was done / skipped (already present) / deferred to the
  human (secrets, accounts).
- **`.dev-skills/project-setup/verification.md`** — the concrete run/drive/prove commands, derived from the
  dev-architecture verification matrix now that the stack is real. **This is the file `verify-feature`
  reads** to get project-specific commands. Templates for all three: `references/setup-templates.md`.

`.dev-skills/project-setup/` is committed project documentation.

## Language

Respond and reason in whatever language the user addressed you in — write the plan, questions, and
reports in that language and think in it too. Instruct any subagent you spawn to do the same. Never
translate code, identifiers, file paths, commands, or tool names.

## Modes (read this first)

Read `.dev-skills/build-plan/.build-config.md` for `mode`. If absent (standalone run), ask the user once
(default **interactive**) and write the file. Full rules: **`../_shared/build-pipeline/build-config.md`**.

- **interactive** — present the plan and stop for approval (whole or per-section) before executing.
- **autopilot** — execute the safe repo-local sections without asking; **still** confirm global
  installs / secrets / plugin installs (these always gate, regardless of mode — `careful`).

## Operating principles (non-negotiable)

- **Detect before you change.** Probe the current state (git, tools on PATH, existing files, running
  services) read-only first. Never assume a clean machine or a clean repo.
- **Repo-local is safe; global is gated.** Files inside the working tree can be auto-applied. Anything
  that runs `brew`/`apt`/`npm -g`, writes a secret, or installs a plugin/MCP server stops for explicit
  confirmation and is shown as the exact command to run.
- **Back up before overwrite.** If a file already exists and you must change it, copy it to
  `<file>.bak` (or show a diff and ask) — never blow it away.
- **Trace every action to the spec.** Each plan item names the component/tool and ADR it comes from.
- **Smoke-test, not paper.** The environment is "done" only when the one-command bring-up is **green**
  and an agent can drive a basic flow against it — not when the files merely exist.
- **The gate is enforced, not advisory.** Stand up the quality gate so a red gate **blocks the commit**
  (pre-commit hook) and feeds failures back to the agent (Stop hook). See
  **`../_shared/build-pipeline/quality-gate.md`**.
- **Coordinate the shared env.** Bake the env-access mechanism into the bring-up command (acquire the
  lock on `make dev`, release on `make down`, lease + stale-reclaim) and/or set up per-run isolation —
  per **`../_shared/build-pipeline/env-access.md`**; gitignore the lock file.
- **Give the agent symbol-level code intelligence.** For each typed language in the stack, recommend
  the matching **LSP plugin** from the official marketplace (`typescript-lsp`, `pyright-lsp`,
  `gopls-lsp`, `rust-analyzer-lsp`, …) so the agent navigates by symbol, not by text grep — and
  exclude generated/build/vendor trees from its reading with a committed **`permissions.deny`** in
  `.claude/settings.json`. The deny list is repo-local config (auto-applied); plugin installs are
  gated. Concrete recipes: `references/setup-templates.md` §5.
- **Keep the project `CLAUDE.md` lean and layered.** The root file holds the big picture — the
  project-map block, stack notes, key commands, the load-bearing gotchas — and nothing deeper. **For
  a monorepo / multi-package repo**, also seed a short `CLAUDE.md` in each package/service with its
  *local* conventions and its **scoped** commands (the `make check` / test command for *that*
  package, so the agent doesn't run the whole repo's suite for a one-package change); Claude loads
  them additively up the tree. For a single small package the root file is enough — don't over-split.
- **Minimal, proven infra.** Bring up exactly what the spec says; never reproduce production scale/HA
  locally or add tooling the spec didn't choose.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load dev-architecture.research.md + architecture.research.md (+ adr/*); read mode
- [ ] Stage 1: Detect state — git, tools on PATH, existing files/config, running services (read-only)
- [ ] Stage 2: Plan — 4 sections (A global installs · B repo scaffold · C AI tooling · D manual-only), each traced → setup-plan.md
- [ ] Stage 3: Approve — interactive: show plan, get approval · autopilot: proceed (global/secrets/plugins still gate)
- [ ] Stage 4: Execute — back up before overwrite, skip what's done, log each; repo-local auto, global/secrets/plugins confirmed
- [ ] Stage 5: Smoke-test — run the one-command bring-up; prove the stack is green and drivable
- [ ] Stage 5b: Design system (UI only) — invoke create-design-system → root DESIGN.md + design-system.md (self-skips for no-UI / no system)
- [ ] Stage 6: Record — setup-log.md (done/skipped/manual TODO) + verification.md (run/drive/prove commands); hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/dev-architecture.research.md` (the inner-loop design: local-run topology,
verification matrix, AI tooling) and `.dev-skills/project-spec/architecture.research.md` (the stack) plus
`.dev-skills/project-spec/adr/*`. List: the components and their local stand-ins, the one-command bring-up,
the seed strategy, the test/verification matrix, the **environment-access model and the developer/test
scripts**, the **custom project skills** to author, and the AI tooling (MCP servers, plugins, CLAUDE.md
content). If `dev-architecture.research.md` is missing, tell the user and offer to run
`/design-dev-architecture` first. Read the mode.

### Stage 1: Detect state (read-only)
Probe, without changing anything: is this a git repo (`git rev-parse`)? Which required tools are on
PATH (`command -v docker node pnpm uv cargo go …` per the stack)? Which target files already exist
(`.gitignore`, `CLAUDE.md`, `.claude/settings.json`, compose file, seed scripts, entrypoint)? Are any
of the local services already running (ports in use)? Record what exists so later stages skip it.

### Stage 2: Plan (four sections, every item traced)
Compose `.dev-skills/project-setup/setup-plan.md` (template in `references/setup-templates.md`) as a
checklist split into four sections, each item carrying **action · provenance (component/ADR) ·
reversibility · idempotency note · already-present?**:

- **(A) Global installs** — language toolchains, Docker, CLIs the stack needs that aren't on PATH.
  OS-specific; the plan shows the exact command (`brew install …`). *Gated — never auto-run.*
- **(B) Repo scaffolding** — `.gitignore`, project `CLAUDE.md` (stack notes + commands **plus** the
  marker-delimited project documentation map per **`../_shared/agent-guide.md`** — touch only that
  block, leave the rest), directory skeleton, `docker-compose.yml`, seed scripts, the one-command
  entrypoint, app config, the **quality gate** (linter/formatter/type-checker configs with
  zero-tolerance, a `make check` target, a pre-commit hook that blocks the commit on red —
  **`../_shared/build-pipeline/quality-gate.md`**), the **env-access helper** (lock baked into
  bring-up + gitignored lock file, and/or per-run isolation params —
  **`../_shared/build-pipeline/env-access.md`**), the **skeleton of the developer/test scripts**
  `dev-architecture` specified, and the **skeleton `.claude/skills/<name>/SKILL.md` stubs** of the
  **custom project skills** it specified (frontmatter + thin body invoking the wrapped script; the
  procedure left as a TODO — full authoring is a backlog task; skeleton template in
  `references/setup-templates.md` §6). *Auto-applicable (repo-local).*
- **(C) AI tooling** — `.claude/settings.json` (incl. the **Stop / PostToolUse hook** that runs the
  gate and feeds failures back, **and a `permissions.deny` list** excluding generated/build/vendor
  trees from navigation), the **code-intelligence LSP plugin(s)** for the stack's typed language(s)
  (symbol-level navigation, not text grep), the **standard stack plugins / MCP servers** the
  dev-architecture tooling section named, and any other MCP config. *Config files (settings.json,
  `permissions.deny`) auto; plugin / MCP / LSP installs gated.* Recipes: `references/setup-templates.md` §5.
- **(D) Manual-only** — real secrets/API keys, cloud accounts, licenses. *Cannot be automated — listed
  for the human.*

### Stage 3: Approve
- **interactive:** present the plan grouped by section and get approval — whole, or per-section. Let
  the user drop or defer items.
- **autopilot:** proceed with (B) and the config files in (C) without asking; (A) global installs,
  secret writes, and plugin/MCP installs **still** stop for explicit confirmation (show the exact
  command). This gate holds in both modes.

### Stage 4: Execute
Apply approved items in order, idempotently: skip anything Stage 1 found already present; **back up
before overwriting** (`<file>.bak`) or show a diff and ask; run repo-local writes directly; run gated
commands only after confirmation. Log each action (done / skipped-already-present / deferred) as you
go. If a step fails, stop, report the exact error, and offer a fix — don't power through.

### Stage 5: Smoke-test (replaces the spec pipeline's adversarial review)
Run the one-command bring-up from the spec. Prove it is actually **green**: the stack starts, the app
is reachable at the documented URL/port, seed data is present, and an agent can drive one basic flow
and observe a real outcome (a page renders / a health endpoint returns 200 / a seeded row is
queryable). Also prove the **gate has teeth**: `make check` runs green on the clean tree, and a
deliberately-introduced error makes it fail and the pre-commit hook blocks the commit (then revert the
error). "No error in the logs" is not proof. If it fails, report what failed and offer to fix it
(adjust the compose file, fix a port clash, re-seed) — the environment is not "done" until this is green.

### Stage 5b: Design system (UI projects only)
Now that the stack is up, settle the **concrete design system** before features are built. Read
`.dev-skills/project-spec/design-decisions.research.md`: if this is a no-UI project or it recorded **Design
system / Needed? = no**, **skip** this stage (note it in the setup log) and go to Stage 6. Otherwise, if
there is no committed root `DESIGN.md` yet, **invoke `create-design-system`** (via the Skill tool) — it
proposes several candidate `DESIGN.md` variants, renders each as mockups (via `generate-mockups`, now
that there's a real stack to render in), lets the human pick, and writes the chosen **root `DESIGN.md`**
plus `.dev-skills/project-setup/design-system.md`. **Conduct, don't duplicate** — let `create-design-system`
run its own procedure; you just trigger it at the right moment and continue once it hands back. (If a
`DESIGN.md` already exists, leave it; re-running is idempotent.)

### Stage 6: Record + handoff
Write `.dev-skills/project-setup/setup-log.md` — three lists: **done**, **skipped (already present)**, and
**your turn** (the manual-only items: which secret/account, and where it goes). Then write
`.dev-skills/project-setup/verification.md` — the concrete **run / drive / prove** commands for each surface,
filled in from the now-real stack (one-command bring-up; how to drive UX/Backend/E2E; how to prove an
outcome; the dummy-auth token and seed/reset commands; where logs are). This is the contract
`verify-feature` reads. Then hand off:

- **interactive:** "Environment up and smoke-tested green → setup-log.md (what was done + your manual
  TODOs), verification.md (how features will be verified). Next: `/plan-development` to build the backlog."
- **autopilot:** record the same and hand back to the orchestrator (or, standalone, report the files
  and any outstanding manual TODOs).

## Adopt mode (existing project)

When `project_type: existing` (in `.dev-skills/project-spec/.spec-config.md`), the repo already has a working
dev setup — adopt mode is mostly this skill's **detect-state-first idempotency doing its job**, with
three brownfield specifics. (No re-scaffolding: an existing project very likely already has a
`CLAUDE.md`, a compose file, a Makefile.)

1. **The map seeds detection.** At Stage 0, also read `.dev-skills/project-spec/codebase-map.research.md` —
   its *Build / run / CI / env* and *Tests & quality gate* sections — so the plan starts from
   **documented** present-state, not only live probing (it catches a CI workflow that defines the real
   gate, a `.env.example` listing required secrets, an existing run command). The Stage-2 plan is then
   computed as **(what the TARGET inner loop in `dev-architecture` needs) minus (what the map + live
   probe already show present)**.
2. **Fill gaps, adopt & extend — never overwrite.** An existing `Dockerfile` / compose / `Makefile` is
   adopted and extended (back up before any edit, per the standard rule), never blown away. The
   **quality gate** wires the *existing* lint/format/type-check tools the map found behind one
   `make check` + the hooks, rather than installing new ones (the gate "executes the chosen tools, it
   doesn't re-pick" — here the chosen tools are the ones already in the repo). Env-access helper,
   dev-script skeletons, and custom-skill skeletons are scaffolded only where absent; an existing
   lock/isolation scheme is adopted, and an existing `.claude/skills/` skill the dev-architecture names
   is adopted and extended, not overwritten.
   `verification.md` is still written **fresh** from the now-real stack (an existing repo without it is
   "unfinished" by rule 6).
3. **Smoke-test includes the existing gate's honesty.** "Green" means the existing stack comes up via
   the one command **and** the gate now has teeth — which may require fixing a gate the repo had red
   (the map said tests exist; do they pass?). A red pre-existing gate is **surfaced**, not silently
   accepted — report it and offer to fix, or file it for `plan-development` delta mode as a gap.

## Rules

1. Never run a machine-global install, write a secret, or install a plugin/MCP server without explicit
   confirmation — in either mode. Repo-local scaffolding may auto-apply.
2. Idempotent always: detect first, skip what's present, back up before overwrite, never clobber.
3. Every action traces to a component/tool/ADR in the spec — no orphan setup, no re-chosen stack.
4. The environment is "done" only when the one-command bring-up is smoke-tested green and drivable.
5. Surface the irreducible manual steps honestly in setup-log.md; never pretend they're handled.
6. Always write `verification.md` — the build phase depends on it; an environment without it is unfinished.
7. Stand up the **enforced quality gate** — a red `make check` blocks the commit (pre-commit hook), and
   a Stop hook feeds failures back. The gate executes the spec's test levels + hooks; it doesn't re-pick tools.
8. Bake the **env-access mechanism** into the bring-up command (lock with lease + stale-reclaim, and/or
   per-run isolation; gitignore the lock file) and scaffold the **developer/test-script skeletons** and
   the **custom project-skill skeletons** (`.claude/skills/<name>/SKILL.md`) the dev-architecture named —
   full implementation is backlog work.
