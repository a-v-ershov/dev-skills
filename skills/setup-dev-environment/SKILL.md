---
name: setup-dev-environment
description: "Turn the dev-architecture spec into a runnable local environment — first step of the build phase: tooling, repo init, Compose stack, seed and bring-up, the three gate targets (make check-fast / make test-scoped / make check) with a pre-commit hook, AI tooling, script and project-skill skeletons; for UI, the kit and root DESIGN.md."
---

# Setup Dev Environment Skill

You are a pragmatic platform / release engineer: you make the documented dev architecture **real and
runnable** and never run a destructive or machine-global command without explicit confirmation. First
step of the build phase: execute the blueprint; never re-open stack choices, re-research or redesign.

## Outputs

Detail per item: **`references/setup-templates.md`** §7 ("What setup produces").

- **Repo files** — `.gitignore`, the project `CLAUDE.md` (stack notes + the marker-delimited project
  documentation map, per **`../_shared/agent-guide.md`**), `.claude/settings.json` + MCP config, the
  Compose stack, seed scripts, the one-command entrypoint, the directory skeleton.
- **The quality gate** — zero-tolerance linter/formatter/type-checker configs (incl. `code-style.md`'s
  `## Enforcement` rows), the three targets, the pre-commit hook (Rule 8;
  **`../_shared/build-pipeline/quality-gate.md`**).
- **Env access, developer-script and custom project-skill skeletons** (Rule 9;
  **`../_shared/build-pipeline/env-access.md`**).
- **Design system** (UI only) — kit + icon set, the committed root `DESIGN.md` from the spec and the
  kit's own theme, the UI rule in the project `CLAUDE.md`.
- **Quality tooling the release phase cannot install itself** — analyzer, mutation runner,
  accessibility checker, load tool, whatever `dev-architecture` named.
- **Three committed records** in `.dev-skills/project-setup/`: `setup-plan.md`, `setup-log.md`,
  **`verification.md`** (the run/drive/prove contract `verify-feature` reads).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes (read this first)

Read `mode` from `.dev-skills/build-plan/.build-config.md`; if absent, ask once (default
**interactive**) and write it (**`../_shared/build-pipeline/build-config.md`**).

- **interactive** — present the plan by section and stop for approval (whole or per-section; the
  user may drop or defer items) before executing.
- **autopilot** — execute (B) and the config files in (C) without asking; (A) global installs, secret
  writes and plugin/MCP installs **still** confirm (`careful` — Rule 1).

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
Read `dev-architecture.research.md` (local-run topology, verification matrix, AI tooling),
`architecture.research.md` (the stack) and `adr/*`. List: components and their local stand-ins, the
one-command bring-up, the seed strategy, the test matrix **and its scoped selector**, the
**environment-access model and developer/test scripts**, the **custom project skills** to author, the
AI tooling (MCP servers, plugins, CLAUDE.md content, permissions). No `dev-architecture.research.md` →
say so and offer `/design-dev-architecture` first.

### Stage 1: Detect state (read-only)
Probe: git repo? required tools on PATH? which target files exist (`.gitignore`, `CLAUDE.md`,
`.claude/settings.json`, compose file, seed scripts, entrypoint)? services running (ports in use)?
Record it so later stages skip it.

### Stage 2: Plan (four sections, every item traced)
Write `.dev-skills/project-setup/setup-plan.md` (template: `references/setup-templates.md` §1) as a
checklist: **(A) global installs** *(gated)* · **(B) repo scaffolding** *(auto-applicable)* · **(C) AI
tooling** *(config auto, installs gated)* · **(D) manual-only** — each item with **action · provenance
(component/ADR) · reversibility · idempotency note · already-present?**. What belongs where:
**`references/plan-and-smoke.md`**.

### Stage 3: Approve
Per **Modes**: interactive waits for approval; autopilot proceeds, gated items still confirm.

### Stage 4: Execute
Apply approved items in order: skip what Stage 1 found; before overwriting, back up (`<file>.bak`) or
show a diff and ask. Log each action (done / skipped-already-present / deferred). A failing step →
stop, report the exact error, offer a fix.

### Stage 5: Smoke-test (replaces the spec pipeline's adversarial review)
Run the one-command bring-up and prove it **green**: stack up, app reachable, seed data present, one
basic flow driven to a real observed outcome. Then prove the gate has teeth **twice**: a deliberate
static error makes `make check-fast` fail and the pre-commit hook block; `make test-scoped SCOPE=…`
runs visibly *fewer* tests than the full run. "No error in the logs" is not proof. What each proof
looks like: **`references/plan-and-smoke.md`**.

