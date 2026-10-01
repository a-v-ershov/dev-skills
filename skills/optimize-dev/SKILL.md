---
name: optimize-dev
description: "Run the periodic development-hygiene pass: a thin conductor that runs groom-backlog (merges small or same-cause tasks under the shared 15-task ceiling), then audit-tests (30-second routine run, 10-e2e cap). Use between build runs; name one half (backlog | tests) to run it alone; autopilot applies everything without pausing."
argument-hint: "[autopilot] [backlog | tests]"
---

# Optimize Dev Skill (orchestrator)

You are the maintenance conductor for the two places hygiene decays — a fragmenting backlog and a
slowing test suite. Sequence the two sub-skills, pass the mode down, merge their reports; never groom
or optimize anything yourself.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to each
sub-skill.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — what exists (backlog? tests?), scope argument, autopilot argument
- [ ] Stage 1: Groom — invoke groom-backlog (skipped: no backlog, or scope says tests)
- [ ] Stage 2: Tests — invoke audit-tests (skipped: no tests, or scope says backlog)
- [ ] Stage 3: Close — one merged report + one «What you should do»
```

### Stage 0: Intake
Check for a backlog (`.dev-skills/build-plan/tasks/` non-empty) and tests (a test directory or runner
config anywhere). `backlog` or `tests` narrows the pass to that half; a half whose subject is
absent is skipped — **announced in one line, never silently**. Nothing to do → say so and stop. Carry
the `autopilot` argument, if given, into every sub-skill invocation.

### Stage 1: Groom the backlog
Invoke **`dev-skills:groom-backlog`** (with `autopilot` when given). It sizes the open tasks, builds
the merge plan, holds its own confirmation gate, applies, reports. Collect its summary — open count
before/after and anything flagged.

### Stage 2: Audit the tests
Invoke **`dev-skills:audit-tests`** (with `autopilot` when given). It measures against the budgets,
holds its own gate, applies, re-measures, writes `.dev-skills/optimize/test-audit.md`. Collect its
summary — before/after wall-clocks, e2e count, filed tasks.

### Stage 3: Close
One short combined report: what each half found and changed (backlog N → M open tasks; routine run
Xs → Ys, e2e K → L), what was skipped and why, wall-clock per half reconciling with the total
(**`../_shared/build-pipeline/report-format.md`**). Then **one** merged «What you should do» — the
sub-skills' items combined, deduplicated, renumbered; "nothing" is valid.

## Rules

1. **Conduct, don't duplicate.** Merge rules live in `groom-backlog`/`planning-method.md`, budgets in
   `audit-tests`/`verification.md`; restate neither, do neither yourself.
2. **The sub-skills own their confirmation gates** — never pre-approve for them; `autopilot` is passed
   through verbatim, never invented.
3. **Skipping is announced**, one line with the reason.
4. **Backlog first, then tests** — grooming is cheap and frames the report; the test audit is the long
   half.
5. **One merged closing report, one «What you should do».**
