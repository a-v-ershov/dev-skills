# Setup templates

Three documents `setup-dev-environment` produces under `.dev-skills/project-setup/`. Fill the angle-bracket
placeholders from the spec and the detected state.

> The project `CLAUDE.md` it scaffolds (section B above) is **not** templated here: its stack notes +
> commands are stack-specific, and its **project documentation map** block is rendered from the shared
> spec **`_shared/agent-guide.md`** (marker-delimited, idempotent — touch only that block).

## 1. `setup-plan.md` — the approvable plan

```markdown
# Setup plan — <Product name>

> Date: <YYYY-MM-DD> · Source: dev-architecture.research.md, architecture.research.md
> Mode: <interactive | autopilot>

## A. Global installs  (gated — run only with confirmation; shown as exact commands)
| Item | Command | From (component / ADR) | Reversible? | Already present? |
|------|---------|------------------------|-------------|------------------|
| Docker | `brew install --cask docker` | local stack / adr-0007 | yes (uninstall) | no |
| pnpm | `corepack enable` | JS toolchain | yes | no |

## B. Repo scaffolding  (auto-applicable — repo-local)
| Item | Action | From | Reversible? | Already present? |
|------|--------|------|-------------|------------------|
| .gitignore | write Node/OS ignores | stack | yes (git) | no |
| docker-compose.yml | app + Postgres + MinIO | local-run topology | yes | no |
| seed script | scripts/seed.ts | seed strategy | yes | no |
| entrypoint | Makefile `dev` target → `docker compose up` | one-command bring-up | yes | no |
| quality gate | linter+formatter+typechecker config (zero-tolerance) | test levels / quality-gate.md | yes | no |
| `make check-fast` | target running format + lint + type-check + suppressions (no tests) | quality-gate.md | yes | no |
| `make test-scoped` | target running **only** the tests matching `SCOPE=<paths\|pattern>` — the build loop's run | quality-gate.md | yes | no |
| `make check` | static checks **plus** the whole accumulated suite — the release pipeline's run, never a hook's | quality-gate.md | yes | no |
| pre-commit hook | runs `make check-fast`, blocks commit on red | quality-gate.md | yes | no |
| env-access | lock helper baked into bring-up (gitignored lock) and/or per-run isolation | env-access.md | yes | no |
| dev/test scripts | skeleton of fast local scripts (full impl = backlog) | dev-architecture / dev scripts | yes | no |
| custom project skills | skeleton `.claude/skills/<name>/SKILL.md` stubs (full authoring = backlog; §6) | dev-architecture / custom skills | yes | no |
| project CLAUDE.md | stack notes + commands **+** project documentation map (`_shared/agent-guide.md`) | AI tooling | yes | partial (back up) |

## C. AI tooling  (config auto; plugin/MCP installs gated)
| Item | Action | From | Gated? |
|------|--------|------|--------|
| .claude/settings.json | **`permissions.deny`** (exclude generated/build/vendor) — **no gate-running Stop/PostToolUse hook** | AI tooling / quality-gate.md / §5 | no (config) |
| LSP plugin: <lang> | `/plugin install <lang>-lsp@claude-plugins-official` — symbol navigation | AI tooling / §5 | yes (install) |
| MCP: postgres | register db MCP server | AI tooling | yes (install) |
| plugin: <name> | install | AI tooling | yes (install) |

## D. Manual-only  (your turn — cannot be automated)
| Item | What you must do | Where it goes |
|------|------------------|---------------|
| <Cloud account> | create account, get API key | `.env` → `<VAR>` |
| <Secret> | obtain <secret> | `.env` → `<VAR>` |
```

## 2. `setup-log.md` — what actually happened

