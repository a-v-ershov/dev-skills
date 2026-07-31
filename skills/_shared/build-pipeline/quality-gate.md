# Quality gate (shared — build pipeline)

The **quality gate** is the fast, deterministic feedback loop the build pipeline runs on every task:
linter + formatter + type-checker + test-runner. It is the cheap layer that catches the obvious in
seconds — before the expensive, adversarial `verify-feature` drive/prove runs — and the **accumulating
test suite is the regression net** that keeps a later task from silently breaking an earlier one.

This doc defines the gate once. `setup-dev-environment` builds it; `implement-feature`, `verify-feature`
and `build-tasks` enforce it. They reference this file rather than restating the rule.

## Two commands, and only one of them is automatic

The two differ in **who asks for the run**, and that is the whole distinction:

| | Runs | Invoked by |
|---|---|---|
| **Static gate** (`make check-fast`) | format · lint · type-check · suppressions | **automatically** — the pre-commit hook |
| **Full gate** (`make check`) | the static gate **plus** the test suite | **deliberately** — the implementer's hand-off, the verifier's run, and `build-tasks` before the checkpoint commit |

Both names are recorded in `.dev-skills/project-setup/verification.md`; the stack's equivalents are fine.

- **Format** — the formatter in check mode (e.g. `ruff format --check`, `prettier --check`).
- **Lint** — the linter (e.g. Ruff, ESLint).
- **Type-check** — the type-checker in strict mode (e.g. `mypy --strict`, `tsc --noEmit`).
- **Test** — the test-runner over the accumulated suite (e.g. `pytest`, `vitest`), whole, as the
  regression pass. **Full gate only.**

The concrete tools come from the stack `design-architecture`/`design-dev-architecture` already chose —
the gate **executes** that decision, it does not re-pick tools.

**No test run is ever mandatory on commit.** The pre-commit hook runs the static gate and nothing
heavier: a compiler-shaped check costs seconds and is worth paying without being asked, a test suite
is not, and it grows. The developer decides when to pay for a run — and the pipeline decides for
itself, by calling the full gate at the three points above, which are the points where something is
actually being asserted. **Do not add a test step to the pre-commit hook**, and do not smuggle one in
under another name (a "quick subset", a changed-files runner, a wrapper target that shells out to the
suite). If a project wants tests on commit, that is the project's own hook to write, not this
contract's to mandate.

## Keep the gate cheap — it is run hundreds of times

Every hand-off, every verification and every commit pays for the suite, so its cost is charged to
every future task. A gate that grows slower is a gate agents start working around.

**Production-grade slow primitives must be cheap under test.** Password hashing and KDFs (Argon2,
bcrypt, scrypt), artificial delays, retry backoff, deliberate rate limits — these are slow *by
design*, that is their whole job in production, and weakening them there is a defect. Under test they
need a configurable cheap setting, or a handful of feature tests quietly dominate the entire run.
Measured case: Argon2 at OWASP defaults costs ~32 ms per operation, which made 86 auth tests take 42 s
of a 95 s suite; the same tests with test-cost parameters took 7.7 s and the whole 1006-test suite
dropped to 33 s — with nothing dropped from it.

Reach for that **before** trimming what the suite runs. Selecting "only the tests related to this
change" is the tempting fix and usually the wrong one: it gives up the regression net precisely where
a task is most likely to break an earlier one, and the tests of the feature being built are typically
the slow ones anyway.

## Zero-tolerance config

The gate is only effective for AI-written code if it cannot be silently sidestepped:

- **Fail on suppressions.** A new `eslint-disable` / `# type: ignore` / `# noqa` in a diff fails the
  gate; silencing a rule requires a deliberate, human-authored override, never a drive-by comment.
- **Fail on new warnings**, not only errors. Strict type-checking on (`--strict`) — it catches the
  implicit-any / untyped-dict patterns agents default to when unsure of a contract.

## Where it is configured vs enforced

- **Configured by `setup-dev-environment`** (repo-local, so auto-applicable): the tool configs, both
  targets, and a **pre-commit hook that runs the static gate** and blocks the commit on red.
  **Do not wire a Claude Code hook — Stop, PostToolUse or any other — that runs a gate when the agent
  finishes a turn or an edit.** A gate that is red mid-task is the *normal* state halfway through
  building something: the hook then blocks the turn and forces a polling loop around it. Measured
  case: a Stop hook running the full gate killed a turn over a **formatter warning** on a
  work-in-progress file, and the agent spent the turn on whitespace instead of the task. The gate
  belongs where it decides something — the pre-commit hook, the implementer's hand-off, and the
  verifier's run — and nowhere that merely notices the agent stopped typing.
- **Enforced at three points, all of them deliberate:**
  1. `implement-feature` self-check — runs the **full gate** before handing off; does not hand off on red.
  2. `verify-feature` — its authored tests become part of the suite the full gate runs.
  3. `build-tasks` — the **full gate must be green before the checkpoint commit**; a red gate routes
     the task back to `implement-feature` (counts as a round), it is never committed red. This is the
     pipeline choosing to run the suite, not a hook imposing it — and it is the *only* place the
     suite is mandatory, which is why the pre-commit hook does not need to repeat it.

## Make failures actionable

When the gate fails, the message must carry the specific finding, file, line, and a one-line remedy —
a coding agent loops back on a structured failure message and fixes most issues without a human. The
throughput failure mode is not "the gate is too strict", it is "the gate's messages are not actionable".

## Greenfield caution

On a fresh project, zero-tolerance from day one is correct, but introduce strictness **deliberately for
the chosen stack** and keep the messages actionable — otherwise the implement↔verify loop stalls on a
churn of style fixes instead of converging on behavior.
