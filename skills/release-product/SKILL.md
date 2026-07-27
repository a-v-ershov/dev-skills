---
name: release-product
disable-model-invocation: true
description: "Take a built, verified product to a cut release. Use after build-tasks, as the release phase — the third pipeline, after the project-spec and build phases. A thin orchestrator: it reads the spec's quality-attribute contracts and runs the system-level audits (audit-security / audit-performance / audit-product / audit-code-health / audit-accessibility) as fresh, independent subagents in PARALLEL (they are read-only — they mutate nothing and collide on nothing), collects and ranks their findings by severity, files blockers/majors as rework tasks into the backlog (via plan-development's amend mode), drives a build-tasks run to fix them and re-audits — bounded by max_audit_iterations — until clean or escalated, then invokes cut-release (version + changelog + release notes + tag + commit + PR, always with confirmation, stopping before prod deploy). Audits never fix code; the cut is the only outward-facing step and always stops for the human. Resumable: the findings docs + backlog are the source of truth. Conducts the focused sub-skills; it does not duplicate their logic."
argument-hint: "[--audit <name>] [--skip-ship]"
---

# Release Product Skill (orchestrator)

You are the release captain. You do not audit, fix, or ship yourself — you read the spec's contracts,
spawn each audit as a **fresh, independent subagent**, collect and rank what they find, route fixes
through the build pipeline, and — only when the system is clean — invoke `cut-release`. The audits are
**read-only** and run in **parallel**: they mutate nothing, so they collide on nothing. This is the one
place the release phase parallelizes where the build phase deliberately did not. The findings docs + the
backlog are the source of truth, so you can be killed and resumed.

The loop:

```
spawn all enabled audits in parallel (read-only, fresh agents)
   → collect findings → rank (severity-rubric)
   → any open 🔴/🟡?  → file rework tasks (plan-development amend) → build-tasks fixes → re-audit  ⟲
                        (bounded by max_audit_iterations; a 🔴 at the cap → needs_human, stop)
   → clean (no open 🔴)?  → cut-release (version + changelog + notes + tag + PR, always confirmed)
   → build .dev-skills/release/release-summary.md
```

The audits are sub-skills run as **subagents** (one fresh agent each, via the Agent/Skill tool). Static
audits (`audit-security`, `audit-code-health`) fan out freely; **dynamic audits that drive the running
stack (`audit-performance`, `audit-product`) acquire the env lease** themselves
(`../_shared/build-pipeline/env-access.md`), so they self-serialize on the one running stack. You hold
none of an audit's context — just the backlog state and the findings verdicts.

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill follows the same rule
on its own. Never translate code, identifiers, commands, or file paths. (Commit messages are always
English — the `commit` skill, invoked by `cut-release`, enforces that.)

## Modes

Read `.dev-skills/release/.release-config.md` for `mode`, `max_audit_iterations`, and the enabled `audits`. If
absent, ask once (defaults: interactive + 3 + all applicable) and write it. Full rules:
**`../_shared/release-pipeline/release-config.md`**. The audit machine, severity, and report shapes:
**`../_shared/release-pipeline/audit-method.md`**, **`severity-rubric.md`**, **`report-template.md`**.

- **interactive** — present the audit plan and confirm; stop at each 🔴, before filing rework, and
  before `cut-release`.
- **autopilot** — run audit → fix → re-audit back-to-back without stopping; **except** the two things
  that always stop: a 🔴 surviving the cap (`needs_human`), and `cut-release` itself.

## Procedure

```
- [ ] Step 0: Intake — confirm build is complete; read the spec contracts + .release-config.md (write if absent); detect resume
- [ ] Step 1: Audit — spawn the enabled audits in parallel (fresh agents); collect findings docs + verdicts
- [ ] Step 2: Triage — rank all findings; file 🔴/🟡 as rework tasks (plan-development amend); ⚪ logged only
- [ ] Loop: build-tasks fixes the rework → re-run only the affected audits → repeat until clean or cap (needs_human)
- [ ] Step 3: Cut — no open 🔴 → invoke cut-release (always confirmed); honor --skip-ship to stop at audits
- [ ] Done: build release-summary.md; refresh the project documentation map; report verdict + filed tasks + what shipped
```

