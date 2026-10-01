---
name: audit-tests
description: "Audit the test suite against its runtime budgets — routine run ≤30 s with no e2e, ≤10 e2e total behind a release-time target, full suite ≤5 min — and take the cost out: measure, find per-test setup, sleeps, production-cost primitives, duplicates, quarantine rot; apply edits after your yes (or with autopilot), re-measure. Use periodically or via optimize-dev."
argument-hint: "[autopilot]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/tests/*' '*/test/*' '*/__tests__/*' '*test*' '*spec*' '*/e2e/*' '*playwright.config.*' '*vitest.config.*' '*jest.config.*' '*pytest.ini' '*pyproject.toml' '*conftest.py' '*/tsconfig*.json' '*Makefile' '*justfile' '*/package.json' '*/.github/workflows/*' '*/.gitlab-ci.yml' '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Audit Tests Skill

You are the suite's economist: like `audit-performance` for the product, **measure against a budget,
reproduce the cost, take it out** — never weakening what the suite proves. `write-tests` closes what
is *missing*; you cut what the net *costs*.

Tier model and speed rules you enforce, not reinvent: **`../_shared/build-pipeline/quality-gate.md`**
("Prefer the cheapest level", "Keep tests fast", the flake-quarantine rule). Optimization patterns and
per-stack run-splitting recipes: **`references/optimization-catalogue.md`**.

## The budgets

Read from `.dev-skills/project-setup/verification.md` → `## Test budgets`; absent → write the section
with these defaults, so they become project policy:

| Budget | Default |
|---|---|
| **Routine run** — wall-clock | **≤ 30 s** |
| **e2e tests inside the routine run** | **0** |
| **e2e tests, total count** | **≤ 10**, one per journey |
| Full suite (`make check` equivalent) — wall-clock | ≤ 5 min (`quality-gate.md`) |

**Routine run** = every entry point that runs tests *without a deliberate release-time decision*: the
default test script (`npm test`, `make test`, bare `pytest`), watch mode, any git-hook test step
(forbidden outright by `quality-gate.md` — a finding, not budget math), the per-commit/PR CI job, the
build loop's scoped run. **e2e runs only deliberately**: the explicit e2e target at release (inside
the full gate), or **exactly one** e2e scoped to the flow being changed (the build loop's "one e2e per
task" exception).

## Inputs and outputs

- **Reads:** test tree and configs; run entry points (scripts, Makefile/justfile, git hooks, CI
  workflows); `verification.md`; `.dev-skills/project-spec/code-style.md` → `## Testing` if present;
  the runners' timing output.
- **Writes:** tests and fixtures; harness config; run entry points (scripts, Makefile, CI) — that is
  what makes the budgets real; `## Test budgets`; `.dev-skills/optimize/test-audit.md`; rework tasks
  for product-caused slowness via `plan-development` amend, under the shared 15-open ceiling
  (**`../_shared/build-pipeline/planning-method.md`**). **Never product code** (hook-enforced).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths or metric names. Commit messages are always English.
**One branch — the current one** (normally `main`): never branch, switch or open a worktree unless the
user explicitly asked in this session — **`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — runners, configs, every entry point that fires tests automatically; budgets
- [ ] Stage 1: Measure — time the routine run and the full suite per file; inventory the e2e tests and the quarantine markers
- [ ] Stage 2: Findings — over-budget runs, e2e in the routine path, repeated setup, sleeps, duplicates, quarantine rot
- [ ] Stage 3: Plan + confirm — numbered edits, each with its expected saving; autopilot = upfront yes
- [ ] Stage 4: Apply + prove — edit, re-run green, re-measure; before/after table that reconciles
- [ ] Stage 5: Record — .dev-skills/optimize/test-audit.md + «What you should do»
```

### Stage 0: Intake
Determine **from the project, not habit**: runners and levels, where tests live, and **every entry
point that runs them automatically** (default scripts, watch configs, git hooks, each CI trigger). Read
`verification.md` (commands, budgets) and `.build-config.md` for `mode` if present; the **`autopilot`
argument** governs the Stage 3 gate. State what you found in three lines — commands, counts, automatic
entry points — so the human can correct you.

### Stage 1: Measure
Run the routine command and the full suite with **per-file (per-test where cheap) wall-clock** from the
runner's own reporter (`pytest --durations`, vitest/jest reporters, the Playwright report — recipes in
the catalogue); none → time the run whole and bisect. Count tests per level. Inventory
every e2e: file · journey · seconds. Confirm a suspect flake by re-running the same selection on the
unchanged tree before claiming it (`quality-gate.md`).

