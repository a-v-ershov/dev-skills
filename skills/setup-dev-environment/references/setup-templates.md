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
| `make check` | target running lint + type-check + tests | quality-gate.md | yes | no |
| pre-commit hook | runs `make check`, blocks commit on red | quality-gate.md | yes | no |
| env-access | lock helper baked into bring-up (gitignored lock) and/or per-run isolation | env-access.md | yes | no |
| dev/test scripts | skeleton of fast local scripts (full impl = backlog) | dev-architecture / dev scripts | yes | no |
| custom project skills | skeleton `.claude/skills/<name>/SKILL.md` stubs (full authoring = backlog; §6) | dev-architecture / custom skills | yes | no |
| project CLAUDE.md | stack notes + commands **+** project documentation map (`_shared/agent-guide.md`) | AI tooling | yes | partial (back up) |

## C. AI tooling  (config auto; plugin/MCP installs gated)
| Item | Action | From | Gated? |
|------|--------|------|--------|
| .claude/settings.json | hooks + **`permissions.deny`** (exclude generated/build/vendor) | AI tooling / quality-gate.md / §5 | no (config) |
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
  `make check` green and the pre-commit hook blocks a deliberately-broken commit.

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

## Gate (must be green before commit)
- One command: `make check` → format check + lint + type-check + tests (the accumulated suite).
- Zero-tolerance: fails on lint/type errors, new warnings, and new suppression comments.
- Enforced by a pre-commit hook (blocks the commit on red) and a Claude Code Stop hook (feeds failures
  back). Method: `_shared/build-pipeline/quality-gate.md`.

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

## Test levels
| Level | Command | Covers |
|-------|---------|--------|
| Unit | `pnpm test` | <...> |
| Integration | `pnpm test:int` | against local stand-ins |
| E2E (agent-driven) | `pnpm e2e` | the user flows, no manual step |

- Tests live in `<dir>` (e.g. `tests/`); name a new one `<convention>` (e.g. `test_<unit>.py` /
  `<name>.test.ts`). The verifier writes its adversarial tests here; the implementer may add its own.

## Developer & test scripts (fast, intentionally-divergent local paths)
| Command | Purpose | Diverges from prod by | Isolated? |
|---------|---------|------------------------|-----------|
| `<run subset / stage>` | fast iterate on one stage | skips expensive stages; cached intermediates | per-run `--data-dir` |
| `<fixture / sample gen>` | known inputs + intermediates | local sample data, no cloud | yes |
| `<inspector / visualizer>` | see an intermediate outcome | local render, no prod assets | yes |
```

## 4. `.claude/settings.json` — the quality-gate hook (copy-ready)

The Claude Code **Stop hook** that runs the gate after the agent finishes editing and **feeds the
failures back** so it fixes them before finishing — the in-session counterpart of the pre-commit hook.
Drop this into the project's `.claude/settings.json` (merge it with any existing `hooks` block):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "make check 1>&2 || { echo 'Quality gate (make check) is red — fix the reported issues before finishing.' 1>&2; exit 2; }",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

- **Exit codes do the work.** `make check` green → exit 0, the agent stops normally; red → the wrapper
  exits **2**, which blocks the stop and feeds the gate's own output back as the next thing to fix.
- **Keep it actionable, keep it fast.** If the full suite is slow, point the Stop hook at a faster
  subset (lint + type-check + changed-file tests) and let the **pre-commit hook** run the whole suite —
  the commit is the hard gate (`_shared/build-pipeline/quality-gate.md`). Raise `timeout` (seconds) to
  fit the gate's runtime.
- It is the same gate `make check` runs everywhere; the hook changes only *when* it runs (on stop) and
  *that a red result blocks* — never *what* it checks.

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
