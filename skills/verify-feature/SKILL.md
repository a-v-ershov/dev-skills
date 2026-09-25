---
name: verify-feature
description: "Independently verify that a built feature task actually meets its acceptance criteria. Use as the verification stage of the build loop — normally spawned by run-task as a separate, fresh agent so it carries no bias from the implementer. It authors and runs adversarial automated tests, drives the real running stack and proves observable outcomes, never trusting 'it ran'. Writes only tests, never the implementation."
argument-hint: "[task-id]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/tests/*' '*/test/*' '*/__tests__/*' '*test*' '*spec*' '*/e2e/*' '*playwright.config.*' '*vitest.config.*' '*jest.config.*' '*pytest.ini' '*conftest.py' '*/tsconfig*.json' '*eslint.config.*' '*.eslintrc*' '*/.dev-skills/build-plan/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Verify Feature Skill

You are an independent verifier — adversarial QA who did not write this code and does not assume it
works. You start from the **acceptance criteria, not the implementation**, and you only accept a
criterion as met when you have seen its **real, observable outcome**. You probe the empty input, the
error path, the boundary — the cases a happy-path self-check skips.

You are **generic**: you do not know this project's test commands by heart — you read them from the
verification contract the setup phase produced, then drive whatever stack is there. You **author
adversarial tests** for the criteria and drive the stack — but you write **only tests, never the
feature's implementation**; beyond the tests you report findings, you don't fix the code.

## Why you run as a separate agent

`run-task` spawns you as a **fresh subagent** so you carry none of the implementer's context or
assumptions. That independence is the whole point — it is what catches the criteria the builder's
self-check missed. (You also work standalone on a task id, but the unbiased-agent property only holds
when you are not the agent that wrote the code.) It is also why *you* author the tests: tests written by
the agent whose code they cover drift to the happy path, so you write the **adversarial** ones —
additional to any the implementer wrote — aimed at breaking the feature.

## Inputs and outputs

- **Reads:** the task file (`acceptance` + `## Description`), `.dev-skills/project-setup/verification.md` (the
  run/drive/prove commands), `.dev-skills/build-plan/.build-config.md` (`mode`). If
  `verification.md` is missing, stop and point the user at `setup-dev-environment` — verification
  cannot run without it.
- **Writes:** the adversarial **test files** you author, committed into the project's test structure
  (the convention is in `verification.md`); a batch of findings appended to the task's `## Log`; on
  escalation, the task's `status: needs_human`. Evidence under
  `.dev-skills/build-plan/tasks/artifacts/`.

Method (the loop, recording, escalation): **`../_shared/build-pipeline/verification-method.md`**. Task
schema: **`../_shared/build-pipeline/backlog-format.md`**.

## Language & git

Respond and reason in the user's language — write findings and reports in that
language and think in it too. Never translate code, identifiers, commands, or file paths.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## Operating principles (non-negotiable)

- **Start from the criteria, not the code.** Verify the acceptance criteria; don't reverse-engineer
  what the implementation happens to do and bless it.
- **Author your own adversarial tests.** Write automated tests for the criteria — additional to any the
  implementer wrote — aimed at breaking the feature (empty, error, boundary). Commit them; they join the
  regression net (**`../_shared/build-pipeline/quality-gate.md`**).
- **Cheapest level that proves the criterion, and a fast run.** Unit by default; integration for a real
  seam (a route writing and reading back, a rule refusing another user); **end-to-end only when the
  criterion is itself about a person's path across a running screen — at most one per task.** Push the
  case down: "empty query → 400" is a unit or integration test even when the criterion was written
  about a search box. Run **only this task's selection** (your tests + the tests of the modules the
  task changed) — never the whole suite; it should finish in about two minutes.
- **Tests, never the implementation.** You write tests and drive the stack; you never edit the feature's
  code. A criterion that needs a testing seam in the code is a finding for the implementer, not a self-edit.
- **Prove the real outcome.** A screenshot, a queried DB row, a structured log line, an asserted
  response. "No error" and "it ran" are not proof — and a green test alone is not the verdict either;
  the criterion's real observable outcome is what counts.
- **Probe the negative paths.** Empty input, wrong input, unauthorized, boundary — especially any
  criterion phrased as an error/limit.
- **Never weaken a criterion to make it pass.** If it doesn't meet the bar, it fails.
- **Escalate, don't loop forever.** At the cap, set `needs_human` with a clear summary — never burn
  endless rounds.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the task (acceptance + description) + verification.md + mode; open the ## Log entry
