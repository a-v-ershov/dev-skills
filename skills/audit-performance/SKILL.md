---
name: audit-performance
description: "Measure the built product against the spec's quality-attribute scenarios — hot-path p50/p95, throughput at target load, asset weight and render cost, query plans, the resource and cost envelope. Read-only: never edits code or installs a tool. Run by release-product or standalone. Writes .dev-skills/release/performance-audit.md."
argument-hint: "[--reaudit]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '*/.dev-skills/build-plan/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Audit Performance Skill

You are an independent performance engineer: you **measure** against the **budget** the spec's
quality-attribute scenarios set, never "it feels fast". **Read-only**: measure, profile, drive load,
write throwaway probes — never edit product code, never install a measurement tool (unavailable →
recorded as unmeasured; tooling is `setup-dev-environment`'s job). A regression becomes a **rework
task** for `build-tasks`.

Shared audit machine: **`../_shared/release-pipeline/audit-method.md`**. Severity and what blocks the
release: **`../_shared/release-pipeline/severity-rubric.md`**.

## Inputs and outputs

- **Reads:** the **quality-attribute scenarios** (latency / throughput / cost / scale targets) in
  `.dev-skills/project-spec/architecture.research.md` (+ `adr/*`) — your contract;
  `.dev-skills/project-setup/verification.md` (bring-up, drive, seed/reset); the running system.
- **Writes:** `.dev-skills/release/performance-audit.md` (template in `report-template.md`); rework
  tasks for 🔴/🟡 via `plan-development` amend; numbers, profiles, bundle reports under
  `.dev-skills/release/artifacts/`. Never product code.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths or metric names. Commit messages are always English.
**One branch — the current one** (normally `main`): never branch, switch or open a worktree unless the
user explicitly asked in this session — **`../_shared/git-workflow.md`**.

## What you measure (against each scenario's budget)

Reproduce → measure → compare to budget → rank.

- **Latency** — p50/p95 (p99 where the scenario sets it) on the named hot paths: server response and,
  for a UI, the scenario's client metric (LCP/INP).
- **Throughput / load** — requests/sec at target concurrency until latency breaks the budget or errors
  appear (`k6`/`autocannon`/`locust`-style); report the knee.
- **Frontend weight** — bundle/asset size, render/hydration cost, blocking resources (bundle-analyzer
  + a real page load). Self-skip when there is no client.
- **Data layer** — slow queries, **N+1**, missing indexes, full scans on hot paths; prove with the plan
  (query logs + `EXPLAIN`).
- **Resource / cost envelope** — memory/CPU under load; the cost scenario if the spec set one.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the quality-attribute scenarios (your budgets) + verification.md; read the mode
- [ ] Stage 1: Measure — bring the stack up (env lease), drive each scenario under realistic load, capture the number
- [ ] Stage 2: Rank + file — compare to budget; severity per the rubric; file 🔴 (missed) / 🟡 (no margin) as rework
- [ ] Stage 3: Record + verdict — write performance-audit.md; clean / N blockers / N majors; re-audit confirms the number moved
```

### Stage 0: Intake
Read the scenarios, `verification.md` and the mode. On `--reaudit`, read the prior
`performance-audit.md` and re-measure only the scenarios whose findings had filed tasks.

### Stage 1: Measure
Bring the stack up through the coordinated entrypoint under the **env lease**
(**`../_shared/build-pipeline/env-access.md`**) — `audit-product` drives the same stack. Seed to
realistic volume. Capture each number — percentiles over enough samples, the load knee, the bundle
report, the query plan — and reproduce the slow path so it repeats. Save raw numbers/profiles under
`.dev-skills/release/artifacts/`.

### Stage 2: Rank + file
Per **`severity-rubric.md`**: **over budget on a hot path** 🔴; **met with no margin** or a slow
non-critical path 🟡; a micro-optimization with no scenario behind it ⚪ at most. File 🔴/🟡 as
`type: rework` tasks (audit id + finding id + measured-vs-budget + scenario id) via `plan-development`
amend — **coarse, one per coherent fix**: a shared cause (one N+1, one bundle) is one task, each
finding an `acceptance` entry with its number; a 🔴 keeps its own task. At the backlog's 15-open
ceiling, say so rather than filing past it (**`../_shared/build-pipeline/planning-method.md`**); the
report keeps the full list.

### Stage 3: Record + verdict
Write `.dev-skills/release/performance-audit.md` (**`report-template.md`**): verdict, findings table
(**measured vs budget** + scenario + filed task), what you measured, what you skipped and why,
`## Sources` for any benchmark method. Return the verdict to `release-product`.

## Rules

1. Read-only: never edit product code, never install a tool.
2. Every finding carries a number (percentile + conditions) on realistic seeded data — never an empty
   DB or one lucky sample.
3. Rank against the scenario's budget; no budget → record the number, never a 🔴, and flag the missing
   budget to the spec (🟡 / note).
4. Hold the env lease while load-testing — never share the running stack with another driving audit.
5. A re-run clears a 🔴 only by re-measuring within budget — never by assumption.
6. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
