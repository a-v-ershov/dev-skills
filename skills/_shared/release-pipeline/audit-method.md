# Audit method (shared — release pipeline)

How a system-level quality attribute is proven at the release boundary. An **audit** is the release
phase's counterpart to the build phase's `verify-feature`: where `verify-feature` proves one task's
**acceptance criteria**, an audit proves an **emergent, cross-cutting property of the whole system**
(security, performance, accessibility, end-to-end product behavior, code health) — the kind no single
task could prove. Each `audit-*` skill runs this same machine and references this file rather than
restating it.

## Why a separate, fresh, independent agent

`release-product` spawns each audit as a **fresh top-level subagent** with no memory of who wrote the
code. That independence is the point — an auditor that did not build the system does not assume it
works, and starts from the **contract, not the implementation**. The contract already exists: the spec
phase wrote it.

| Audit | Contract it proves against (from the spec) |
|-------|--------------------------------------------|
| `audit-security` | the STRIDE-lite threat model + trust boundaries in `.dev-skills/project-spec/architecture.research.md` |
| `audit-performance` | the quality-attribute scenarios (latency, throughput, cost, scale) in `.dev-skills/project-spec/architecture.research.md` |
| `audit-accessibility` | the accessibility decisions in `.dev-skills/project-spec/design-decisions.research.md` |
| `audit-product` | the user flows + their acceptance criteria in `.dev-skills/project-spec/user-flows.research.md` |
| `audit-code-health` | the quality bar — the gate config + the codebase's own conventions |

If the contract doc is missing, the audit says so and proves against sensible defaults for its domain,
recording the gap — it does **not** invent a contract and pass against it silently.

## Read-only: findings, never fixes

An audit **reads** the built system and **writes only two things**: its findings doc and rework tasks in
the backlog. It **never edits the product's code** — fixing is a separate `build-tasks` run on the
tasks it files. This is the same writer/reviewer split that keeps `verify-feature` honest: the side
whose job is to find failure does not also get to declare it fixed.

(An audit may *run* read-only analysis tools, take measurements, drive the app, or write a throwaway
probe script — but it does not change the product to make a finding go away.)

## The loop (read contract → probe → prove → rank → file)

For each item in its contract the audit produces evidence, then ranks it:

0. **Read the contract** — the scenario / threat / decision / flow this audit must hold the system to
   (table above). Read the system the way the audit's domain needs (a static read, the dependency
   graph, the running stack).
1. **Probe** — exercise the property: run the analyzer, measure the number, drive the flow, reproduce
   the attack. Static audits read; **dynamic audits (performance, product) bring the stack up through
   the coordinated entrypoint** (env lock / per-run isolation — `../build-pipeline/env-access.md`) so
   audits running in parallel don't collide on one running stack.
2. **Prove** — capture a **real, observable outcome**: a measured p95, a secret at `file:line`, a
   reproduced 500, a failing axe rule with its node, a duplicate-block report. **"Looks fine" / "no
   obvious issue" is not a verdict** — a pass is proven and a fail is proven.
3. **Rank** — assign severity per `severity-rubric.md` (🔴 blocker / 🟡 major / ⚪ minor) against the
   contract, not against taste. Save evidence under `.dev-skills/release/artifacts/`.

## Filing rework (how a finding becomes a fix)

The audit does not fix; it **files**:

- **🔴 blocker / 🟡 major** → file a **rework task** into the backlog via `plan-development`'s amend
  mode (`type: rework`, tagged with the audit + finding id, the evidence link, and the contract item it
  restores). `build-tasks` later fixes it; the audit **re-runs** afterwards to confirm (the
  orchestrator drives this loop, bounded by `max_audit_iterations`).
- **⚪ minor** → recorded in the findings doc only; no task.

A 🔴 that survives `max_audit_iterations` rounds becomes a `needs_human` escalation — never an infinite
audit↔fix loop.

## Recording — the findings doc

Write `.dev-skills/release/<noun>-audit.md` (template: `report-template.md`): the verdict (clean / N blockers /
N majors), a findings table (id · severity · what · evidence · contract item · filed task), what was
checked, what was **skipped and why** (a silent cap reads as "all clear" when it isn't), and a
`## Sources` section for any world-claim the audit leaned on. This doc is committed project
documentation — the audit trail of *why the release was, or wasn't, cut*.

## What an audit is NOT

- Not the builder grading its own work — a separate, fresh agent.
- Not a code fix — it files tasks; `build-tasks` fixes them.
- Not "ran the tool, no crash" — the contract item's proven outcome is the verdict.
- Not a gap-hunt for its own sake — flag only what the contract demands (`severity-rubric.md`).
