# Dev Architecture — <Product name>

> Status: Draft | Date: <YYYY-MM-DD>
> Source: .dev-skills/project-spec/architecture.research.md, .dev-skills/project-spec/user-flows.research.md
> Scope: the inner loop — local run + AI-drivable testing + AI tooling. NOT the production design.

## Constraints

- **Developer OS targets:** <macOS / Linux / Windows / WSL.>
- **AI coding agents in use:** <Claude Code, and any others.>
- **Existing team tooling:** <what is already in place.>

## Local-run architecture

> One command brings the whole product up locally, seeded and ready — usable by both the AI agent
> and a human developer. Local stand-ins are chosen for API parity with the production service.

**Bring it all up:** `<single command, e.g. docker compose up>` → <what it starts, seeded>.

**Human access:** <local URL / port to open, default seeded login, where to watch logs — so a
person can run and use the product, not only an agent.>

| Component (from architecture) | Prod service | Local stand-in | Why (API parity) | Divergence from prod |
|-------------------------------|--------------|----------------|-------------------|----------------------|
| <object store> | <S3> | <MinIO / LocalStack container> | <same S3 API> | <no IAM, single node> |
| <database> | <managed Postgres> | <Postgres container> | <same engine/version> | <no HA, no backups> |
| <auth / BaaS> | <BaaS> | <emulator / OSS equivalent> | <...> | <...> |

- **Compose topology:** <services, networks, volumes — the shape of the local stack.>
- **Seed data:** <how the local stack is populated and reset.>
- **Env / secrets:** <how config and secrets are provided locally — never real secrets in the repo.>
- **Build-shape parity with the target platform:** <the artifact the chosen host runs (serverless
  functions / long-lived process / container image) + the runtime major version, and the one command
  that produces that same shape locally.>
- **Schema migrations:** <the mechanism, identical locally and in prod; how the agent applies and
  rolls back. Seeding is not a migration test.>
- **Env-var contract:** <the variables the chosen platform requires, mirrored in `.env.example`, and
  the check that fails loudly at bring-up when one is missing.>
- **Analytics in checks:** <where events go during verification — a local sink or a no-op, never the
  production counter.>
- **Environment access model:** <how concurrent actors avoid clobbering the one shared env — an
  advisory lock baked into bring-up (lease + stale-reclaim) for the shared stack, and/or per-run
  isolation (ephemeral data dir / unique compose project + port offset). Per
  `_shared/build-pipeline/env-access.md`.>

## Developer & test scripts (fast, intentionally-divergent local paths)

> Purpose-built scripts that **deliberately diverge** from prod for fast iteration / integration
> testing — distinct from the parity stand-ins above. Each names its intentional divergence (a
> documented speed tradeoff, not a parity risk). `setup-dev-environment` scaffolds the skeleton; the
> full scripts are built as backlog tasks.

| Script / command | Purpose | Intentional divergence from prod | How the agent uses it |
|------------------|---------|----------------------------------|-----------------------|
| <run subset / single stage> | <fast iterate on one stage> | <skips transcription; uses cached intermediates> | <drive a stage; assert its output> |
| <fixture / sample generator> | <known inputs + pre-computed intermediates> | <local sample data, no cloud> | <seed a known state fast> |
| <intermediate inspector / visualizer> | <see crop / scene / caption output> | <local render, no prod assets> | <prove an intermediate outcome> |

## Verification loop (maximize the agent's autonomous feedback)

