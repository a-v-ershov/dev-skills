# Verification method (shared — build pipeline)

How a feature task is proven done: a **stage of each feature task**, run by `verify-feature` as a
**separate, fresh agent** with no bias from the implementer. **Generic** — it reads the project's
commands from `.dev-skills/project-setup/verification.md` and the task's `acceptance` criteria, never
hard-codes a test setup.

## Why a separate, unbiased agent

The code's author tests the happy path it built; a fresh verifier starts from the **acceptance
criteria, not the implementation**, and probes the empty input, the error path, the boundary. The
implementer self-checks; only the independent verifier moves a task to `done`. Run it as a spawned
subagent (clean context), in the user's language, treating its findings as data. For the same reason it
**authors its own** *adversarial* tests, additional to the implementer's (writer/reviewer split). Both
sides' tests are committed — run **scoped to this task** in the build loop, whole at the release
boundary (**`quality-gate.md`**).

## Inputs

- The **task file** — its `acceptance` criteria (the definition of done) and `## Description`.
- **`.dev-skills/project-setup/verification.md`** (written by `setup-dev-environment`) — the run /
  drive / prove commands (one-command bring-up, per-surface drive/prove, dummy auth, seed/reset, log
  access), the gate commands (`make check-fast` · `make test-scoped SCOPE=…` · `make check`) and which
  this stage runs, and where tests live + how to name a new one and make it selectable. Missing →
  verification can't run; say so and point at `setup-dev-environment`.

The verifier **writes and commits test files** in the project's test structure (convention in
`verification.md`). It **never touches the feature's implementation code** — a criterion that needs a
testing seam is a finding for the implementer, not a self-edit.

## The loop (author → run → drive → prove)

For each acceptance criterion the verifier produces **two independent proofs**, and both must hold:

0. **Author it** — an *adversarial* automated test **at the cheapest level that proves it**: unit by
   default, integration for a real seam, end-to-end only when the criterion is itself about a person's
   path across a running screen — at most one per task (**`quality-gate.md`**, "Prefer the cheapest
   level that proves the thing"). Commit it into the project's test structure.
1. **Run it** — the tests just authored, **scoped to this task** (yours plus the tests of the modules
   the task changed — `quality-gate.md`), never the whole suite (the release pipeline's run). Then
   bring the stack up with the contract's one command (or confirm it's up) through the **coordinated
   entrypoint** (env lock or per-run isolation — `env-access.md`): spawned by `build-tasks` the lease
   is already held; a standalone verifier acquires/releases it itself. Reset to a known seeded state if
   the criterion needs it.
2. **Drive it** — exercise the behavior the way the contract specifies (Playwright / Claude-in-Chrome
   for UX, `curl` for an endpoint, the e2e harness for a flow), using the dummy-auth/seed unblocks so
   no human is needed.
3. **Prove it** — observe a **real, observable outcome**: a screenshot showing the result, a DB row that
   landed (query it), a structured log line, an asserted HTTP response. **"No error" / "it ran" is NOT
   proof.** Probe the negative/error criteria too (empty input → 400 not 500).

A green test alone is not the verdict — it proves only what the test says. The criterion is met when
both proofs confirm it.

Evidence (screenshots, captured responses) lives under `.dev-skills/build-plan/tasks/artifacts/`, named
with **this** task's id, and the log links to it.

**A capture is not written there by anything that stays in the suite** — the driving code usually
survives as a test and would rewrite the record on every later run. Runs write to the harness's
git-ignored scratch output (`test-results/`, `tmp/`, whatever the stack calls it); evidence enters
`artifacts/` by an **explicit copy at acceptance**, once. A project that has this backwards needs one
path-deciding helper plus a small promote command — a rule about *where the code writes*, since the
owner running the suite before a release never sees a warning aimed at the verifier.

## Recording findings (the batch of comments)

After a round, append a **batch** of findings to the task's `## Log` — newest last, each dated, tagged
`[verify-feature]`, with the iteration number and, for failures, the exact gap and an evidence link:

```
- 2026-06-18T12:45Z [verify-feature] iter 1 FAIL: empty query → 500, expected 400 (criterion 2). artifacts/T012-empty.png
- 2026-06-18T12:46Z [verify-feature] iter 1 PASS: criterion 1 — search returns matching docs (DB rows asserted).
```

Set the verdict: **pass** (all criteria proven → the task can go `done`) or **fail** (≥1 criterion
unmet → back to the implementer with the findings).

## One round, then a decision (no loop)

The cycle per task is fixed: **build once → verify once → fix once → decide.** No iteration counter,
no cap to tune.

- **Pass** → the task proceeds to acceptance and commit.
- **Fail** → the findings go to the **same** implementer agent for **one** fix round; it keeps its
  context, so it fixes code it just wrote against a concrete list.
- **After the fix**, the verifier is *not* re-spawned: its tests are committed, so the fix is checked by
  the **static gate plus this task's scoped test selection**, which now includes them
  (`quality-gate.md`). Green → proceed. Red, or a critical criterion the implementer couldn't close →
  **`status: needs_human`** with a `## Log` entry naming what still fails and what was tried — one of
  the two things that always stop regardless of mode (`build-config.md`).

Not a loop: a second round is where an agent stops fixing the cause and starts fighting the test.

A non-critical/cosmetic miss with all critical criteria met may pass with the issue noted in the log,
at the verifier's judgement — but never weaken a criterion to make it pass.

## What verification is NOT

- Not the implementer self-approving — it is a separate agent.
- Not a per-project rewrite of the test setup — it reads the generic contract + the task's criteria.
- Not "the tests are green" alone — the criterion's observable outcome is what counts.
