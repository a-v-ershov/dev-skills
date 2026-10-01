# Audit method (shared — release pipeline)

How a system-level quality attribute is proven at the release boundary. An **audit** is the release
counterpart to `verify-feature`: that proves one task's **acceptance criteria**; an audit proves an
**emergent, cross-cutting property of the whole system** (security, performance, end-to-end product
behavior). Each `audit-*` skill runs this machine and references this file.

The release chain has two halves: `refactor` and `write-tests` change the repository and run first,
sequentially and alone; then the audits, which change nothing, run in parallel. This file governs
the audits.

## Why a separate, fresh, independent agent

`release-product` spawns each audit as a **fresh top-level subagent** with no memory of who wrote the
code, so it doesn't assume the system works and starts from the **contract, not the
implementation** — the one the spec phase wrote:

| Audit | Contract it proves against (from the spec) |
|-------|--------------------------------------------|
| `audit-security` | the STRIDE-lite threat model + trust boundaries in `.dev-skills/project-spec/architecture.research.md`, plus the production surfaces the deployment decisions imply |
| `audit-performance` | the quality-attribute scenarios (latency, throughput, cost, scale) in `.dev-skills/project-spec/architecture.research.md` |
| `audit-product` | the user flows + their acceptance criteria in `.dev-skills/project-spec/user-flows.research.md`, **and** the accessibility decisions in `design-decisions.research.md` (both are proven by driving the same running product) |
| `audit-dependencies` | the dependency manifests + lockfiles against the ecosystems' advisory databases, and the stack decisions/constraints in `architecture.research.md` — the one fully static audit: it needs no running stack and no env lease |

Contract doc missing → say so, prove against sensible defaults for the domain and record the gap;
**never** invent a contract and pass against it silently.

## Read-only: findings, never fixes — and never setup

An audit **reads** the system and **writes only two things**: its findings doc and rework tasks in
the backlog. Two hard limits:

- **It never edits the product's code.** Fixing is a separate `build-tasks` run on the tasks it files
  (the writer/reviewer split that keeps `verify-feature` honest).
- **It never installs or configures anything** — no analyzer, error tracker, spending cap or missing
  environment variable. Local tooling belongs to `setup-dev-environment`, the production side to
  `setup-production-environment`; a missing capability is **recorded as a finding** naming the
  owning skill.

It may *run* already-installed read-only tools, take measurements, drive the app or write a
throwaway probe script — never change the product or its environment to make a finding go away.

## The loop (read contract → probe → prove → rank → file)

Per contract item:

0. **Read the contract** — the scenario / threat / decision / flow (table above) — and the system as
   the domain needs (a static read, the dependency graph, the running stack).
1. **Probe** — run the analyzer, measure the number, drive the flow, reproduce the attack. Static
   audits read; **dynamic audits (performance, product) bring the stack up through the coordinated
   entrypoint** (env lock / per-run isolation — `../build-pipeline/env-access.md`) so parallel audits
   don't collide on one running stack.
2. **Prove** — capture a **real, observable outcome**: a measured p95, a secret at `file:line`, a
   reproduced 500, a failing axe rule with its node. **"Looks fine" / "no obvious issue" is not a
   verdict** — a pass is proven and a fail is proven.
3. **Rank** — severity per `severity-rubric.md` (🔴 blocker / 🟡 major / ⚪ minor) against the
   contract, not taste. Save evidence under `.dev-skills/release/artifacts/`.

## Filing rework (how a finding becomes a fix)

The audit does not fix; it **files**:

- **🔴 blocker / 🟡 major** → a **rework task** via `plan-development`'s amend mode (`type: rework`,
  tagged with the audit + finding id, the evidence link and the contract item it restores).
  `build-tasks` fixes it; the audit **re-runs once** afterwards (the orchestrator drives that round).
- **⚪ minor** → findings doc only; no task.
- **A missing production capability** (no hard spend cap, no error tracking, no rate limit, a variable
  unset in the target environment) → a finding **owned by `setup-production-environment`**, not filed
  against the code.

**Group findings into coarse tasks — one task per coherent fix, not one per finding.** The backlog is
one board with **one ceiling of 15 open tasks**, shared with the build phase
(**`../build-pipeline/planning-method.md`**, "This applies to everyone who files a task"):

- Findings in the same surface, with the same cause, or that one agent would close in one sitting are
  **one** task; each finding becomes its own `acceptance` entry with its evidence link, verified
  separately.
- Keep a 🔴 in its own task so it can be fixed and re-audited alone; split when one sitting can't
  hold the work.
- If the honest grouping still overflows the ceiling, say so and confirm the count — never file past
  it silently.

The findings doc keeps the **full, ungrouped list** (grouping schedules the work, it doesn't record
it); each finding's row names the task it was filed under.

## One round, then a decision (no loop)

After the fix run, the affected audits re-run **once**. Whatever is still open becomes a
`needs_human` escalation — no iteration counter, no second round; a finding that survives a targeted
fix and a re-audit is a signal about the product. Same bound as the build loop
(`../build-pipeline/verification-method.md`).

## Recording — the findings doc

Write `.dev-skills/release/<noun>-audit.md` (template: `report-template.md`): verdict (clean / N
blockers / N majors), a findings table (id · severity · what · evidence · contract item · filed
task), what was checked, what was **skipped and why** (a silent cap reads as "all clear"), and a
`## Sources` section for any world-claim. Committed — the audit trail of *why the release was, or
wasn't, cut*.

## What an audit is NOT

- Not the builder grading its own work — a separate, fresh agent.
- Not a code fix — it files tasks; `build-tasks` fixes them.
- Not a setup step — a missing capability is a finding.
- Not "ran the tool, no crash" — the contract item's proven outcome is the verdict.
- Not a gap-hunt for its own sake — flag only what the contract demands (`severity-rubric.md`).
