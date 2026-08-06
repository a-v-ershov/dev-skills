# Environment access (shared — build pipeline)

The local dev environment is a **single stateful resource** — the running stack, the bound ports, the
local DB, the seed state. More than one actor can reach for it (a second `build-tasks` run, a
standalone skill, a human at the keyboard), so access must be **coordinated or isolated**, or the
actors clobber each other. `design-dev-architecture` chooses, per stack, between two complementary
mechanisms; `setup-dev-environment` implements whichever; `build-tasks` holds the lease across a task.

## Two mechanisms (chosen per stack)

### 1. Advisory lock — for a single shared stack
When the local env is one heavy shared stack (Docker Compose, a real local DB, fixed ports):

- **Lock file** — a **gitignored** runtime file (e.g. `.dev/env.lock`), never committed. (This is the
  build pipeline's one transient runtime file — gitignore it.) It holds: holder id (task id / session /
  `human`), pid, `acquired_at`, `heartbeat_at`, action.
- **Baked into the entrypoint** — the bring-up command acquires (`make dev` → acquire, then start) and
  teardown releases (`make down` → stop, then release). You can't forget it: it's the same command
  everyone runs.
- **Lease + stale reclaim** — the holder re-stamps `heartbeat_at`; a lock whose heartbeat is older than
  the TTL (e.g. 10 min) is presumed abandoned (agents get killed) and any actor may reclaim it. Without
  this, a killed holder deadlocks the env forever.
- **Escape hatch** — `make env-unlock` force-clears a stuck lock for a human.
- **Contended** — if the lock is held and fresh, wait (bounded) or refuse with a clear message naming
  the holder and since when.

### 2. Per-run isolation — where it's cheap
When a run can be namespaced cheaply, isolate instead of locking — then no lock is needed and runs can
go in parallel:

- An **ephemeral data dir** per run (`--data-dir <tmp>`), a **unique compose project name**
  (`COMPOSE_PROJECT_NAME=app-<id>`) + a **port offset**, or a separate DB schema per run.
- Best for the cheap, process-local **developer/test scripts** — they carry their own state and don't
  touch the shared stack.

A stack often uses **both**: the lock guards the one heavy shared stack; the fast dev scripts isolate
per run and skip the lock.

## Who coordinates

- **`build-tasks`** holds the lease for a task's span (implement → verify → gate), releases it after
  the checkpoint commit, and **reclaims a stale lock** left by its own killed run on resume. Its
  subagents inherit the held lease (same holder id → the entrypoint sees the lock is already theirs and
  proceeds).
- **Standalone** runs of `implement-feature` / `verify-feature` / `setup-dev-environment` acquire and
  release the env themselves.
- The concrete commands and which mechanism applies are recorded in `.dev-skills/project-setup/verification.md`.

## Permissions the loop needs

The verification loop reads its own output constantly — the test runner's report directory, the
coverage output, the evidence files a verifier writes, the local binaries it invokes. When each of
those reads raises a permission prompt, an autonomous run stops being autonomous: measured in one
project, a single build phase collected 27 classifier denials and 18 blocked directory reads, almost
all of them the agent trying to read `test-results/` after a failing run and then reasoning without the
error it had just produced.

`setup-dev-environment` writes a committed **allow** block into `.claude/settings.json` covering the
harness's own artefacts, alongside the `permissions.deny` list that keeps generated trees out of
navigation. What belongs in it is derived from the stack, not from a fixed list — the rule is:

> Anything **this project's own tooling writes** and the agent is expected to read back is allowed.
> Anything that reaches **outside the repository** is not.

Typical members: the test-report directory (`test-results/`, `playwright-report/`, `.pytest_cache/`),
the coverage output, the build log directory, the local binary directory the runner uses
(`node_modules/.bin/`, `.venv/bin/`), and whatever path `verification.md` names for evidence. Never in
it: the network, the package manager's install commands, anything under `$HOME` outside the repo,
production credentials.

Two consequences for the rest of the pipeline:

- **A skill that reads evidence says so at intake.** If the allow block is missing, name it once, at
  the start of the run, and offer to add it — do not discover it as twenty prompts spread across an
  hour of work.
- **A blocked read is reported, never worked around.** Do not infer what a report probably said. Say
  the read was blocked, and put the settings fix in the closing «What you should do» block
  (`report-format.md`).