### Step 0: Intake + resume
Confirm the build phase is done (the backlog `.dev-skills/build-plan/board.md` shows no `ready`/`in_progress`
feature tasks left, or the user says so). Read the spec contracts each audit needs
(`.dev-skills/project-spec/architecture.research.md`, `design-decisions.research.md`, `user-flows.research.md`)
and `.dev-skills/project-setup/verification.md` (how to bring the stack up + drive it). Read
`.release-config.md` (write it if absent). **Detect resume:** existing `.dev-skills/release/*-audit.md` with a
clean verdict need not re-run unless their tasks changed; open rework tasks left by a killed run resume
where they are. Honor `--audit <name>` (run just that one) and `--skip-ship` (audits only, no cut).

### Step 1: Audit (parallel fan-out)
Spawn each enabled audit as a **fresh subagent**. They are independent and read-only → launch them
together. Each reads its contract, probes, proves, ranks, writes `.dev-skills/release/<noun>-audit.md`, and
returns its verdict (clean / N blockers / N majors). A `--skip-ship` run ends after this step with the
summary. **A sub-skill not yet available in this collection is a stop condition** regardless of mode:
report it and let the user decide whether to skip that audit or build the skill first.

### Step 2: Triage + the fix loop
Collect every findings doc. The audits already filed 🔴/🟡 as rework tasks (`type: rework`, via
`plan-development`'s amend mode) and ranked per **`severity-rubric.md`**; you reconcile and present the
combined picture. In interactive, confirm before the fix run; before any **destructive** backlog change
(cancelling/reopening a `done` task) always stop, in both modes. Then:

1. **Fix** — invoke `build-tasks` to drive the open rework tasks (it implements + verifies each, as
   usual). You do not fix anything yourself.
2. **Re-audit** — re-run **only the audits whose findings were addressed**, as fresh agents, to confirm
   the contract is now upheld (proven, not assumed). Each round bumps that audit's iteration count.
3. **Repeat** until no open 🔴 remains. When an audit's 🔴 survives `max_audit_iterations`, it escalates
   to `needs_human` — surface it and stop the loop for that audit (both modes). Open 🟡 do not block;
   record them for the human's call.

### Step 3: Cut (the only outward-facing step)
When no open 🔴 remains (and `--skip-ship` was not set), invoke `cut-release`. It confirms the tree is
clean and no blocker is open, then updates docs + version + changelog + release notes, tags, commits,
and opens the PR — **always with explicit confirmation, in both modes** (`careful`). It stops before any
production deploy (out of scope by design). If `cut-release` is not yet available, report that the
release is audit-clean and ready to cut by hand, and stop.

### Done: summary + handoff
Build `.dev-skills/release/release-summary.md` (**`report-template.md`**) — decisions-first: the verdict, open
blockers + any waivers (the human's action list), the rework filed, the audits run with their verdicts,
and what shipped if `cut-release` ran. Do not re-derive — roll up each audit's verdict + the cut result.
Then **refresh the project documentation map** block in the root `CLAUDE.md` so `.dev-skills/release/` shows up
— idempotent, only between the markers, per **`../_shared/agent-guide.md`** (this is the release phase's
primary map refresh; it runs even under `--skip-ship`, where `cut-release` never does). Report the paths
and hand off.

## Rules

1. **Conduct, don't duplicate.** Never audit, fix, or ship yourself — spawn the `audit-*` subagents,
   invoke `build-tasks` for fixes and `cut-release` for the ship.
2. **Audits are read-only and parallel.** They mutate nothing → run them together. They never edit
   product code — they file rework tasks; `build-tasks` fixes them.
3. **Re-audit after every fix.** A contract is upheld only when an audit proves it again — never assume a
   fix worked. Bound the loop by `max_audit_iterations`; escalate to `needs_human` at the cap.
4. **Only a 🔴 blocks the cut.** Majors are filed, not blocking; minors are logged. Severity follows the
   shared rubric, against the contract — not taste.
5. **The cut always stops for the human.** `cut-release` confirms before acting in both modes, and stops
   before production deploy.
6. **Resume, don't restart.** Reuse a clean audit verdict and in-flight rework; never re-run a settled
   audit or rebuild a finished fix without reason.
7. **release-summary.md is always rolled up** from the findings docs + the cut result; never hand-authored
   from scratch.
