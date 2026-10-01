# Quality gate (shared — build pipeline)

The **quality gate** — linter + formatter + type-checker + test-runner — is the fast, deterministic loop
run on every task; it catches the obvious in seconds, before `verify-feature`'s expensive drive/prove.
`setup-dev-environment` builds it; `implement-feature`, `verify-feature` and `build-tasks` enforce it.

## Three commands, and only one of them is automatic

| | Runs | Invoked by |
|---|---|---|
| **Static gate** (`make check-fast`) | format · lint · type-check · suppressions | **automatically** — the pre-commit hook |
| **Scoped test run** (`make test-scoped SCOPE=…`) | only the tests that belong to the work in hand | **deliberately** — the implementer's self-check and hand-off, the verifier's run, and `run-task` before the checkpoint commit |
| **Full gate** (`make check`) | the static gate **plus the whole suite** | **deliberately — in the release pipeline only**: `refactor`, `write-tests`, `cut-release` |

All three names are recorded in `.dev-skills/project-setup/verification.md`; the stack's equivalents are fine.

- **Format** — the formatter in check mode (e.g. `ruff format --check`, `prettier --check`).
- **Lint** — the linter (e.g. Ruff, ESLint).
- **Type-check** — the type-checker in strict mode (e.g. `mypy --strict`, `tsc --noEmit`).
- **Test** — the test-runner: over a **selection** in the build loop, over the **whole** suite at the
  release boundary.

Tools are the ones `design-architecture`/`design-dev-architecture` chose — executed, never re-picked.

**No test run is ever mandatory on commit.** The pre-commit hook runs the static gate only (seconds,
worth paying unasked). **Do not add any test step to the pre-commit hook** — not the suite, not a scoped
run, not a changed-files runner. The developer decides when to pay for tests; the pipeline calls the
scoped run where it asserts something.

## What "belongs to the work in hand"

The scoped selection is small and derived, not guessed:

1. **The tests written for this task** — the implementer's unit tests and, from the fix round on, the
   adversarial tests the verifier committed for this task's criteria.
2. **The tests of the modules this task changed** — from `git diff --name-only`: the tests beside those
   modules and the ones that import them (catches "my change broke the thing next door").
3. **Nothing else** — not the neighbouring feature's e2e, not the full browser suite.

`verification.md` records the selector (`pytest tests/billing -k invoice`, `vitest run src/search`,
`playwright test --grep @search`). No way to run a selection is a finding for
`setup-dev-environment`, not a reason to run everything.

## The build loop never runs the whole suite

The whole suite costs every task more as the product grows and says little about the feature in hand;
the **release pipeline** runs it:

- `refactor` runs the full gate before it starts and after every transformation;
- `write-tests` runs the full gate at the end, over the net it just extended;
- `cut-release` confirms the full gate is green before the cut.

Accepted trade-off: a regression in code the task did **not** touch surfaces at the release run, not at
that task's commit — rule 2 covers the common case, the release gate the rest.

## When the project has no scoped run yet

A repo that adopted this skill set mid-flight often has only `make check`. Never silently fall back to
running everything — it hides the gap.

- **Check at intake, once per run.** `build-tasks` (and a standalone `run-task`) confirms the scoped
  target named in `verification.md` exists and runs; not re-checked per task.
- **Missing → say so and offer the fix.** One line at the start: the target is absent, the loop pays
  for the whole suite on every hand-off until it exists, `/setup-dev-environment` adds it (or it
  becomes one `setup` task). Then proceed — the run is not blocked.
