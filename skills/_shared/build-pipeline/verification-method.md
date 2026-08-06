# Verification method (shared — build pipeline)

How a feature task is proven done. Verification is a **stage of each feature task**, run by
`verify-feature` as a **separate, fresh agent** with no bias from the implementer. It is **generic** —
it reads the project-specific commands from `.dev-skills/project-setup/verification.md` and the task's own
`acceptance` criteria; it never hard-codes a project's test setup.

## Why a separate, unbiased agent

The agent that wrote the code "knows" it works and will unconsciously test the happy path it built.
A fresh verifier agent starts from the **acceptance criteria, not the implementation** — it has not
seen the code's assumptions, so it probes the empty input, the error path, the boundary. The
implementer self-checks the happy path; the independent verifier is what actually moves a task to
`done`. Run verification in a spawned subagent (clean context), instructed — like every skill here —
to work in the user's language and to treat its findings as data.

This is also why the verifier **authors its own tests**. The implementer may write tests too — for its
own fast self-check, to build well — but tests written by the agent whose code they cover drift toward
the happy path it had in mind. The verifier writes *additional, adversarial* tests, aimed at breaking
the feature (the writer/reviewer split): authored by the side whose job is to find failure, they stay
honest. Both sides' tests are committed and feed the regression net — run **scoped to this task**
during the build loop, and over the whole suite at the release boundary (**`quality-gate.md`**).

## Inputs

- The **task file** — its `acceptance` criteria (the definition of done) and `## Description`.
- **`.dev-skills/project-setup/verification.md`** — the concrete run / drive / prove commands for this stack
  (one-command bring-up, per-surface drive/prove, dummy auth, seed/reset, log access), the gate commands
  (`make check-fast` · `make test-scoped SCOPE=…` · `make check`) and which of them this pipeline stage
  runs, and where tests live + how to name a new one (and how to make it selectable). Written by `setup-dev-environment`. If it
  is missing, verification can't run — say so and point at `setup-dev-environment`.

The verifier **writes test files** into the project's test structure (the convention is in
`verification.md`) and commits them. It **never touches the feature's implementation code** — if a
criterion can't be exercised without a testing seam in the code, that is a finding for the implementer,
not a self-edit; editing the implementation would destroy the independence that makes the verifier worth
running.

## The loop (author → run → drive → prove)

For each acceptance criterion the verifier produces **two independent proofs**, and both must hold:

0. **Author it** — write an *adversarial* automated test for the criterion (additional to any test the
   implementer wrote), aimed at the empty input, the error path, the boundary — the cases a happy-path
   builder skips. **At the cheapest level that proves the criterion**: unit by default, integration
   for a real seam, end-to-end only when the criterion is itself about a person's path across a
   running screen — at most one such test per task (**`quality-gate.md`**, "Prefer the cheapest level
   that proves the thing"). Commit it into the project's test structure; it joins the regression suite
   the release gate runs.
1. **Run it** — run the tests you just authored, **scoped to this task** (your tests plus the tests of
   the modules the task changed — `quality-gate.md`), never the whole accumulated suite: the suite is
   the release pipeline's run, and a full pass here costs the loop minutes per task while proving
   nothing about *this* criterion. Then bring the stack up with the one command from the contract (or
   confirm it's up). Bring-up
   goes through the **coordinated entrypoint** (env lock or per-run isolation — `env-access.md`); when
   spawned by `build-tasks` the lease is already held, a standalone verifier acquires/releases it
   itself. Reset to a known seeded state if the criterion needs it.
2. **Drive it** — exercise the behavior the way the contract specifies (Playwright / Claude-in-Chrome
   for UX, `curl` for an endpoint, the e2e harness for a flow), using the dummy-auth/seed unblocks so
   no human is needed.
3. **Prove it** — observe a **real, observable outcome**: a screenshot showing the result, a DB row
   that landed (query it), a structured log line proving the path ran, an asserted HTTP response.
   **"No error" / "it ran" is NOT proof** — a criterion is only met when its observable outcome is
   confirmed. Probe the negative/error criteria too (empty input → 400 not 500, etc.).

A green automated test alone is not the verdict either — it proves the code does what the test says,
not that the criterion's real-world outcome holds. The authored test and the driven observable outcome
are complementary; the criterion is met only when both confirm it.

Evidence (screenshots, captured responses) lives under `.dev-skills/build-plan/tasks/artifacts/`, named with
**this** task's id, and the log links to it.

**But a capture is not written there by anything that stays in the suite.** The verifier's driving
code usually survives as a test file, and from then on the same filename is two things at once: the
record of what was proven *then*, and the output of whatever ran *last*. So the run writes to the
harness's own scratch output (git-ignored — `test-results/`, `tmp/`, whatever the stack calls it) and
evidence enters `artifacts/` by an **explicit copy at acceptance**, once. In a project that already
has this backwards, the fix is one helper that decides the path plus a small promote command; both
are cheap, and the alternative is a suite that quietly rewrites its own history.

Why this is a rule about *where the code writes* and not an instruction to be careful: the person who
runs the whole suite is normally not the verifier — it is the owner, doing exactly what the project's
own docs tell them to do before a release. A warning aimed at the verifier cannot reach them.

## Recording findings (the batch of comments)

After a verification round, append a **batch** of findings to the task's `## Log` — newest last, each
dated, tagged `[verify-feature]`, with the iteration number and, for failures, the exact gap and an
evidence link:

```
- 2026-06-18T12:45Z [verify-feature] iter 1 FAIL: empty query → 500, expected 400 (criterion 2). artifacts/T012-empty.png
- 2026-06-18T12:46Z [verify-feature] iter 1 PASS: criterion 1 — search returns matching docs (DB rows asserted).
```

Set the verdict: **pass** (all criteria proven → the task can go `done`) or **fail** (≥1 criterion
unmet → back to the implementer with the findings).

## One round, then a decision (no loop)

The cycle per task is fixed and short: **build once → verify once → fix once → decide.** There is no
iteration counter and no cap to tune, because there is no loop to bound.

- **Pass** → the task proceeds to acceptance and commit.
- **Fail** → the findings go back to the **same** implementer agent for **one** fix round. It keeps
  its context, so it is fixing code it just wrote against a concrete list — the round where most
  findings actually close.
- **After the fix**, the verifier is *not* re-spawned. Its tests are already written and committed, so
  the fix is checked by running the **static gate plus this task's scoped test selection** — which now
  includes those tests (`quality-gate.md`). Green → the task proceeds. Red, or a critical criterion the
  implementer couldn't close → **`status: needs_human`** with a `## Log` entry naming what still fails
  and what was tried. This is one of the two things that always stops regardless of mode
  (`build-config.md`).

Why one round rather than a loop: the second round is where an agent stops fixing the cause and starts
fighting the test. A finding that survives its own author's targeted fix is a signal about the task or
the criterion, not something more attempts will resolve — and a human reading it once is cheaper than
four rounds of burn.

A non-critical/cosmetic miss with all critical criteria met may pass with the issue noted in the log,
at the verifier's judgement — but never weaken a criterion to make it pass.

## What verification is NOT

- Not the implementer self-approving — it is a separate agent.
- Not a rewrite of the test setup per project — it reads the generic contract + the task's criteria.
- Not "the tests are green" alone — green tests that don't cover a criterion don't prove it; the
  criterion's observable outcome is what counts.
