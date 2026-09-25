---
name: write-tests
description: "Map where the product is NOT protected by an automated test, then close the top of that list with honest tests. Use in the release phase (run by release-product, after refactor) or standalone whenever the test net needs checking. It builds the gap map — what should be covered against what is covered, read from the tests' contents rather than their names, with mutation testing to expose a suite that executes lines without catching bugs — ranks it by risk, and writes the top ones at the cheapest level that proves each, keeping them fast and selectable. Red-first: a test is not accepted until it has been seen going red."
argument-hint: "[<feature / flow / task-id> | empty = whole product]"
---

# Write Tests Skill

A green suite proves only what somebody thought to put in it. It says nothing about what is **not** in
it — and that silence is where the expensive failures live: a scenario nobody checks breaks quietly and
surfaces at a user, worst of all around money, access, and deleted data.

You do two things, in this order: you **map the holes**, then you **close the top ones with tests that
can actually fail**. You are not the build loop's verifier — `verify-feature` proves one task's
acceptance criteria as it is built. You come back afterwards, over the whole product, and ask what
nobody proved.

**You never edit product code.** Writing a test and then adjusting the product until it passes is
approving your own work — exactly what the separate-verifier split exists to prevent. A real bug becomes
a **rework task** and the test stays **red**.

## Inputs and outputs

- **Reads:** the **user flows and their states** in `.dev-skills/project-spec/user-flows.research.md`
  and the **acceptance criteria** in `.dev-skills/build-plan/tasks/` (what should be covered);
  `.dev-skills/project-setup/verification.md` (how to run, drive, seed, and prove);
  `.dev-skills/project-spec/code-style.md` → `## Testing` (the test conventions, when present); the
  existing tests.
- **Writes:** test files; `.dev-skills/release/test-gaps.md` (the map + what was closed); rework tasks
  for the bugs found (via `plan-development` amend). **Never product code** — enforced by a write-scope
  hook, not just by this sentence.

## Language & git

Respond and reason in the user's language — write the map, the findings, and the
report in that language and think in it too. Never translate code, identifiers, commands, or paths.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

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
An argument (a feature, a flow, a task id) narrows everything to it; empty means the whole product.
Determine **from the project, not from habit**: which test levels actually exist and with what tools,
where tests live, and the one command that runs them all. Say what you found in one line so the human
can correct you.

### Stage 1: What should be covered
Build the standard from the project's own sources of truth:

- **Every flow and every state it names** — not just the happy path: empty, loading, the validation
  error, the permission denial, the boundary.
- **Every task's acceptance criteria** — each "given / when / then" must be proven by something.
- **The risk surfaces, always, regardless of what the spec says**: money and payments · sign-in, access,
  and ownership of someone else's data · deletion · external side effects · idempotency (a repeat must
  not do the work twice) · data-access rules where the database is reachable from the client.

### Stage 2: What is covered now
Read the existing tests and match them to the standard **by what they assert, not by what they are
called** — a file named for a payment task may create a payment and never check double-charging.
Remember that **line coverage is not behaviour coverage**: a file can be 100% green with the error
branch never once exercised.

