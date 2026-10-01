---
name: write-tests
description: "Map where the product lacks an honest test (flows, acceptance criteria, risk surfaces; mutation testing for hollow ones), rank gaps by risk, close the top ones red-first. Never edits product code: a real bug becomes a rework task, its test left red. Run by release-product after refactor, or standalone. Writes .dev-skills/release/test-gaps.md."
argument-hint: "[<feature / flow / task-id> | empty = whole product]"
---

# Write Tests Skill

You **map where the product is not protected by a test**, then **close the top gaps with tests that
can actually fail**. `verify-feature` proves one task as built; you sweep the whole product afterwards
for what nobody proved. **You never edit product code**: a real bug becomes a **rework task** and the
test stays **red**.

## Inputs and outputs

- **Reads:** `.dev-skills/project-spec/user-flows.research.md` (flows, states);
  `.dev-skills/build-plan/tasks/` (acceptance criteria); `.dev-skills/project-setup/verification.md`
  (run, drive, seed, prove); `.dev-skills/project-spec/code-style.md` → `## Testing` when present; the
  existing tests.
- **Writes:** test files; `.dev-skills/release/test-gaps.md` (map + what was closed); rework tasks for
  bugs found (via `plan-development` amend).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — scope (whole product, or one feature/flow/task); how this project tests, and at which levels
- [ ] Stage 1: What SHOULD be covered — flows + their states, acceptance criteria, the always-count risk surfaces
- [ ] Stage 2: What IS covered — read the tests by content; mutation-test the critical modules to expose hollow ones
- [ ] Stage 3: Gaps — three kinds, ranked by risk → .dev-skills/release/test-gaps.md
- [ ] Stage 4: Write the top gaps — delegated in batches; level chosen deliberately, style from the neighbours, hostile cases always
- [ ] Stage 4b: Prune — duplicate coverage, tests that cannot fail, e2e a unit proves; proposed, never silent
- [ ] Stage 5: RED-FIRST — prove each new test goes red on the behaviour it claims to check
- [ ] Stage 6: Triage the red — my test's fault → fix the test · a real bug → rework task, test stays red
- [ ] Stage 7: Full gate + record — what was closed, what is red and why, which tasks were filed
```

### Stage 0: Intake
An argument (feature, flow, task id) narrows everything; empty = whole product. Determine **from the
project, not habit** which test levels exist, with what tools, where tests live and the one command
that runs them all; state it in one line so the human can correct you.

### Stage 1: What should be covered
- **Every flow and every state it names** — empty, loading, validation error, permission denial,
  boundary.
- **Every acceptance criterion** — each given / when / then proven by something.
- **The risk surfaces, always, whatever the spec says**: money and payments · sign-in, access and
  ownership of others' data · deletion · external side effects · idempotency (a repeat must not do the
  work twice) · data-access rules where the database is client-reachable.

### Stage 2: What is covered now
Match existing tests to the standard **by what they assert**. On the **critical modules** (those the
flows and threat model lean on) run **mutation testing** (`mutmut` / `Stryker` / `pitest` /
equivalent): high line coverage with a low mutation score is a hollow suite. Tool missing → **do not
install it**; record the module as unmeasured and read the assertions.

### Stage 3: The gap map
- **(a) No test at all** — a scenario, branch or risk surface nothing covers.
- **(b) Happy path only** — no hostile case (empty, invalid, boundary, another user, a repeated paid
  action, an external failure).
- **(c) Hollow test** — green, but would not fail on a real breakage: trivial assertion, fitted to one
  input.

Rank by risk: **money → sign-in, access and ownership → deletion → external effects and idempotency →
data-access rules → visual → everything else**; lift anything a **human has never seen**
(`review: auto`). Write the map to `.dev-skills/release/test-gaps.md`.

### Stage 4: Write the top gaps · Stage 4b: Prune
Close the top of the list — under `release-product`, everything at the risk surfaces; standalone, agree
how far. **Delegate the authoring in batches** (you keep the map, ranking and red-first verdict);
**cheapest level that proves each gap**, fast and selectable. Then **take cost back out**: duplicate
coverage, tests that cannot fail (the mutation run found them), e2e a unit test proves identically,
their fixtures. Deletion is **proposed, never silent**; a **failing** test is never deleted to go green
— that is a finding. Full rules, incl. what a delegated batch is told:
**`references/writing-and-pruning.md`**.

### Stage 5: RED-FIRST
Run each new test and **see it red on exactly the behaviour it claims to check** (missing or broken
behaviour already is). **Green on the first run is suspect**: break the checked behaviour temporarily
(flip the condition, mock the error) for one run, see the red, **put everything
back**. That break is the **only** touch of product code allowed — no hook enforces this, the rule
does: one minimal break at a time, reverted at once (`git restore <file>` or undo the exact edit), the
revert **proven with `git diff`, not memory** — product code and manifests unchanged; only test files
and `.dev-skills/` change permanently.

### Stage 6: Triage the red
- **Your test is wrong** (selector, unprepared data, missing wait) → fix the test; that is not fitting
  it to green.
- **A genuine bug** → **you may not fix it here.** File a `type: rework` task via `plan-development`
  amend: one-line summary, acceptance criteria = the checked behaviour, reproduction (test, expected,
  actual). **One task per coherent fix, not per red test**: same module or cause → one task, each red
  test its own `acceptance` entry; the 15-open-task ceiling is shared with the build phase
  (**`../_shared/build-pipeline/planning-method.md`**). **Leave the test red and visible**, task id in
  a comment beside it; say out loud the run is now red and `run-task` does not commit red — offer
  `/run-task <id>` next.

Only on the human's explicit "I'll fix it later" may you mark it expected-to-fail with the project's
mechanism (`test.fail()`, `it.fails()`, `xfail`) plus the task id. **Never fit the test to green**: no
weakened assertion, no branch for the test's input, no tuned data, no early return.

### Stage 7: Full gate + record
Run the **whole** check (`make check`). The build loop only ran each task's selection
(**`../_shared/build-pipeline/quality-gate.md`**), so a failure in untouched code is a real finding;
your test red from a real bug is the *result* — show the run as it is, name what is red and why.

Report in one line the full run's **wall-clock** against the `verification.md` budget (default
5 minutes) — over budget is a **finding about the suite**, filed like any other, slowest files named
(**`quality-gate.md`** → "The full run has a budget too") — and **test count and wall-clock before and
after**, pruning included. **A red that will not reproduce is quarantined, not re-run until green**:
re-run the same selection on the unchanged tree; a different result twice = flaky, its own finding and
task; nothing about the suite is provable until it is handled.

Write `.dev-skills/release/test-gaps.md`: the ranked map (surface · needed level · kind of gap · why
risky · what to check); gaps closed and with what, including **what each new test went red on**; what
is open; what could not be measured; the **filed bug tasks** separately. Hand `release-product` the
summary plus task ids.

## Rules

1. **Red-first is mandatory**; no proven red = decoration.
2. **Product code is never edited** — except Stage 5's temporary break, reverted in the same turn.
3. **A real bug → rework task, test stays red**, never fitted to green; expected-to-fail only on the
   human's explicit request.
4. **Read tests by content, not by name**; line coverage is not behaviour coverage.
5. **Hostile cases always; risk surfaces whatever the spec says; paid APIs through the project's
   mocks**, never live.
6. **Cheapest level that proves the gap** (unit by default; e2e only for a real journey, one per
   journey); style and placement from this project; in the standard run, **selectable** by the scoped
   runner.
7. **Install nothing** — tooling is `setup-dev-environment`'s.
8. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