- **Present but useless → the same.** A `test-scoped` that runs the whole suite is a finding
  (`setup-dev-environment`'s smoke test proves it runs visibly fewer tests than the full one).
- **The selector finds nothing for a changed module** — a **coverage gap to report**, never a licence
  to run everything: run what was found, note the module. It is `write-tests`' input.

## The full run has a budget too

`refactor`, `write-tests` and `cut-release` each **report the `make check` wall-clock in one line**,
against the budget in `verification.md` (set at setup; **5 minutes** is a sane default for a small
product):

- over budget → a **performance finding about the suite**, filed like any other, slowest files named —
  never a reason to skip the run, never something to be patient with.
- The build loop's own budget is per task and much tighter (below).

## A test that will not reproduce is quarantined, not tolerated

A result that changes between two runs of the *same* code makes every green meaningless.

- **Confirm it before calling it flaky** — re-run the failing selection on the unchanged tree. Same
  failure twice → a real red.
- **Different result → quarantine it**: the project's skip/quarantine mechanism **plus a task id and one
  line of what was observed**, and file the task. A quarantine marker without a task id is a
  suppression, and the gate fails on those.
- **Never adjust a test to make it pass.** Red because behaviour moved is the finding; red at random is
  a test defect.
- **Never "prove" a speed-up or a fix with a single green run** of a suite known to flake.

## Prefer the cheapest level that proves the thing

Test level is a cost decision — start from the bottom:

- **Unit** — pure logic, calculation, validation, formatting, state transitions. Most criteria.
  Milliseconds.
- **Integration** — a real seam: a route writes to the database and reads it back, a rule refuses
  another user's row. Seconds.
- **End-to-end** — **the exception, not the tier you reach for**: only when the criterion is itself
  about a person's path across a running screen and cannot be proven below. Tens of seconds to minutes,
  and the flakiest thing in the suite.

Rules that follow:

- **One e2e per task at most**, only when a criterion demands it. Several e2e over one journey with
  different data is a unit test wearing a browser.
- **Push the case down.** "Empty query → 400" is a unit or integration test even when the criterion
  mentions a search box. Drive the UI only for criteria about the UI.
- **Driving the stack to *prove* a criterion is not *authoring* an e2e test** — the verifier's drive
  (`verification-method.md`) is a one-off observation, not necessarily a permanent browser test.
- **Budget: a task's scoped run should finish in about two minutes.** Past that, the selection is too
  wide or the tests are at the wrong level — say so in the task log.

## Keep tests fast — the suite is run for the rest of the product's life

**Production-grade slow primitives must be cheap under test.** Password hashing and KDFs (Argon2,
bcrypt, scrypt), artificial delays, retry backoff, rate limits are slow *by design* (weakening them in
production is a defect), so they need a configurable cheap test setting. Measured: Argon2 at OWASP
defaults made 86 auth tests take 42 s of a 95 s suite; test-cost parameters → 7.7 s, suite 33 s,
nothing dropped.

For a new test: no `sleep` where an await-for-condition works, no per-case fixture rebuild where per
file would do, no network to a service with a local stand-in. A test slow because the *product* is
slow is a performance finding.

## Zero-tolerance config

The gate must not be silently sidestepped:

- **Fail on suppressions.** A new `eslint-disable` / `# type: ignore` / `# noqa` in a diff fails the
  gate; silencing a rule needs a deliberate, human-authored override.
- **Fail on new warnings**, not only errors. Strict type-checking on (`--strict`) — it catches the
  implicit-any / untyped-dict patterns agents default to.
- **A skipped or expected-to-fail test is a suppression too.** `skip` / `xfail` / `test.fail()` added to
  pass a red run needs a task id beside it (`write-tests` sets the convention), never a bare marker.

## Where it is configured vs enforced

- **Configured by `setup-dev-environment`** (repo-local): the tool configs, all three targets, and a
  **pre-commit hook that runs the static gate** and blocks the commit on red. **Do not wire a Claude
  Code hook — Stop, PostToolUse or any other — that runs a gate when the agent finishes a turn or an
  edit:** red mid-task is *normal*, and such a hook blocks the turn over, say, a formatter warning on a
  work-in-progress file.
- **Enforced at four points, all deliberate:**
  1. `implement-feature` self-check — **static gate + the scoped run** before handing off; never hands
     off on red.
  2. `verify-feature` — runs the tests it authored for this task (plus rule 2's neighbours); they join
     the suite the release gate runs.
  3. `run-task` — **static gate + the scoped run must be green before the checkpoint commit**; red
     routes the task back to `implement-feature` (counts as the one fix round) or to `needs_human`.
     Never committed red.
  4. The **release pipeline** — the full gate over the whole suite, at the three points above. The only
     place the whole suite is mandatory.

## Make failures actionable

A failure message carries the finding, file, line, and a one-line remedy, so an agent fixes most issues
alone — unactionable messages, not strictness, are what kill throughput.

## Greenfield caution

Zero-tolerance from day one, but introduce strictness **deliberately for the chosen stack** and keep
messages actionable — or the implement↔verify loop stalls on style churn instead of converging on
behavior.
