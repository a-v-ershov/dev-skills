# Quality gate (shared — build pipeline)

The **quality gate** is the fast, deterministic feedback loop the build pipeline runs on every task:
linter + formatter + type-checker + test-runner. It is the cheap layer that catches the obvious in
seconds — before the expensive, adversarial `verify-feature` drive/prove runs.

This doc defines the gate once. `setup-dev-environment` builds it; `implement-feature`, `verify-feature`
and `build-tasks` enforce it. They reference this file rather than restating the rule.

## Three commands, and only one of them is automatic

They differ in **who asks for the run** and in **how much of the suite it costs**:

| | Runs | Invoked by |
|---|---|---|
| **Static gate** (`make check-fast`) | format · lint · type-check · suppressions | **automatically** — the pre-commit hook |
| **Scoped test run** (`make test-scoped SCOPE=…`) | only the tests that belong to the work in hand | **deliberately** — the implementer's self-check and hand-off, the verifier's run, and `run-task` before the checkpoint commit |
| **Full gate** (`make check`) | the static gate **plus the whole suite** | **deliberately — in the release pipeline only**: `refactor`, `write-tests`, `cut-release` |

All three names are recorded in `.dev-skills/project-setup/verification.md`; the stack's equivalents are fine.

- **Format** — the formatter in check mode (e.g. `ruff format --check`, `prettier --check`).
- **Lint** — the linter (e.g. Ruff, ESLint).
- **Type-check** — the type-checker in strict mode (e.g. `mypy --strict`, `tsc --noEmit`).
- **Test** — the test-runner: over a **selection** in the build loop, over the **whole** accumulated
  suite at the release boundary.

The concrete tools come from the stack `design-architecture`/`design-dev-architecture` already chose —
the gate **executes** that decision, it does not re-pick tools.

**No test run is ever mandatory on commit.** The pre-commit hook runs the static gate and nothing
heavier: a compiler-shaped check costs seconds and is worth paying without being asked, a test run is
not. The developer decides when to pay for one — and the pipeline decides for itself, by calling the
scoped run at the points above, which are the points where something is actually being asserted.
**Do not add any test step to the pre-commit hook** — not the suite, not a scoped run, not a
changed-files runner. The scoped run belongs to the skills that assert something with it, never to a
hook that fires on every commit.

## What "belongs to the work in hand"

The scoped selection for a task is small, and it is derived, not guessed:

1. **The tests written for this task** — the implementer's own unit tests and, from the fix round on,
   the adversarial tests the verifier committed for this task's acceptance criteria.
2. **The tests of the modules this task changed** — read the diff (`git diff --name-only`), then run
   the tests that live beside those modules and the ones that import them. This is what catches "my
   change broke the thing next door" without paying for the whole suite.
3. **Nothing else.** Not the neighbouring feature's e2e run, not the full browser suite, not "while
   we're here".

`verification.md` records the concrete selector for the stack (`pytest tests/billing -k invoice`,
`vitest run src/search`, `playwright test --grep @search`). If a project has no way to run a
selection, that is a finding for `setup-dev-environment`, not a reason to run everything.

## The build loop never runs the whole suite

A full run is charged to **every** task, it grows with the product, and by the tenth task it is the
single largest cost in the loop while telling the implementer almost nothing about the feature it is
building. So the build loop pays for the selection, and the **release pipeline** — where the question
genuinely is "does all of this still work together?" — pays for the whole thing:

- `refactor` runs the full gate before it starts and after every transformation (behaviour must be
  provably unchanged — that is its entire safety net);
- `write-tests` runs the full gate at the end, over the net it just extended;
- `cut-release` confirms the full gate is green before the cut.

What this trades away, stated plainly: a regression that a task introduces in code it did **not**
touch is not caught at that task's commit — it surfaces at the release run. That is accepted
deliberately. Selection rule 2 (the tests of the changed modules) covers the common case, the release
gate covers the rest, and the alternative — a full suite on every hand-off, every verification and
every commit — is what makes agents start working around the gate.

## When the project has no scoped run yet

The three targets are `setup-dev-environment`'s output, so a repo that adopted this skill set
mid-flight usually has `make check` and nothing else. The loop must not silently fall back to running
everything — that is precisely the cost this design exists to avoid, and it hides the gap forever.

- **Check at intake, once per run.** `build-tasks` (and a standalone `run-task`) confirms that the
  scoped target named in `verification.md` exists and runs. It does not check again per task.
- **Missing → say so and offer the fix.** One line, at the start: the target is absent, the loop will
  pay for the whole suite on every hand-off until it exists, and `/setup-dev-environment` adds it (or
  it becomes one `setup` task). Then proceed — the run is not blocked on it.
- **Present but useless → the same treatment.** A `test-scoped` that runs the whole suite anyway is a
  finding, not a selection. `setup-dev-environment`'s smoke test is supposed to catch this by proving
  the scoped run executes visibly fewer tests than the full one.
- **The selector finds nothing for a changed module** — no test lives beside it and no tag matches.
  That is a **coverage gap to report**, never a licence to run everything: run what the selection did
  find, and note the module the loop could not select for. It is `write-tests`' input.

## The full run has a budget too

`refactor`, `write-tests` and `cut-release` run `make check` over the whole suite, and each of them
**reports that run's wall-clock in one line**. Compare it against the budget recorded in
`verification.md` (set it at setup; **5 minutes** is a sane default for a small product):

- over budget → a **performance finding about the suite**, filed like any other, with the slowest
  files named. It is not a reason to skip the run, and it is not something to be patient with
  release after release. A suite nobody can afford is a suite that stops being run.
- The build loop's own budget is per task and much tighter (below).

