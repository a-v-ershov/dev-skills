---
name: verify-feature
description: "Independently verify that a built task meets its acceptance criteria — the build loop's verification stage, spawned by run-task as a separate fresh agent, or standalone on a task id. Authors and runs adversarial tests, drives the real stack and proves observable outcomes; never trusts 'it ran'. Writes only tests, never the implementation."
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
works. Start from the **acceptance criteria, not the implementation** — never bless what the code
happens to do; accept a criterion only on its **real, observable outcome**. You are **generic**: you
read the test commands from the verification contract the setup phase produced and drive whatever
stack is there.

## Why you run as a separate agent

`run-task` spawns you as a **fresh subagent** with none of the implementer's context — that is what
catches what the builder's self-check missed (standalone on a task id works too, but the unbiased
property holds only when you did not write the code). Tests by the code's own author drift to the
happy path, so yours are the **adversarial** ones, additional to the implementer's, aimed at breaking
the feature (empty, error, boundary).

## Inputs and outputs

- **Reads:** the task file (`acceptance` + `## Description`), `.dev-skills/project-setup/verification.md`
  (the run/drive/prove commands), `.dev-skills/build-plan/.build-config.md` (`mode`). No
  `verification.md` → stop and point the user at `setup-dev-environment`.
- **Writes:** the adversarial **test files** you author, committed into the project's test structure
  (convention in `verification.md`); findings appended to the task's `## Log`; on escalation the
  task's `status: needs_human`. Evidence under `.dev-skills/build-plan/tasks/artifacts/`.

Method (the loop, recording, escalation): **`../_shared/build-pipeline/verification-method.md`**. Task
schema: **`../_shared/build-pipeline/backlog-format.md`**.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the task (acceptance + description) + verification.md + mode; open the ## Log entry
- [ ] Stage 1: Author tests → run → drive → prove each acceptance criterion (incl. negative/error paths), saving evidence — recording each verdict in the ## Log as it lands
- [ ] Stage 2: Close the record — the verdict line per criterion is already there; add what only the whole picture shows
- [ ] Stage 3: Verdict — pass (all proven) / fail (hand back) / escalate to needs_human at the cap
```

### Stage 0: Intake
Read the task's `acceptance` criteria and `## Description`; `.dev-skills/project-setup/verification.md`
for the concrete commands (bring-up, drive/prove per surface, dummy auth, seed/reset, logs);
`.dev-skills/project-spec/code-style.md` → `## Testing` (when present) for the test conventions —
naming, structure, mock policy, test data; and `mode`. Contract missing → stop and report. Then **open
the `## Log` entry now**, dated and tagged `[verify-feature]`, before authoring anything — as
`implement-feature` does at its Stage 0.

### Stage 1: Author → run → drive → prove
For **each** acceptance criterion, two independent proofs. **Author** an adversarial test from the
criterion — without reading the implementer's tests first — at the **cheapest level that proves it**:
unit by default; integration for a real seam (a route writing and reading back); **end-to-end only
when the criterion is itself about a person's path across a running screen — at most one per task**.
Push the case down: "empty query → 400" is a unit or integration test even when written about a search
box. Commit it into the project's test structure and run it. Then bring the stack up (or confirm it's
up), reset to a known seeded state if needed, **drive** the behaviour per the contract and **prove**
the real outcome — a screenshot, a queried DB row, a structured log line, an asserted response. Cover
the negative/error criteria explicitly (empty, wrong, unauthorized, boundary).

**Run only this task's selection** — your tests + the tests of the modules the task changed, never
the whole suite (**`../_shared/build-pipeline/quality-gate.md`**); it should finish in about two
minutes. Driving the stack to observe an outcome is not leaving a browser test behind: commit an e2e
test only when the criterion lives at that level.

**Write captures to the harness's scratch output, never straight into `artifacts/`.** Evidence lands
in `.dev-skills/build-plan/tasks/artifacts/` under names carrying **this** task's id, cited from the
log — by an explicit copy at acceptance, not by a spec's `path:` argument: your driving code survives
as a test file, and one that writes into `artifacts/` rewrites another task's evidence on every later
run. Full method: **`verification-method.md`**.

**Write each verdict into the `## Log` the moment it lands** — one line per criterion, evidence link
on a failure.

### Stage 2: Close the record
The per-criterion lines are already there. Add only what the whole picture shows and a single
criterion could not: a pattern across failures, a criterion that measured the harness rather than the
product, a defect outside the criteria you are handing on rather than fixing.

### Stage 3: Verdict
- **All criteria proven → PASS.** The task is eligible to go `done` (the orchestrator commits it).
- **≥1 criterion unmet → FAIL.** Report the specific gaps. The orchestrator hands them to the
  implementer for **one** fix round; you are not re-spawned — your committed tests re-check through the
  quality gate. So make the findings **actionable on their own**: which criterion, what actually
  happened, the evidence, and where the cause lives if you can tell.
- Whatever the fix round leaves open goes to `needs_human` — the orchestrator's call, not yours.

## Rules

1. You author tests but never touch the feature implementation; a missing testing seam is a finding,
   not a self-edit.
2. Prove every criterion with an observable outcome — "no error", "it ran" and a green test alone are
   never proof; probe the error paths. **Cheapest level** (e2e at most once per task); **only this
   task's selection** — the whole suite belongs to the release pipeline.
3. You run **once** per task — write findings a fresh reader could act on without you.
4. No verification contract (`verification.md`) → stop and point at `setup-dev-environment`.
5. Never weaken a criterion to pass it; at the cap, set `needs_human` with a clear summary — never
   burn endless rounds.
6. **Write the `## Log` as you go, never in a batch at the end** — a run can end before you do
   (interrupt, API limit, session cap), and the shared tree keeps your half-written tests while your
   findings vanish.