> The point of this phase: give the agent the most ways — and the fastest — to run the product,
> drive it, prove the real outcome, and unblock itself, so it builds autonomously at high quality.
> Fill the matrix for each surface the product has (drop a column that doesn't apply).

| Move | UX / Frontend | Backend | E2E |
|------|---------------|---------|-----|
| **Run it** (one command) | <dev server cmd> | <make dev / docker compose up> | <bring up staging-like env> |
| **Drive it** (exercise) | <Claude-in-Chrome / Playwright> | <curl the route, hit health endpoints> | <run the flow against staging> |
| **Prove it** (observe real outcome) | <screenshot before/after> | <query the DB — did the row land? · read structured logs — did the path run?> | <replay prod traffic; assert> |
| **Unblock it** (remove friction) | <dummy auth · seed scripts for known state> | <structured logs the agent can grep · add log lines to prove the path ran> | <safe / idempotent test data> |

### Test levels

| Level | Covers | Tool | Runs in CI? |
|-------|--------|------|-------------|
| Unit | <...> | <...> | <...> |
| Integration | <against the local stand-ins> | <...> | <...> |
| E2E (agent-driven) | <the user flows, no manual steps> | <Playwright / harness> | <...> |

- **Test data:** <how provisioned and reset between runs.>
- **Design-system enforcement:** <the kit's / stack's own lint rule wired into `make check` (e.g. the
  Tailwind or kit ESLint config), or "none available — reviewed by eye". Never a custom grep-based
  color hunt: false positives get the gate disabled.>

**Flow → verification** (from user-flows.research.md) — every flow run → driven → proven, no manual step:

| Flow | How the agent drives it | How it proves success | Alternate / error paths |
|------|-------------------------|-----------------------|-------------------------|
| <flow> | <Playwright script / curl> | <screenshot / DB row / log line> | <...> |

## AI-development tooling (tuned to the stack)

- **Claude Code config:** <what belongs in project CLAUDE.md; useful settings.json hooks.>
- **MCP servers:** <which to wire for this stack (db / browser / cloud / …) and why.>
- **Recommended Anthropic / Claude Code plugins & skills to install:** <which standard, existing ones
  improve dev for this stack, and what each gives. (Custom skills to *author* go below.)>
- **Other agents (if used):** <equivalent config/plugins for Codex / Cursor / … .>

### Custom project skills (wrap the scripts — invocable by name)

> Project-local Claude Code skills to *author* (beyond the standard ones to install above) so a future
> agent runs the verification loop **by name**. Workflow-level — one skill per verification job, not a
> thin alias per script. They live in the built project's `.claude/skills/<name>/SKILL.md`, are
> committed, and **complement `verification.md`** (the machine contract `verify-feature` reads) — they
> never duplicate `verify-feature`. `setup-dev-environment` scaffolds the skeletons; full authoring is a
> backlog task, blocked on the script each wraps.

| Skill (name) | Wraps (scripts / harness) | What it does (procedure) | When the agent invokes it |
|--------------|---------------------------|--------------------------|---------------------------|
| `/run-integration-tests` | <integration suite / `make test:int`> | bring up env → run suite → report failures | after a change touching <area> |
| `/verify-flow <name>` | <e2e harness, e.g. Playwright> | seed known state → drive the flow → assert the observable outcome | proving a user flow end-to-end |
| `/reset-env` | <seed / reset scripts + env-access teardown> | tear down → re-seed a clean known state | when local state is dirty / unknown |

## Decisions (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| adr/<NNNN>-<slug>.md | <one-line summary, e.g. MinIO vs LocalStack> | Proposed / Accepted |

## Divergences & risks (local ↔ prod)

| Divergence / risk | Impact | Mitigation / why acceptable |
|-------------------|--------|-----------------------------|
| <local has no HA> | <won't catch failover bugs> | <covered in staging> |

## Sources

<Every source consulted while verifying tooling (local stand-in capabilities & API parity, e2e
framework, available MCP servers, current Claude Code plugins/skills), referenced inline above as
[S1], [S2], … See _shared/spec-pipeline/output-format.md.>

- [S1] <title> — <url>
- [S2] <claim> — no reliable source found

## Forks / Decisions log

<Every decision point this phase hit and who resolved it. Required in both modes. A significant,
hard-to-reverse fork also gets a full ADR — reference it here.>

| # | Fork (the open question) | Options considered | Decision | By | Rationale | Confidence | Source / ADR | Needs human confirm? |
|---|--------------------------|--------------------|----------|----|-----------|-----------|--------------|----------------------|
| 1 | <question> | A / B / C | <chosen> | AI \| human | <why> | high\|med\|low | [S2] / adr/0007 | yes \| no |

## Open questions

- <Unresolved dev-environment or tooling question carried into implementation.>
