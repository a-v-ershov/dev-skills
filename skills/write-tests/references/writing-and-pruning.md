# Writing and pruning (write-tests)

The full detail of Stage 4 (authoring the top gaps) and Stage 4b (taking cost back out of the
suite). Read this when you reach the stage.

---

## Stage 4 — writing the top gaps

**Delegate the writing, keep the map and the red-first verdict.** The gap map, the ranking and the
judgement on every red are yours; authoring a batch of tests against a decided gap is mechanical and
belongs in a subagent, so this stage does not consume the context the rest of the release phase needs.
Give each subagent: the gaps it is closing, the level chosen for each, the neighbouring tests to copy
the style from, and the rule that it writes tests only — never product code. It returns the files and
the run output; **you** perform Stage 5 on what comes back. Batch by area, one batch at a time.

Close the top of the list — in a `release-product` run, everything ranked at the risk surfaces; run
standalone, agree how far to go. For each:

- **Choose the cheapest level that proves it**: pure logic, calculation, validation, formatting →
  **unit** (the default — this is where most gaps close); a seam (a route writes to the database and
  reads it back, a rule refuses another user, a repeat does not charge twice) → **integration**; a
  person's path across a screen from entry to outcome → **end-to-end**, and only when the gap is
  genuinely about that path. E2E is the slowest and flakiest thing you can add, and every one of them
  is paid for on every release run from now on — one per journey, not one per case. Push what you can
  down a level (the same rule the build loop follows,
  **`../../_shared/build-pipeline/quality-gate.md`**). One gap sometimes needs two tests at two levels.
- **Keep the new tests fast.** No `sleep` where waiting for a condition works, no per-case rebuild of a
  fixture that could be per-file, no live network where the project has a local stand-in, and
  slow-by-design primitives (Argon2/bcrypt, backoff, rate limits) at their test-cost settings. A test
  that is slow because the *product* is slow is a performance finding, not something to be patient
  with — record it.
- **Make the new tests selectable** — tag or place them so `make test-scoped` can address them (per
  area / per task id, following the project's convention). A test nobody can select is a test the
  build loop can only run by running everything, which it does not do.
- **Follow the neighbours.** Read one or two nearby tests of the same level and copy their style,
  helpers, data setup, and placement, so the test lands in the project's regression run instead of
  beside it.
- **Hostile cases always**, even when the request named only the happy path.
- **Paid and external APIs go through the project's own mocks** (the switch `verification.md` documents)
  — never live: that costs money and touches real data.

## Stage 4b — pruning what the suite pays for and does not earn

Adding is only half the job. A suite grows monotonically unless something removes from it, and the
cost is charged to every future release run: both field projects passed **1 500** and **2 500** tests,
and the owner twice asked for the number to come *down* before anything else could proceed. So, in the
same pass, and **only with the same red-first evidence you demand of a new test**:

- **Duplicate coverage** — two or more tests asserting the same behaviour through the same path (often
  one unit and one e2e written months apart). Keep the cheapest one that proves it; delete the rest,
  naming what each covered.
- **Tests that cannot fail** — the mutation run from Stage 2 already found these. A test that stays
  green under a mutation of the code it claims to check is not coverage, it is cost. Either make it
  bite or delete it; never leave it as decoration.
- **Tests at the wrong level** — an e2e case that a unit test proves identically. Rewrite it down a
  level and delete the browser version; e2e is what makes a suite unaffordable.
- **Dead fixtures and helpers** left behind by the above.

Rules for the pruning: **deletion is proposed, never silent** — list what goes and why, and get a yes
in interactive mode; **a test that fails is never deleted to make the suite green** (that is the one
case where deletion is forbidden outright — it is a finding, see Stage 6); and record the before/after
counts and wall-clock in the report, because that number is the whole point.