**Inventory the quarantine** — every disabled-test marker (`skip`, `xfail`, `test.fail()`, `it.skip`,
`@pytest.mark.skip`, the stack's equivalents), with four facts: a **task id** beside it?; does the task
**still exist, in what status**; **age** (`git blame` on the marker line); **surface covered**, ranked
as `write-tests` ranks risk (money → access/ownership → deletion → external effects).

### Stage 2: Findings
Rank by damage, most first:

- **(a) e2e in the routine path, or more than 10 e2e** — hurts every commit.
- **(b) Routine run over 30 s** — the slowest files and their *cause*, not just the time.
- **(c) Per-test setup that could run once** — DB, server, browser context, seed data, temp project
  rebuilt per test where one per file/session plus namespacing or transaction rollback would do.
  Usually the largest win (catalogue).
- **(d) Production-cost primitives at production settings** — KDFs, retries, backoff, rate limits,
  timers (`quality-gate.md`'s Argon2 case: 42 s → 7.7 s, nothing dropped).
- **(e) Flat waits and real networks** — `sleep` where await-a-condition works; live calls where the
  project's own mocks exist.
- **(f) Duplicate and demotable coverage** — several e2e walking one journey with different data, the
  same behaviour asserted twice, tests that cannot fail. Prune candidates.
- **(g) Quarantine rot** — a marker whose task is **done** (may pass, nobody re-enabled it); whose task
  is **gone or abandoned** (coverage lost, no plan back); a **bare marker with no task id**; a
  **long-lived quarantine on a risk surface** (money/access — rank it with (a), whatever its age).
- **(h) Product-slow, not test-slow** — an endpoint that takes 8 s takes 8 s in every test: file a
  rework task, never patch it here.

### Stage 3: Plan + confirm
One numbered plan: each edit's files, expected saving in seconds and risk; run reconfiguration stated
explicitly — **which commands exist afterwards and what each runs** (e.g. "`npm test` =
unit+integration, ~22 s; `npm run test:e2e` = 8 journeys, release only; CI PR job loses the e2e
step"). Deletions get their own labelled section. It deletes tests and rewires entry points: **wait for
the explicit yes in both config modes**, unless the explicit **`autopilot` argument** was given — then
apply without pausing, logging each item as a fork decision in the report. Apply nothing outside the
plan.

### Stage 4: Apply + prove
Edit tests, fixtures, harness config, entry points. Then prove, in order: the **full suite is as green
as before** (a pre-existing red stays red and present — a finding, not your cleanup); every moved or
merged test **still asserts what it did** (Rule 2); **re-measure** the routine run and the full suite.
Lift a quarantine marker only through its test: re-run it without the marker — green **twice** →
remove the marker; red → it stays and the task is reopened or re-filed with what you saw. One
before/after table — counts per level, wall-clock per command — that reconciles. Budget still missed →
what remains, why (usually a filed product-slowness task), the honest number reached.

### Stage 5: Record
Write `.dev-skills/optimize/test-audit.md`: budgets vs measured (before/after), the e2e inventory with
journeys, the quarantine inventory with each marker's verdict (lifted · stays with a live task ·
finding), what each entry point now runs, the applied plan, the prune list, filed tasks, what was left
and why. End with «What you should do».

## Rules

1. **Measure, don't guess** — every finding carries a number; every applied change is re-measured.
2. **Optimization never weakens proof** — no assertion removed or loosened to meet a budget; a test is
   deleted only as a listed prune (duplicate, demotable, cannot fail), proposed, never silent.
3. **A failing test is never deleted, skipped or quarantined to meet a budget** — red is a finding with
   a task id; a flake is quarantined only per `quality-gate.md`, task id attached. Every marker needs a
   live task id; never lift one on a closed task alone; a dead-task or bare marker is a finding, never
   silently tidied.
4. **Never edit product code**; product slowness is a rework task, one per coherent cause.
5. **Sharing must not couple tests** — a shared resource is read-only or namespaced per test;
   order-dependence it introduces is a defect.
6. **Install nothing** — no timing reporter means time-and-bisect; tooling is `setup-dev-environment`'s.
7. **Confirmation is the default in both modes**; every `autopilot`-applied item is still logged.
8. **Budgets live in `verification.md`** (30 s / 0 routine e2e / ≤10 e2e, one per journey / 5 min) —
   write them when absent so the next audit measures against the same contract.
9. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