On the **critical modules** (the ones the flows and the threat model lean on), run **mutation testing**
(`mutmut` / `Stryker` / `pitest` / the stack's equivalent) — inject faults and see whether the suite
fails. High line coverage with a low mutation score is a hollow suite: assertions that do not assert.
If the tool is not installed, **do not install it** — record the module as unmeasured (installing
tooling is `setup-dev-environment`'s job) and fall back to reading the assertions.

### Stage 3: The gap map
Three kinds:

- **(a) No test at all** — a scenario, a branch, or a risk surface nothing covers.
- **(b) Happy path only** — a test exists, but no hostile case: empty, invalid input, boundary, another
  user, a repeated paid action, an external service failing.
- **(c) Hollow test** — it passes but would not fail on a real breakage: it asserts something trivial,
  it is fitted to one fixed input, the assertions say nothing. Mark it a gap even though it is green.

Rank by risk: **money → sign-in, access and ownership → deletion → external effects and idempotency →
data-access rules → visual → everything else**, and lift anything a **human has never seen** (a task
accepted with `review: auto`). Write the map to `.dev-skills/release/test-gaps.md`.

### Stage 4: Write the top gaps · Stage 4b: Prune
Close the top of the list — in a `release-product` run, everything ranked at the risk surfaces; run
standalone, agree how far to go. **Delegate the authoring in batches** (you keep the map, the ranking
and the red-first verdict); choose the **cheapest level that proves each gap**; keep the new tests fast
and selectable; hostile cases always; paid APIs through the project's own mocks.

Then, in the same pass, **take cost back out**: duplicate coverage, tests that cannot fail (the
mutation run already found them), e2e cases a unit test proves identically, and the fixtures they leave
behind. Deletion is **proposed, never silent**, and a **failing** test is never deleted to make the
suite green — that is a finding.

Full rules for both, including what a delegated batch must be told:
**`references/writing-and-pruning.md`**.


### Stage 5: RED-FIRST (the rule that makes the rest worth anything)
Run each new test and **see it red on exactly the behaviour it claims to check**.

- A test for behaviour that is missing or broken is already red — that is the point.
- **A test that is green on its first run is suspect**: it may be asserting nothing. Prove it can fail —
  break the checked behaviour temporarily (flip the condition, corrupt the input, mock the error) for a
  single run, see the red, and **put everything back**.

That temporary break is the **only** touch of product code this skill is allowed, and **only ever
temporarily** — no hook enforces this scope, the rule does: one minimal break at a time, revert it
immediately after the red run (`git restore <file>` or undo the exact edit), then **prove the revert
with `git diff`, not your memory** — product code and manifests must show no change; only test files
and `.dev-skills/` may change permanently. A test accepted green without this proof is decoration.

### Stage 6: Triage the red — the product's code stays untouched
Red means one of two things:

- **Your own test is wrong** — the wrong selector, unprepared data, a missing wait. Fix the test. Fixing
  your own mistake and fitting the test to green are different things; the second is forbidden (below).
- **A genuine bug** — the test is right and the code is wrong. **You may not fix it here.** File a
  `type: rework` task via `plan-development` amend: a one-line human summary, acceptance criteria stating
  exactly the behaviour the test checks, and how to reproduce it — which test goes red, what was
  expected, what actually happened. **One task per coherent fix, not one per red test**: bugs in the
  same module or with the same cause go into one task, each red test kept as its own `acceptance`
  entry with its reproduction; the backlog's 15-open-task ceiling is shared with the build phase
  (**`../_shared/build-pipeline/planning-method.md`**). **Leave the test red and visible** with the task id in a comment
  beside it, and say out loud that the run is now red and what follows: the gate will fail on your test,
  and in this project the build loop depends on the gate — `run-task` does not commit red. That is not a
  reason to hide the test; it is a reason to fix the bug next, so offer `/run-task <id>` as the next step.

Only if the human explicitly says they will fix it later may you mark the test expected-to-fail with the
project's own mechanism (`test.fail()`, `it.fails()`, `xfail`) plus the task id — never on your own
initiative.

**In neither case is the test fitted to green.** Forbidden: weakening an assertion, adding a branch for
the test's specific input, tuning data to match the wrong answer, returning early so the run "passes"
without checking anything.

### Stage 7: Full gate + record
Run the project's **whole** check (`make check`), not just the new file: the tests must join the
regression net and must not break their neighbours. This is one of the few places the whole suite is
run — the build loop only ever ran each task's own selection
(**`../_shared/build-pipeline/quality-gate.md`**) — so treat a failure in code nobody touched here as a
real finding, not noise: it is a regression the loop could not have seen. Your own test red because of
a real bug is the *result*, not a failure — show the run as it is and name what is red and why.

Report the **wall-clock of that full run** in one line, against the budget in `verification.md`
(default 5 minutes). Over budget → that is a **finding about the suite**, filed like any other, with
the slowest files named (**`../_shared/build-pipeline/quality-gate.md`** → "The full run has a budget
too"). It is the number that decides whether the suite is still affordable, and nobody else measures
it. Report the **test count and wall-clock before and after** this run, pruning included — a release
where both went up is a release that made every future one more expensive.

**A red that will not reproduce is quarantined, not re-run until it is green.** Confirm a failure by
re-running the same selection on the unchanged tree; a different result twice means the test is flaky,
which is its own finding with its own task, and no claim about the suite is provable until it is
handled.

Write `.dev-skills/release/test-gaps.md`: the ranked map (surface · needed level · kind of gap · why it
is risky · what to check), which gaps you closed and with what — including **what each new test went red
on** — what is left open, what could not be measured, and a separate list of the **filed bug tasks**.
Hand `release-product` the same summary plus the task ids.

## Rules

1. **Red-first is mandatory.** A test with no proven red is decoration, not a test.
2. **Product code is never edited** — enforced by the write-scope hook. The only allowed touch is the
   temporary break in Stage 5, reverted in the same turn.
3. **A real bug becomes a rework task and the test stays red.** Red is the finding; masking it turns the
   alarm off. Expected-to-fail only on the human's explicit request.
4. **Never fit a test to green** — no weakened assertion, no branch for the test's input, no tuned data,
   no early return.
5. **Read tests by content, not by name**; line coverage is not behaviour coverage.
6. **Hostile cases always**, and the risk surfaces are covered whether or not the spec mentions them.
7. **Cheapest level that proves the gap** (unit by default, e2e only for a real journey, one per
   journey); style and placement come from this project; the test must land in the standard run and be
   **selectable** by the scoped runner.
8. **Paid APIs go through the project's mocks** — never live.
9. **Install nothing.** A missing mutation-testing tool is recorded as unmeasured.
10. **Not a replacement for `verify-feature`** — that proves one task as it is built; this is the
    retrospective sweep over everything nobody proved.
11. **End every report with «What you should do»** — numbered, imperative, one line per item, in the user's language and free of this set's vocabulary; "nothing" is a valid one-line answer. Timings, where reported, must reconcile with their total. **`../_shared/build-pipeline/report-format.md`**.
