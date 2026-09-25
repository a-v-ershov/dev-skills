# Test-optimization catalogue (audit-tests)

Concrete patterns for taking cost out of a suite without weakening what it proves. Each entry: when it
applies, how to do it, and the risk that turns it from an optimization into a defect. Ordered roughly
by how often it is the biggest win.

## 1. Create the expensive resource once, not per test

The classic shape: a database, a server process, a browser context, a seeded dataset, or a temp
project rebuilt in every test's setup, when the tests only need it to *exist*.

- **Widen the fixture scope** — per-file or per-session instead of per-test: pytest
  `scope="session"`/`"module"` fixtures; vitest/jest `beforeAll` instead of `beforeEach`; Playwright
  reusing one `browser` and cheap per-test `context`s (contexts are milliseconds; browsers are
  seconds).
- **Template database** — create and migrate one database once, then stamp cheap copies per file/run
  (`CREATE DATABASE t TEMPLATE tmpl` in Postgres; file-copy for SQLite). Migration cost is paid once.
- **Transaction rollback per test** — open a transaction in setup, roll back in teardown; each test
  sees a clean state at near-zero cost. Standard in Django/Rails/SQLAlchemy test bases. Does not work
  for code that itself commits or uses multiple connections — those few tests keep a real reset.
- **Seed once, share read-only** — a canonical seeded dataset built once per session; tests that only
  read share it as-is.
- **Namespace what tests mutate** — when tests must write to a shared resource, each writes under its
  own unique prefix/id (worker id + test name) instead of resetting the world.

**Risk — coupling.** Shared state must be read-only or namespaced; the moment test B sees test A's
writes, the suite is order-dependent and every green is suspect. After any sharing change, run the
affected files alone and in a shuffled order once to prove independence.

## 2. Test-cost settings for slow-by-design primitives

Password hashing and KDFs (Argon2/bcrypt/scrypt), retry backoff, rate limits, deliberate delays are
slow in production *on purpose* — and must stay so there. Under test, inject a cheap setting: minimum
hash rounds, zero backoff, tight timeouts, fake timers for anything scheduled. Wire it through config,
never by weakening the production default. `quality-gate.md` carries the measured case: 86 auth tests
at OWASP Argon2 cost took 42 s of a 95 s suite; with test-cost parameters, 7.7 s — nothing dropped.

**Risk:** keep at least one (marked, release-time) test that exercises the production setting, so the
real configuration is still proven to work.

## 3. Kill flat waits and real networks

- `sleep(n)` → await a condition: poll with deadline, wait for an event/selector/log line, or use the
  runner's fake timers. A flat sleep is always either too long (paid every run) or too short (flaky).
- Live HTTP to services that have a local stand-in → the project's own mocks/fakes. Paid APIs never
  run live in tests (`write-tests` rule).
- DNS/TLS/retry stalls in error-path tests → point at a closed local port with a tight timeout, not a
  real unreachable host.

## 4. Push e2e down to the cheapest proving level

An e2e test earns its cost only when the *journey itself* — a person's path across a running screen —
is the thing proven. Everything else demotes:

| e2e test that… | becomes |
|---|---|
| walks one journey with different data per test | **one** e2e for the journey + unit/integration tests for the data cases |
| asserts a validation message / boundary / error code | a unit or integration test on the rule |
| checks an API contract through the UI | an integration test on the route |
| exists to reach one deep screen's logic | a component/integration test with seeded state |

Choosing which ≤10 journeys keep an e2e: rank by risk the way `write-tests` ranks gaps — money →
sign-in/access/ownership → deletion → external effects → the product's primary create-and-share path.
A journey that no longer makes the cut is demoted, not silently dropped: its assertions land at the
lower level first.

## 5. Split the run tiers — make the budget structural

The 30-second routine budget survives only if the entry points enforce it. Target state: the default
command runs unit+integration only; e2e lives behind its own explicit target; CI runs the routine job
per PR and the e2e job only on release events or manual dispatch.

- **npm**: `"test": "vitest run"`, `"test:e2e": "playwright test"` — and `test` must not call
  `test:e2e`. Keep Playwright specs out of vitest's `include` globs (separate directory `e2e/`).
- **Makefile**: `test` (routine) · `test-e2e` · `check` = static gate + full suite + e2e (release
  gate). Names as recorded in `verification.md`.
- **pytest**: mark e2e (`@pytest.mark.e2e`), set `addopts = -m "not e2e"` in config so the bare run
  excludes them; the explicit target runs `-m e2e`.
- **Playwright flow scoping**: tag specs (`@checkout`) so the one flow-under-change test is
  `playwright test --grep @checkout` — the "one e2e while changing this flow" exception.
- **CI**: the PR workflow runs the routine command only; e2e runs on tag/release or
  `workflow_dispatch`. Removing an e2e step from the PR job is an explicit plan item, never a quiet
  edit.
- **Git hooks**: any test step found in a pre-commit/pre-push hook is removed per `quality-gate.md`
  (the static gate is the only automatic hook work) — cite that file in the plan item.

## 6. Parallelize last

Workers (`pytest-xdist`, vitest/jest workers, Playwright workers) multiply throughput **only after**
tests are independent (pattern 1's risk handled). Parallelizing coupled tests converts slowness into
flakes — a strictly worse suite. Use as the finisher, not the first move; if a runner's parallel mode
is not installed/configured, record the opportunity for `setup-dev-environment` — install nothing.

## 7. Measuring — per-runner timing

- `pytest --durations=25 --durations-min=0.1` — slowest tests + setup/teardown split.
- vitest: `--reporter=verbose` prints per-test ms; the JSON reporter for machine-readable.
- jest: `--verbose` per-test ms; `--detectOpenHandles` for the "why does it hang 5 s at the end".
- Playwright: the HTML/JSON report carries per-test duration; sort it.
- go: `go test -v` prints per-test; `-json` for tooling. Rust: `cargo test -- -Z unstable-options
  --report-time` or nextest.
- **No reporter available?** Time the whole run (`time <cmd>`), then bisect by directory/file with the
  runner's path selection. Never install a tool for this — time-and-bisect always works.

Always measure wall-clock on the same machine state before and after, same command, and quote both
numbers; a single lucky run of a known-flaky suite proves nothing (`quality-gate.md`).