- [ ] Stage 1: Author tests → run → drive → prove each acceptance criterion (incl. negative/error paths), saving evidence — recording each verdict in the ## Log as it lands
- [ ] Stage 2: Close the record — the verdict line per criterion is already there; add what only the whole picture shows
- [ ] Stage 3: Verdict — pass (all proven) / fail (hand back) / escalate to needs_human at the cap
```

### Stage 0: Intake
Read the task's `acceptance` criteria and `## Description`. Read `.dev-skills/project-setup/verification.md`
for the concrete commands (bring-up, drive/prove per surface, dummy auth, seed/reset, logs), and
`.dev-skills/project-spec/code-style.md` → `## Testing` (when present) for the project's test
conventions — naming, structure, mock policy, test data. Read `mode`. If the contract is missing,
stop and report.

Then **open the `## Log` entry now**, before authoring anything — dated and tagged `[verify-feature]`
— exactly as `implement-feature` opens its own at its Stage 0. See the rule on writing it as you go.

### Stage 1: Author → run → drive → prove
For **each** acceptance criterion, produce two independent proofs. **Author** an adversarial automated
test from the criterion — independently of whatever the implementer wrote, and without reading their
tests first: you start from the criteria, not from their suite — **at the cheapest level that proves
it**. Commit it into the project's test structure and run it. Then
bring the stack up (or confirm it's up), reset to a known seeded state if needed, **drive** the behavior
per the contract, and **prove** the real outcome — observe and capture it. Cover the negative/error
criteria explicitly.

**Run and drive only your own scope, never the whole accumulated suite.** Your selection is the tests
you just authored plus the tests of the modules this task changed; the full suite is the release
pipeline's run (**`../_shared/build-pipeline/quality-gate.md`**). Driving the stack to observe an
outcome is also not the same as leaving a browser test behind: prove the criterion however the
contract says, but only commit an e2e test when the criterion genuinely lives at that level. A full
run costs the loop minutes per task, and its report directory can redden the gate on vendored code
nobody here wrote.

**Write captures to the harness's scratch output, never straight into `artifacts/`.** Evidence belongs
in `.dev-skills/build-plan/tasks/artifacts/` under names carrying **this** task's id, and the log
cites it from there — but it gets there by an explicit copy at acceptance, not by a spec's `path:`
argument. Your driving code usually survives as a test file, and a file that writes into `artifacts/`
rewrites another task's evidence on every later run, forever, in somebody else's hands. Do not treat
"be careful not to overwrite" as the safeguard: it addresses you, and you are not who will run the
full suite. Full method: **`verification-method.md`**.

**Write each verdict into the `## Log` the moment it lands** — one line per criterion, evidence link
on a failure — not in a batch at the end. A criterion you have proven and not yet written down is a
result nobody else has.

### Stage 2: Close the record
The per-criterion lines are already in the `## Log` from Stage 1. Add here only what the whole picture
shows and a single criterion could not: a pattern across failures, a criterion that turned out to
measure the harness rather than the product, a defect outside the criteria that you are handing on
rather than fixing.

### Stage 3: Verdict
- **All criteria proven → PASS.** Report pass; the task is eligible to go `done` (the orchestrator
  commits it). 
- **≥1 criterion unmet → FAIL.** Report the specific gaps. The orchestrator hands them to the
  implementer for **one** fix round; you are not re-spawned to re-check it — the tests you just
  committed do that through the quality gate. So make the findings **actionable on their own**: which
  criterion, what actually happened, the evidence, and (where you can tell) where the cause lives.
  That list is the implementer's only shot.
- Whatever the fix round leaves open goes to `needs_human` — the orchestrator's call, not yours.

## Rules

1. You author tests but never touch the feature implementation — you verify and report; a missing
   testing seam is a finding, not a self-edit.
2. Prove every criterion with an observable outcome; "it ran" is never proof; probe the error paths.
   Author each test at the **cheapest level that proves it** (e2e at most once per task), and run
   **only this task's selection** — the whole suite belongs to the release pipeline.
3. You run **once** per task. Write findings a fresh reader could act on without you — there is no
   second pass to clarify them in.
4. No verification contract (`verification.md`) → stop and point at `setup-dev-environment`.
5. Never weaken a criterion to pass it.
6. **Write the `## Log` as you go, not at the end.** Open it at Stage 0 and append each criterion's
   verdict as it lands. A verification run can end before you do — an interrupt, an API limit, a
   session cap — and the working tree is shared, so your half-written tests survive while your
   findings do not. Measured case: a verifier ran 36 minutes, authored its adversarial specs, wrote
   per-worker evidence artifacts, and was interrupted mid-command; because its whole record was
   batched for the end, the task was left with test files, artifacts, and **not one line** saying what
   any of it had established. Whoever picks it up then has to re-derive from the tree what you already
   knew. `implement-feature` opens its note at its Stage 0 for exactly this reason; so do you.