```markdown
# Setup log — <Product name>

> Date: <YYYY-MM-DD>

## Done
- Scaffolded .gitignore, docker-compose.yml, scripts/seed.ts, Makefile.
- Wrote project CLAUDE.md (backed up previous to CLAUDE.md.bak).
- Registered the postgres MCP server.
- Smoke-test: `make dev` came up green; app reachable at http://localhost:3000; seed data present;
  `make check` green, `make test-scoped SCOPE=tests/health` ran 3 tests (not the suite), and the
  pre-commit hook blocks a commit with a deliberate type error.

## Skipped (already present)
- Docker (already installed). Node 20 (already on PATH).

## Your turn (manual — required before the app fully works)
- [ ] <Cloud> API key → put in `.env` as `<VAR>` (the stack reads it for <purpose>).
- [ ] <Secret> → `.env` `<VAR>`.
```

## 3. `verification.md` — the run/drive/prove contract (verify-feature reads this)

The concrete commands, filled in from the now-real stack — the dev-architecture verification matrix
made executable. This is the project-specific input the generic `verify-feature` skill consumes.

```markdown
# Verification contract — <Product name>

> Source: dev-architecture.research.md (verification loop). Commands are real and runnable.

## Bring it up
- One command: `make dev`  → starts <services>, seeded, ready.
- App URL: <http://localhost:3000> · Default seeded login: <user / token>.
- Logs: `make logs` (or `docker compose logs -f <svc>`).

## Environment access (one shared env — coordinate or isolate)
- Mechanism: <advisory lock baked into `make dev`/`make down` (lease + stale-reclaim) and/or per-run
  isolation (`--data-dir` / `COMPOSE_PROJECT_NAME` + port offset)>.
- Acquire / release: `make dev` acquires · `make down` releases · force-clear a stuck lock: `make env-unlock`.
- Standalone skill runs acquire and release the env themselves. Method: `_shared/build-pipeline/env-access.md`.

## Gate (three commands — one automatic, two deliberate)
- `make check-fast` → format check + lint + type-check + suppressions. **No tests.** This is what the
  pre-commit hook runs; a red one blocks the commit.
- `make test-scoped SCOPE=<paths|pattern>` → **only** the tests matching the scope. This is the
  **build loop's** test run: the implementer's self-check and hand-off, the verifier's run, and
  `run-task` before the checkpoint commit. Selector for this stack:
  `<pytest tests/<area> -k <pattern> · vitest run <path> · playwright test --grep @<tag>>`.
- `make check` → static checks plus **the whole accumulated suite**. This is the **release
  pipeline's** run: `refactor` (before and after each step), `write-tests` (at the end),
  `cut-release` (before the cut). The build loop never runs it.
- Zero-tolerance: fails on lint/type errors, new warnings, and new suppression comments.
- **No Claude Code Stop / PostToolUse hook running any of them.** Method:
  `_shared/build-pipeline/quality-gate.md`.

## What a task's scoped run selects
1. the tests written for the task (the implementer's unit tests + the verifier's adversarial ones);
2. the tests of the modules the task's diff touched (`git diff --name-only` → the tests beside them
   and the ones importing them);
3. nothing else. Target: **under ~2 minutes**. Longer means the selection is too wide or the tests sit
   at the wrong level.

## Drive & prove, per surface
| Surface | Run it | Drive it | Prove it (observable) |
|---------|--------|----------|-----------------------|
| UX / Frontend | `make dev` | Playwright (`pnpm e2e`) / Claude-in-Chrome | screenshot diff in artifacts/ |
| Backend | `make dev` | `curl localhost:3000/api/...` | query DB (`make psql`) — row landed? · grep structured log |
| E2E | `make dev` | `pnpm e2e -- <flow>` | assertions in the e2e run |

## Unblock (remove human-in-the-loop)
- Dummy auth: `<how to get a test session / token>`.
- Seed / reset: `make seed` / `make reset` — known starting state.
- Structured logs the agent can grep: `<format / how>`.

## Test levels (write at the cheapest one that proves the thing)
| Level | Command | Scoped form | Covers | Typical cost |
|-------|---------|-------------|--------|--------------|
| Unit — **the default** | `pnpm test` | `pnpm test <path>` | logic, validation, formatting, state transitions | ms |
| Integration — a real seam | `pnpm test:int` | `pnpm test:int <path>` | route writes + reads back, ownership rules, idempotency | seconds |
| E2E (agent-driven) — **the exception** | `pnpm e2e` | `pnpm e2e --grep @<tag>` | a person's path across a screen, when it cannot be proven below — **at most one per task** | tens of seconds+ |

- Tests live in `<dir>` (e.g. `tests/`); name a new one `<convention>` (e.g. `test_<unit>.py` /
  `<name>.test.ts`). The verifier writes its adversarial tests here; the implementer may add its own.
- **Tag or path-group new tests so they can be selected** (e.g. `@<task-id>` / a folder per area) —
  the scoped run is only as good as what it can address.
- Slow-by-design primitives (Argon2/bcrypt, retry backoff, deliberate rate limits) run at **test-cost
  parameters** here: `<how it is switched>`.

## Developer & test scripts (fast, intentionally-divergent local paths)
| Command | Purpose | Diverges from prod by | Isolated? |
|---------|---------|------------------------|-----------|
| `<run subset / stage>` | fast iterate on one stage | skips expensive stages; cached intermediates | per-run `--data-dir` |
| `<fixture / sample gen>` | known inputs + intermediates | local sample data, no cloud | yes |
| `<inspector / visualizer>` | see an intermediate outcome | local render, no prod assets | yes |
```