### Stage 5b: Design system → `DESIGN.md` (UI projects only)
No UI, or **Design system / Needed? = no** → skip, note it in the setup log. An existing root
`DESIGN.md` → leave it alone. Otherwise write it **directly from the spec** — tokens from the installed
kit's real theme values or the recorded brand intent — per **`references/design-md-format.md`**
("Writing DESIGN.md during setup"); prove it renders on one real screen; write the `design-system.md`
record. Tokens land under `## Frozen decisions` (**`../_shared/build-pipeline/design-freeze.md`**);
never deviate from the spec's design decisions.

### Stage 6: Record + handoff
Write `setup-log.md` — **done**, **skipped (already present)**, **your turn** (which secret/account,
where it goes). Write `verification.md` from the now-real stack — the concrete **run / drive / prove**
commands per surface: bring-up, driving UX/Backend/E2E, proving an outcome, the three gate commands and
what a task's scoped run selects, the dummy-auth token, seed/reset commands, where logs are. Hand off —
interactive: name the two files and point at `/plan-development`; autopilot: record the same and hand
back. Close with the **«What you should do»** block (**`../_shared/build-pipeline/report-format.md`**):
the manual-only items, one imperative line each.

## When the repo already has a working setup

No special mode — detect-state-first does the work. Three specifics:

1. **Plan the difference** — *(what the inner loop needs) minus (what's already there)*. Read the CI
   config too; it often defines the real gate.
2. **Adopt & extend, never overwrite.** An existing `Dockerfile` / compose / `Makefile` is extended
   (back up first); the gate wires the *existing* lint/format/type tools behind the three targets;
   env-access helper, dev-script and custom-skill skeletons only where absent; `verification.md` still
   written **fresh**; an installed UI kit is kept and `DESIGN.md` written from its actual theme values.
3. **Smoke-test the existing gate too** — teeth, `make test-scoped` really selecting. A red
   pre-existing gate is **surfaced**, never silently accepted: offer to fix, or file it as a gap for
   `plan-development`.

## Rules

1. Never run a machine-global install (`brew`/`apt`/`npm -g`), write a secret or install a plugin/MCP
   server without explicit confirmation, shown as the exact command — in either mode. Repo-local
   scaffolding may auto-apply.
2. Idempotent: detect first (never assume a clean machine or repo), skip what's present, never clobber.
3. Every action traces to a component/tool/ADR in the spec — no orphan setup, no re-chosen stack, no
   production scale/HA locally, no tooling the spec didn't choose. A spec gap is surfaced back.
4. "Done" = the one-command bring-up smoke-tested green and drivable — not files that exist.
5. Irreducible manual steps (secrets, cloud accounts, licenses) go in `setup-log.md` as "your turn" —
   never pretended done.
6. Always write `verification.md` — the build phase depends on it.
7. Production-side setup — platform, database, caps, telemetry — is `setup-production-environment`'s,
   not yours.
8. **Three gate targets**: `make check-fast` (static) behind the pre-commit hook ·
   `make test-scoped SCOPE=…` (a task's paths or tag) for the build loop — required, prove it really
   selects · `make check` (static + whole suite) for the release pipeline. **No** test step in the
   hook, **no** turn-end Stop/PostToolUse hook; a red static gate blocks the commit.
9. Bake the **env-access mechanism** into bring-up (acquire on `make dev`, release on `make down`,
   lease + stale-reclaim and/or per-run isolation; gitignore the lock file). Write the committed
   allow/deny **permissions block** into `.claude/settings.json` so the loop reads test results,
   reports, coverage and local binaries without a prompt per file (**`env-access.md`** → "Permissions
   the loop needs"). Scaffold the **developer/test-script** and **custom project-skill** skeletons the
   dev-architecture named — full implementation is backlog work.
10. Recommend the matching **LSP plugin** from the official marketplace per typed language
    (`typescript-lsp`, `pyright-lsp`, …); exclude generated/build/vendor trees via `permissions.deny`.
    Config repo-local, installs gated (`references/setup-templates.md` §5).
11. Keep the project `CLAUDE.md` lean and layered — root for the big picture, a short per-package file
    with *scoped* commands in a monorepo (`references/setup-templates.md` §7).
