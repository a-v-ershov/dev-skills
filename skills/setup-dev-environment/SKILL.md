---
name: setup-dev-environment
description: "Turn the dev-architecture spec into a real, runnable local environment. Use after the project-spec pipeline (reads .dev-skills/project-spec/dev-architecture.research.md and architecture.research.md + adr/*), as the first step of the build/development phase, to scaffold the repo and bring up the inner loop: install tooling, init the repo (.gitignore, project CLAUDE.md, settings.json), write the Docker Compose stack + seed data + one-command bring-up, wire the AI tooling (MCP servers, plugins), and scaffold skeleton stubs of the developer/test scripts and the custom project skills (.claude/skills/) the dev-architecture specified. For a UI project it also installs the UI kit and icon set the spec chose and writes the committed root DESIGN.md (tokens + rationale) straight from the spec's design decisions and the installed kit's own theme — no candidate systems, no mockups, no picking: the design decisions were made in the spec. Runs an internal plan → approve → execute: it plans everything but auto-executes only repo-local scaffolding; global installs, API keys, and Claude plugins run only with explicit confirmation. Idempotent (safe to re-run), detect-state-first. In a repo that already has a working setup it adopts and extends what's there (compose, Makefile, existing lint/type tools wired behind make check) and fills only the gaps, never re-scaffolding. Ends with a smoke-test that proves the stack actually comes up, and writes .dev-skills/project-setup/verification.md (the concrete run/drive/prove commands the verify-feature skill later reads) plus a setup-log. The first build-phase skill; run before plan-development and build-tasks."
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
  `make check-fast` target (static checks) and a `make check` target (static + the suite), and a
  **pre-commit hook that runs the static gate** and blocks the commit on red. **No test step in that
  hook, and no Claude Code Stop / PostToolUse hook that runs a gate when a turn or an edit ends** —
  both are ruled out in **`../_shared/build-pipeline/quality-gate.md`**, which defines the gate once;
  it executes the test levels `design-dev-architecture` already specified and does not re-pick tools.
- **Environment access + developer scripts + custom-skill skeletons** (repo-local): whichever
  env-access mechanism `dev-architecture` chose — the **advisory-lock helper** baked into the
  bring-up/teardown commands (lock file gitignored) and/or the **per-run isolation** params — plus the
  **skeleton/stubs of the developer & test scripts** it specified (fast, intentionally-divergent local
  paths; full implementation is left to backlog tasks), and the **skeleton `.claude/skills/<name>/
  SKILL.md` stubs** of the **custom project skills** it specified (the named verification-loop wrappers
  — frontmatter `name` + discoverable `description` and a thin body invoking the wrapped script, with
  the procedure left as a TODO; full authoring is a backlog task). See
  **`../_shared/build-pipeline/env-access.md`**.