## 4. The pre-commit hook (copy-ready) — and the hook that must NOT exist

**The only automatic gate is the pre-commit hook, and it runs the static checks.** `.githooks/pre-commit`,
wired with `git config core.hooksPath .githooks`:

```bash
#!/usr/bin/env bash
# The static gate, on every commit. Red blocks the commit.
#
# NO TESTS HERE — not the suite, not a scoped run. A compiler-shaped check
# costs seconds and is worth paying without being asked; a test run is not.
# Tests are run deliberately by the skills that assert something with them:
# `make test-scoped` in the build loop (implement-feature, verify-feature,
# run-task) and `make check` in the release pipeline. Do not add a test step
# back under any name — "just the changed files" is still a test step, and a
# hook cannot know which selection this commit is about.
#
# Escape hatch: `git commit --no-verify` — for a deliberate failure, explained
# in the commit message.

set -e
make check-fast
```

**Do NOT write a Claude Code `Stop` or `PostToolUse` hook that runs a gate.** It reads as free
insurance and is not:

- A gate that is red mid-task is the **normal** state halfway through building something. The hook
  turns that into a blocked turn and a polling loop around it.
- Measured case: a `Stop` hook running the full gate killed a turn over a **formatter warning** on a
  work-in-progress file. The agent spent that turn on whitespace instead of the task it was given.
- It buys nothing the pipeline doesn't already have: `implement-feature` runs the static gate plus the
  task's scoped tests before handing off, `run-task` runs them again before the checkpoint commit, and
  the release pipeline runs the whole suite. Those are the moments where something is actually being
  asserted; the end of a turn is not one of them.

If a project already has such a hook, removing it is a fix, not a loosening
(`_shared/build-pipeline/quality-gate.md`).

## 5. `.claude/settings.json` — code intelligence (LSP) + navigation deny

Two more blocks in the **same** `.claude/settings.json` (merge with the `hooks` block above): the
**LSP plugins** that give the agent symbol-level navigation, and a **`permissions.deny`** list that
keeps generated/build/vendor trees out of the agent's reading and grep.

LSP is delivered as **plugins** from the official marketplace (`claude-plugins-official`); each plugin
drives a language-server binary that must be on `$PATH`. Recommend the plugin(s) for the stack's typed
languages — the install is gated (the `careful` pattern, shown as the exact `/plugin install` command),
the binary is fetched per the plugin. There is no separate "LSP MCP" and no `.claudeignore` file — these
two settings blocks are the mechanism.

