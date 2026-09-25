---
name: optimize-dev
description: "Run the periodic development-hygiene pass: a thin conductor that first grooms the backlog (groom-backlog — sizes open tasks and merges small or same-cause ones back under the shared 15-task ceiling) and then audits the test suite (audit-tests — the 30-second routine-run budget, the 10-e2e cap, e2e out of every automatic path). Use from time to time between build runs, when tasks have piled up small or the tests have grown slow; name one half (backlog | tests) to run it alone. It conducts and reports — the sub-skills do the work and carry their own confirmation gates; pass autopilot to apply everything without pausing."
argument-hint: "[autopilot] [backlog | tests]"
---

# Optimize Dev Skill (orchestrator)

You are the maintenance conductor. Development hygiene decays in two predictable places: the backlog
fragments (audits, adhoc requests and reworks pile up small tasks until the board is bookkeeping), and
the test suite grows slower with every task until nobody affords to run it. This skill exists so
"time to time" is a single command: it sequences the two focused sub-skills, passes the mode down,
and merges their reports. **It conducts; it does not duplicate** — no merge rule and no budget is
restated here, and you never groom or optimize anything yourself.

## Language & git

Respond and reason in the user's language — and tell each sub-skill the same rule. Never translate
code, identifiers, commands, or paths. Workflow vocabulary follows **`../_shared/glossary.md`**.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — what exists (backlog? tests?), scope argument, autopilot argument
- [ ] Stage 1: Groom — invoke groom-backlog (skipped: no backlog, or scope says tests)
- [ ] Stage 2: Tests — invoke audit-tests (skipped: no tests, or scope says backlog)
- [ ] Stage 3: Close — one merged report + one «What you should do»
```

### Stage 0: Intake
Check what the pass applies to: a backlog exists (`.dev-skills/build-plan/tasks/` non-empty) and tests
exist (a test directory or runner config anywhere in the repo). An argument of `backlog` or `tests`
narrows the pass to that half; a half whose subject is absent is skipped — **announced in one line,
never silently**. Nothing to do at all → say so and stop. Carry the `autopilot` argument, if given,
into every sub-skill invocation.

### Stage 1: Groom the backlog
Invoke **`dev-skills:groom-backlog`** (with `autopilot` when given). It sizes the open tasks, builds
the merge plan, holds its own confirmation gate, applies, and reports. Collect its summary — open
count before/after and anything it flagged.

### Stage 2: Audit the tests
Invoke **`dev-skills:audit-tests`** (with `autopilot` when given). It measures the runs against the
budgets, holds its own gate, applies, re-measures, and writes
`.dev-skills/optimize/test-audit.md`. Collect its summary — the before/after wall-clocks, the e2e
count, and any filed tasks.

### Stage 3: Close
One short combined report: what each half found and changed (backlog N → M open tasks; routine run
Xs → Ys, e2e K → L), what was skipped and why, wall-clock per half that reconciles with the total
(**`../_shared/build-pipeline/report-format.md`**). Then **one** merged «What you should do» — the
sub-skills' items combined, deduplicated, renumbered; "nothing" is a valid answer.

## Rules

1. **Conduct, don't duplicate.** The merge rules live in `groom-backlog`/`planning-method.md`; the
   budgets live in `audit-tests`/`verification.md`. Restate neither; do neither yourself.
2. **The sub-skills own their confirmation gates.** You never pre-approve on their behalf; `autopilot`
   is passed through verbatim, not invented.
3. **Skipping is announced**, one line with the reason — never silent.
4. **Backlog first, then tests** — grooming is cheap and its result frames the report; the test audit
   is the long half.
5. **One merged closing report, one «What you should do»** — the human gets a single list, not two
   reports to reconcile.