- **The design system** (UI projects only) — the spec already decided it, so here you just make it
  real, in this order:
  1. **Install** the UI kit and icon set `design-decisions` named, per the kit's **current official
     instructions** (check them — install commands go stale; don't run them from memory).
  2. **Write the committed root `DESIGN.md`** — tokens + rationale, straight from the spec's design
     direction and the installed kit's own theme values. **No candidates, no mockups, no picking:**
     the choice was made in the spec. Format: `references/design-md-format.md`; per-kit token mapping:
     `references/adoption-recipes.md`. Plus the short `.dev-skills/project-setup/design-system.md` record.
  3. **Write the UI rule into the project `CLAUDE.md`** — components come from the kit, colors and
     spacing come from the design tokens, icons come from the one chosen set. Without that rule the
     next session's agent hand-rolls its own button.
  Skipped entirely for a no-UI project or when `design-decisions` says no system is needed.
- **The quality tooling the release phase will need** (repo-local dev dependencies, wired behind the
  project's own commands): whatever `dev-architecture` named for measuring the codebase and the suite —
  a duplication/dead-code analyzer, a mutation-testing runner, an accessibility checker, a load tool.
  Install them **here**, because the release phase deliberately cannot: `refactor`, `write-tests`, and
  every `audit-*` are forbidden from installing anything, and record a missing tool as *unmeasured*
  instead. A tool nobody installed is a measurement nobody takes.
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

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Git workflow

**One branch — the current one, normally `main`.** Never create a branch, never switch to another
branch, and never open a worktree on your own initiative. **The single exception:** the user
explicitly asked for a separate branch in this session — then use the name they gave (or propose one
and confirm it) and say plainly which branch the work is on. A request to commit, to fix, or to ship
is not a request to branch. Full rule: **`../_shared/git-workflow.md`**.

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
- **The gate is enforced, not advisory.** Stand up the quality gate so a red **static** gate blocks
  the commit (pre-commit hook), and the full gate — the one with the suite — is what
  `implement-feature`, `verify-feature` and `build-tasks` run deliberately. No turn-end hook. See
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
- [ ] Stage 5b: Design system (UI only) — write root DESIGN.md straight from the spec's design decisions + the installed kit's theme; render one screen to prove it; design-system.md (skip for no-UI / no system)
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
  zero-tolerance, a `make check-fast` and a `make check` target, a pre-commit hook that runs the
  **static** one and blocks the commit on red —
  **`../_shared/build-pipeline/quality-gate.md`**), the **env-access helper** (lock baked into
  bring-up + gitignored lock file, and/or per-run isolation params —
  **`../_shared/build-pipeline/env-access.md`**), the **skeleton of the developer/test scripts**
  `dev-architecture` specified, and the **skeleton `.claude/skills/<name>/SKILL.md` stubs** of the
  **custom project skills** it specified (frontmatter + thin body invoking the wrapped script; the
  procedure left as a TODO — full authoring is a backlog task; skeleton template in
  `references/setup-templates.md` §6). *Auto-applicable (repo-local).*
- **(C) AI tooling** — `.claude/settings.json` (**a `permissions.deny` list** excluding
  generated/build/vendor trees from navigation — and **no gate-running Stop / PostToolUse hook**, see
  the gate doc), the **code-intelligence LSP plugin(s)** for the stack's typed language(s)
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
deliberately-introduced **type or lint** error makes `make check-fast` fail and the pre-commit hook
block the commit (then revert the error). Use a static error, not a failing test — the hook does not
run tests, so a broken test would prove nothing about it. "No error in the logs" is not proof. If it fails, report what failed and offer to fix it
(adjust the compose file, fix a port clash, re-seed) — the environment is not "done" until this is green.

### Stage 5b: Design system → `DESIGN.md` (UI projects only)
Now that the stack is up and the kit is installed, write the design system down. Read
`.dev-skills/project-spec/design-decisions.research.md`: if this is a no-UI project or it recorded **Design
system / Needed? = no**, **skip** this stage (note it in the setup log) and go to Stage 6. If a root
`DESIGN.md` already exists, leave it alone and note that (idempotent).

Otherwise **write the root `DESIGN.md` directly from the spec** — no candidates, no mockups, no
picking. The design decisions are already made: `define-design-decisions` chose the UI kit, the icon
set, the theming approach, and the type/color/spacing/motion intent; this stage only makes them
concrete and machine-readable.

- **Source of the tokens:** the theming approach from the spec. "Start from the kit's ready-made
  theme" → read that theme's actual token values from the installed kit (its theme file / CSS
  variables / config in the repo — the kit is installed now, so read the real values rather than
  recalling them) and record them. "Author from brand intent" → derive a coherent token set from the
  design direction + the product's audience and brand notes.
- **Format:** the Google open format — YAML token front matter + prose rationale, canonical section
  order: **`references/design-md-format.md`**. Per-kit token mapping (which of the kit's variables
  becomes which token): **`references/adoption-recipes.md`**.