| Language | Plugin | Language-server binary |
|----------|--------|------------------------|
| TypeScript / JS | `typescript-lsp` | `typescript-language-server` |
| Python | `pyright-lsp` | `pyright-langserver` |
| Go | `gopls-lsp` | `gopls` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` |
| Java | `jdtls-lsp` | `jdtls` |
| C / C++ | `clangd-lsp` | `clangd` |

```json
{
  "enabledPlugins": {
    "typescript-lsp@claude-plugins-official": true
  },
  "permissions": {
    "deny": [
      "Read(./**/node_modules/**)",
      "Read(./**/dist/**)",
      "Read(./**/build/**)",
      "Read(./**/.next/**)",
      "Read(./**/*.generated.*)",
      "Read(./**/vendor/**)"
    ]
  }
}
```

- **Pick the plugins for the stack's languages**, not all of them. A typed language left on text-grep
  navigation is exactly the low-ROI case the research flags — symbol navigation is the high-ROI fix.
- **`permissions.deny` follows gitignore semantics** (`*` within a path segment, `**` across
  directories). It blocks the agent from *opening* a generated/vendor file once found (it does not
  filter the file out of a recursive search result), and it covers `Read` / `Edit` / `Grep` / `Glob`
  and the recognized Bash file commands. Commit it so the whole team — and every agent — gets the same
  noise reduction. Tune the globs to the stack (`target/`, `__pycache__/`, `.venv/`, `bin/obj/`).
- **`enabledPlugins` records the choice**; the actual install is gated like every other plugin/global
  step. Add the service MCP plugins the dev-architecture tooling section named (e.g. a database or
  source-control MCP) the same way.

## 6. `.claude/skills/<name>/SKILL.md` — custom project-skill skeleton

For each **custom project skill** the dev-architecture's *Custom project skills* table named, scaffold a
skeleton at `.claude/skills/<name>/SKILL.md` in the **built project's** repo (not dev-skills's). These are
**committed**, project-local, and **complement `verification.md`** — they wrap a dev/test script or the
e2e harness into a named, invocable verification job; they never duplicate `verify-feature`. The skeleton
carries the discoverable frontmatter and a thin body that calls the wrapped script, with the procedure
left as a TODO — `plan-development` files a backlog task to author it fully (blocked on the wrapped
script). Repo-local, so auto-applicable; never overwrite an existing skill of the same name.

```markdown
---
name: <verb-name>            # e.g. run-integration-tests
description: "<Third-person: WHAT it does and WHEN to use it — this is how Claude selects the skill.
  e.g. Run the integration suite against the local stack and report failures. Use after a change that
  touches <area>, or before pushing.>"
---

# <Verb-name>

<!-- TODO (backlog: author fully) — wraps: <script / harness, e.g. `make test:int`>.
     Complements .dev-skills/project-setup/verification.md; does NOT duplicate verify-feature. -->