## A test that will not reproduce is quarantined, not tolerated

A test whose result changes between two runs of the *same* code is worse than no test: it makes every
green meaningless and every red a coin-toss. Measured in the field, one suite produced two different
second failures on two consecutive runs of one commit, and every "this made it green" claim after that
was unfalsifiable.

- **Confirm it before calling it flaky** — re-run the failing selection on the unchanged tree. Same
  failure twice → it is a real red, treat it as one.
- **Different result → quarantine it**: mark it with the project's skip/quarantine mechanism **plus a
  task id and one line of what was observed**, so it stops gating the loop, and file the task. A
  quarantine marker without a task id is a suppression, and the gate fails on those.
- **Never adjust a test to make it pass.** A test that is red because the behaviour moved is the
  finding; a test that is red at random is a defect in the test.
- **Never "prove" a speed-up or a fix with a single green run** of a suite known to flake.

## Prefer the cheapest level that proves the thing

Test level is a cost decision, and the default runs from the bottom:

- **Unit** — pure logic, calculation, validation, formatting, a state machine's transitions. This is
  where most criteria are proven. Milliseconds.
- **Integration** — a real seam: a route writes to the database and reads it back, a rule refuses
  another user's row, a repeat does not charge twice. Seconds.
- **End-to-end** — **the exception, not the tier you reach for.** Justified only when the criterion is
  itself about a person's path across a running screen and cannot be proven below. Tens of seconds to
  minutes, and it is the flakiest thing in the suite.

Rules of thumb that follow from that:

- **One e2e per task at most**, and only when a criterion demands it. Several e2e tests covering the
  same journey with different data is a unit test wearing a browser.
- **Push the case down.** "Empty query → 400" is a unit or integration test even when the criterion
  was written about a search box. Drive the UI for the criteria that are about the UI.
- **Driving the stack to *prove* a criterion is not the same as *authoring* an e2e test.** The
  verifier drives the running product to observe a real outcome (`verification-method.md`) — that is
  a one-off observation, not necessarily a permanent browser test.
- **Budget: a task's scoped run should finish in about two minutes.** Past that, the selection is too
  wide or the tests are at the wrong level — say so in the task log rather than quietly waiting.

## Keep tests fast — the suite is run for the rest of the product's life

**Production-grade slow primitives must be cheap under test.** Password hashing and KDFs (Argon2,
bcrypt, scrypt), artificial delays, retry backoff, deliberate rate limits — these are slow *by
design*, that is their whole job in production, and weakening them there is a defect. Under test they
need a configurable cheap setting, or a handful of feature tests quietly dominate the entire run.
Measured case: Argon2 at OWASP defaults costs ~32 ms per operation, which made 86 auth tests take 42 s
of a 95 s suite; the same tests with test-cost parameters took 7.7 s and the whole 1006-test suite
dropped to 33 s — with nothing dropped from it.

The same discipline applies to what a new test does: no `sleep` where an await-for-condition works,
no fixture that rebuilds the world per test case when it could be built per file, no network to a
service that has a local stand-in. A test that is slow because the *product* is slow is a performance
finding, not a test to be patient with.

## Zero-tolerance config

The gate is only effective for AI-written code if it cannot be silently sidestepped:

- **Fail on suppressions.** A new `eslint-disable` / `# type: ignore` / `# noqa` in a diff fails the
  gate; silencing a rule requires a deliberate, human-authored override, never a drive-by comment.
- **Fail on new warnings**, not only errors. Strict type-checking on (`--strict`) — it catches the
  implicit-any / untyped-dict patterns agents default to when unsure of a contract.
- **A skipped or expected-to-fail test is a suppression too.** `skip` / `xfail` / `test.fail()` added
  to get past a red run needs a task id beside it (`write-tests` sets that convention), never a bare
  marker.

## Where it is configured vs enforced

- **Configured by `setup-dev-environment`** (repo-local, so auto-applicable): the tool configs, all
  three targets, and a **pre-commit hook that runs the static gate** and blocks the commit on red.
  **Do not wire a Claude Code hook — Stop, PostToolUse or any other — that runs a gate when the agent
  finishes a turn or an edit.** A gate that is red mid-task is the *normal* state halfway through
  building something: the hook then blocks the turn and forces a polling loop around it. Measured
  case: a Stop hook running the full gate killed a turn over a **formatter warning** on a
  work-in-progress file, and the agent spent the turn on whitespace instead of the task. The gate
  belongs where it decides something — the pre-commit hook, the implementer's hand-off, and the
  verifier's run — and nowhere that merely notices the agent stopped typing.
- **Enforced at four points, all of them deliberate:**
  1. `implement-feature` self-check — the **static gate + the scoped run** before handing off; does
     not hand off on red.
  2. `verify-feature` — runs the tests it authored for this task (plus rule 2's neighbours); its tests
     join the suite the release gate runs.
  3. `run-task` — the **static gate + the scoped run must be green before the checkpoint commit**; red
     routes the task back to `implement-feature` (counts as the one fix round) or to `needs_human`. It
     is never committed red.
  4. The **release pipeline** — the full gate, over the whole suite, at the three points listed above.
     This is the only place the whole suite is mandatory.

## Make failures actionable

When the gate fails, the message must carry the specific finding, file, line, and a one-line remedy —
a coding agent loops back on a structured failure message and fixes most issues without a human. The
throughput failure mode is not "the gate is too strict", it is "the gate's messages are not actionable".

## Greenfield caution

On a fresh project, zero-tolerance from day one is correct, but introduce strictness **deliberately for
the chosen stack** and keep the messages actionable — otherwise the implement↔verify loop stalls on a
churn of style fixes instead of converging on behavior.