- **Also record** the icon set, the installed kit and its version, and how tokens are wired into the
  stack (Tailwind `theme.extend`, CSS custom properties, a `components.json`, a Material theme file)
  so `implement-feature` uses tokens rather than literals.
- **Then prove it renders.** Apply the tokens to one real screen or the scaffold's start page, take
  a screenshot, and put it in the setup log — a `DESIGN.md` nobody has rendered is paper. If the
  tokens don't actually take effect, fix the wiring before moving on.
- Write the short record `.dev-skills/project-setup/design-system.md`: which kit + icon set, where the
  tokens came from, how they're wired, the screenshot path.

Deviating from the spec's design decisions here is **out of scope** — if the kit turns out to be
wrong (a needed component genuinely doesn't exist), stop and say so: that is a spec change
(`/define-design-decisions`, then `/plan-development` to reconcile the plan), not a call to make during setup.

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

## When the repo already has a working setup

Nothing special is configured for this — it is this skill's **detect-state-first idempotency doing
its job**. Three specifics:

1. **Probe, then plan the difference.** Stage 1 already inventories what's present (compose file,
   Makefile, CI config, lint/type tools, `.env.example`, existing run command). The Stage-2 plan is
   **(what the dev-architecture inner loop needs) minus (what's already there)** — and read the CI
   config, not just the local files: it often defines the real gate.
2. **Fill gaps, adopt & extend — never overwrite.** An existing `Dockerfile` / compose / `Makefile` is
   adopted and extended (back up before any edit), never blown away. The **quality gate** wires the
   *existing* lint/format/type-check tools behind one `make check` + the hooks rather than installing
   new ones (the gate "executes the chosen tools, it doesn't re-pick" — here they're the ones already
   in the repo). Env-access helper, dev-script skeletons, and custom-skill skeletons are scaffolded
   only where absent; an existing `.claude/skills/` skill named by the dev-architecture is extended,
   not overwritten. `verification.md` is still written **fresh** from the now-real stack.
   For a UI project with a kit already installed, keep it and write `DESIGN.md` from its actual theme
   values — replacing an installed kit is a spec decision, not a setup one.
3. **The smoke-test includes the existing gate's honesty.** "Green" means the stack comes up via the
   one command **and** the gate has teeth — which may mean fixing a gate the repo had red (tests exist;
   do they pass?). A red pre-existing gate is **surfaced**, not silently accepted: report it and offer
   to fix, or file it as a gap for `plan-development`.


## Rules

1. Never run a machine-global install, write a secret, or install a plugin/MCP server without explicit
   confirmation — in either mode. Repo-local scaffolding may auto-apply.
2. Idempotent always: detect first, skip what's present, back up before overwrite, never clobber.
3. Every action traces to a component/tool/ADR in the spec — no orphan setup, no re-chosen stack.
4. The environment is "done" only when the one-command bring-up is smoke-tested green and drivable.
5. Surface the irreducible manual steps honestly in setup-log.md; never pretend they're handled.
6. Always write `verification.md` — the build phase depends on it; an environment without it is unfinished.
7. **Install the quality tooling the release phase cannot install itself** (analyzer, mutation runner,
   accessibility checker, load tool — whatever the dev-architecture named). Production-side setup —
   platform, database, caps, telemetry — is **not** yours: that is `setup-production-environment`.
8. Stand up the **enforced quality gate** — a red `make check-fast` blocks the commit (pre-commit
   hook); the suite lives in `make check`, which the pipeline runs deliberately. **No test step in the
   hook and no turn-end hook.** The gate executes the spec's test levels; it doesn't re-pick tools.
9. Bake the **env-access mechanism** into the bring-up command (lock with lease + stale-reclaim, and/or
   per-run isolation; gitignore the lock file) and scaffold the **developer/test-script skeletons** and
   the **custom project-skill skeletons** (`.claude/skills/<name>/SKILL.md`) the dev-architecture named —
   full implementation is backlog work.