1. Bring up / ensure the local env (acquire the env-access lock — see verification.md).
2. Run the wrapped script: `<command>`.
3. Assert the observable outcome (exit code · asserted rows/logs/screenshots — not "it ran").
4. Report pass/fail with the evidence; on fail, surface the failing case for the agent to fix.
```

- **Workflow-level, not a thin alias.** Each skill encodes a whole verification job (bring up → drive →
  assert → report), so it earns its name; a one-liner that just shells out adds nothing.
- **The depth lives in the wrapped script**, not the skill — the skill is the discoverable, reusable
  entry point future agents invoke by name.

---

## 7. What setup produces — the outputs inventory

Everything below is repo-local unless marked otherwise. `.dev-skills/project-setup/` is committed
project documentation.

### Repo files
`.gitignore`, a project `CLAUDE.md`, `.claude/settings.json` + MCP config, the Docker Compose stack,
seed scripts, a one-command entrypoint (`Makefile` / `justfile` / script), and the directory skeleton
— whatever `dev-architecture` specifies.

The project `CLAUDE.md` carries two parts: your stack notes + commands, **and** the marker-delimited
**project documentation map** — write or refresh that block per `../../_shared/agent-guide.md` so an
agent can navigate `.dev-skills/project-spec/`, `build-plan/` and `project-setup/`. An earlier
`create-project-spec` run may already have seeded the block; refresh it in place, idempotently.

Keep that file **lean and layered**: the root holds the big picture — the project-map block, stack
notes, key commands, the load-bearing gotchas — and nothing deeper. For a monorepo, also seed a short
`CLAUDE.md` in each package with its *local* conventions and its **scoped** commands, so the agent
doesn't run the whole repo's suite for a one-package change; Claude loads them additively up the tree.
For a single small package the root file is enough — don't over-split.

### The quality gate
Linter + formatter + type-checker configs (zero-tolerance) and **three targets** — `make check-fast`
(static checks), `make test-scoped SCOPE=…` (only the tests belonging to given paths/pattern — what
the whole build loop uses), `make check` (static + the whole suite, run by the release pipeline) —
plus a **pre-commit hook that runs the static gate** and blocks the commit on red.

**No test step in that hook — not the suite, not a scoped run — and no Claude Code Stop / PostToolUse
hook that runs a gate when a turn or an edit ends.** Both are ruled out in
`../../_shared/build-pipeline/quality-gate.md`, which defines the gate once. Setup **executes** the
test levels `design-dev-architecture` specified; it does not re-pick tools.

### Environment access, developer scripts, custom-skill skeletons
Whichever env-access mechanism `dev-architecture` chose — the **advisory-lock helper** baked into the
bring-up/teardown commands (lock file gitignored) and/or the **per-run isolation** params — plus the
**skeletons of the developer & test scripts** it specified (fast, intentionally-divergent local paths;
full implementation is backlog work), and the **skeleton `.claude/skills/<name>/SKILL.md` stubs** of
the **custom project skills** it specified (frontmatter `name` + discoverable `description` and a thin
body invoking the wrapped script, with the procedure left as a TODO; full authoring is a backlog
task). See `../../_shared/build-pipeline/env-access.md` and §6 above.

### The design system (UI projects only)
The spec already decided it; here you make it real, in this order:

1. **Install** the UI kit and icon set `define-design-decisions` named, per the kit's **current
   official instructions** — check them, install commands go stale; don't run them from memory.
2. **Write the committed root `DESIGN.md`** — tokens + rationale, straight from the spec's design
   direction and the installed kit's own theme. Format and the full procedure:
   `design-md-format.md`; per-kit token mapping: `adoption-recipes.md`. Plus the short
   `.dev-skills/project-setup/design-system.md` record.
3. **Write the UI rule into the project `CLAUDE.md`** — components come from the kit, colours and
   spacing from the design tokens, icons from the one chosen set. Without that rule the next session's
   agent hand-rolls its own button.

Skipped entirely for a no-UI project, or when `design-decisions` says no system is needed.

### The quality tooling the release phase will need
Repo-local dev dependencies wired behind the project's own commands: whatever `dev-architecture` named
for measuring the codebase and the suite — a duplication/dead-code analyzer, a mutation-testing runner,
an accessibility checker, a load tool. Install them **here**, because the release phase deliberately
cannot: `refactor`, `write-tests` and every `audit-*` are forbidden from installing anything and record
a missing tool as *unmeasured*. A tool nobody installed is a measurement nobody takes.

### The three records
- `.dev-skills/project-setup/setup-plan.md` — the approvable plan (§1).
- `.dev-skills/project-setup/setup-log.md` — done / skipped / deferred to the human (§2).
- `.dev-skills/project-setup/verification.md` — the run/drive/prove contract `verify-feature` reads (§3).
