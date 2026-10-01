# Environment access (shared — build pipeline)

The local dev environment (stack, ports, local DB, seed state) is a **single stateful resource**
several actors reach for (a second `build-tasks` run, a standalone skill, a human): access is
**coordinated or isolated**. `design-dev-architecture` picks the mechanism per stack,
`setup-dev-environment` implements it, `build-tasks` holds the lease across a task.

## Two mechanisms (chosen per stack)

### 1. Advisory lock — for a single shared stack
For one heavy shared stack (Docker Compose, a real local DB, fixed ports):

- **Lock file** — a **gitignored** runtime file (e.g. `.dev/env.lock`), never committed (the build
  pipeline's one transient runtime file). Holds: holder id (task id / session / `human`), pid,
  `acquired_at`, `heartbeat_at`, action.
- **Baked into the entrypoint** — bring-up acquires (`make dev` → acquire, then start), teardown
  releases (`make down` → stop, then release); everyone runs the same command, so it can't be forgotten.
- **Lease + stale reclaim** — the holder re-stamps `heartbeat_at`; past the TTL (e.g. 10 min) the lock
  is presumed abandoned and any actor may reclaim it, so a killed holder can't deadlock the env.
- **Escape hatch** — `make env-unlock` force-clears a stuck lock for a human.
- **Contended** — held and fresh → wait (bounded) or refuse, naming the holder and since when.

### 2. Per-run isolation — where it's cheap
When a run can be namespaced cheaply, isolate instead — no lock, runs go in parallel:

- An **ephemeral data dir** per run (`--data-dir <tmp>`), a **unique compose project name**
  (`COMPOSE_PROJECT_NAME=app-<id>`) + a **port offset**, or a separate DB schema per run.
- Best for the cheap, process-local **developer/test scripts**, which carry their own state.

Often **both**: the lock guards the heavy shared stack; the fast dev scripts isolate and skip it.

## Who coordinates

- **`build-tasks`** holds the lease for a task's span (implement → verify → gate), releases it after
  the checkpoint commit, and **reclaims a stale lock** left by its own killed run on resume. Its
  subagents inherit it (same holder id → the entrypoint sees the lock is theirs).
- **Standalone** runs of `implement-feature` / `verify-feature` / `setup-dev-environment` acquire and
  release it themselves.
- The commands and the mechanism in use are recorded in `.dev-skills/project-setup/verification.md`.

## Permissions the loop needs

The loop constantly reads its own output (test reports, coverage, evidence, local binaries); a
permission prompt on each read ends autonomy. So `setup-dev-environment` writes a committed **allow**
block into `.claude/settings.json` for the harness's own artefacts, beside the `permissions.deny` list
that keeps generated trees out of navigation. Derived from the stack, not a fixed list:

> Anything **this project's own tooling writes** and the agent is expected to read back is allowed.
> Anything that reaches **outside the repository** is not.

Typical members: the test-report directory (`test-results/`, `playwright-report/`, `.pytest_cache/`),
coverage output, the build log directory, the runner's local binary directory (`node_modules/.bin/`,
`.venv/bin/`), and whatever path `verification.md` names for evidence. Never: the network, the package
manager's install commands, anything under `$HOME` outside the repo, production credentials.

Two consequences:

- **A skill that reads evidence says so at intake.** Allow block missing → name it once at the start
  and offer to add it, not as twenty prompts over an hour.
- **A blocked read is reported, never worked around.** Do not infer what a report probably said; say
  the read was blocked and put the settings fix in the closing «What you should do» block
  (`report-format.md`).
