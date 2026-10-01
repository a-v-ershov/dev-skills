---
name: release-product
description: "Take a built, verified product to a cut release (third pipeline, after build-tasks). Orchestrates refactor then write-tests in agents, sequentially; the read-only audits and simplify-product in parallel; write-readme and manual-test. Files 🔴/🟡 as coarse rework, ONE build-tasks fix round, ONE re-audit; the rest is needs_human. Ends in cut-release."
argument-hint: "[--only <step>] [--skip-ship]"
---

# Release Product Skill (orchestrator)

You are the release captain: you never refactor, test, audit, fix or ship yourself — you sequence the
sub-skills, rank their findings, route fixes through the build pipeline and, once clean, invoke
`cut-release`. The findings docs and the backlog are the source of truth; you can be killed and resumed.

The chain has two halves: the steps that change the repo (`refactor`, then `write-tests`) run
**sequentially and alone**, each in its agent; the read-only audits then **fan out in parallel**.
`manual-test` runs last so its briefing matches the tree the human will open.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English (the `commit`
skill, via `cut-release`). **One branch — the current one** (normally `main`): never branch, switch or
open a worktree unless the user explicitly asked in this session — **`../_shared/git-workflow.md`**.
Pass both rules to every agent you spawn.

## Modes

Read `mode` and the enabled `steps` from `.dev-skills/release/.release-config.md`; if absent, ask once
(defaults: interactive + all applicable) and write it
(**`../_shared/release-pipeline/release-config.md`**). Audit machine, severity, report shapes:
**`../_shared/release-pipeline/audit-method.md`**, **`severity-rubric.md`**, **`report-template.md`**.

- **interactive** — present the chain and confirm; stop at each 🔴, before filing rework, before
  `cut-release`.
- **autopilot** — run back-to-back, **except** the three things that always stop: the refactor plan's
  approval, an open finding after the single fix round (`needs_human`), `cut-release` itself.

## Procedure

```
- [ ] Step 0: Intake — confirm the build is complete; read the spec contracts + .release-config.md (write if absent); detect resume
- [ ] Step 1: Repo steps, in order and alone — refactorer agent (plan → approval → execute), then test-writer agent
- [ ] Step 2: Audits — spawn audit-security · audit-performance · audit-product · audit-dependencies · simplify-product in parallel (fresh agents)
- [ ] Step 3: Handover + briefing — /write-readme, then /manual-test for the human's hands-on pass
- [ ] Step 4: Triage — rank all findings; file 🔴/🟡 as rework tasks (plan-development amend); ⚪ logged only
- [ ] Step 5: One fix round — build-tasks fixes the rework → re-run ONLY the affected audits, once → still open = needs_human
- [ ] Step 6: Cut — no open 🔴 → invoke cut-release (always confirmed); honor --skip-ship
- [ ] Done: build release-summary.md; refresh the project documentation map; report the verdict, the filed tasks, and the handoff
```

### Step 0: Intake + resume
Confirm the build is done (`.dev-skills/build-plan/board.md` shows no `ready`/`in_progress` feature
tasks, or the user says so). Read `.dev-skills/project-spec/architecture.research.md`,
`design-decisions.research.md`, `user-flows.research.md`, `.dev-skills/project-setup/verification.md`
(how to bring the stack up and drive it) and `.release-config.md` (write if absent). **Resume:** a
`.dev-skills/release/*.md` with a clean verdict is not re-run unless its tasks changed; open rework from
a killed run resumes where it is. Honor `--only <step>` (just that step) and `--skip-ship` (everything
except the cut).

### Step 1: The repo steps (sequential, alone)
**refactor**, then **write-tests**, each in its own named agent, one at a time, never in parallel with
anything.

- **Refactor = two spawns of the `refactorer` agent** (`subagent_type: refactorer`). **Plan** phase: it
  checks the safety net (refuses a red suite — fix that first via `run-task`), measures, writes the
  "before" signals into `.dev-skills/release/refactor.md` and returns the ranked plan **without
  executing**. Show it to the human and wait for approval **in both modes** — never pre-approve. Then
  **execute** phase with the approved items, one at a time with the gate after each (a large plan →
  several sequential execute spawns, one batch each).
- **`test-writer` agent, once** (`subagent_type: test-writer`). A **red** suite at the end is a
  *result*: it found a real bug and filed a task — treat those as findings in Step 4, not a broken run.
  Surface its prune proposals to the human; nothing is deleted silently.

### Step 2: Audits (parallel fan-out)
Spawn each enabled audit as a **fresh subagent**, all together. Each reads its contract, probes,
proves, ranks, writes `.dev-skills/release/<noun>-audit.md` and returns clean / N blockers / N majors.
The dynamic ones (`audit-performance`, `audit-product`) take the env lease themselves
(**`../_shared/build-pipeline/env-access.md`**). **`simplify-product` rides along but is not an
audit**: it writes `.dev-skills/release/simplification-proposals.md` and returns «N proposals, none
blocking» — nothing filed. **A sub-skill missing from this collection is a stop condition** in both
modes: report it, let the user skip or build it.

### Step 3: Handover document, then the human's briefing
Invoke **`/write-readme`**: it refreshes `README.md` against the current tree (clone → run, deploying,
what to bring, clean seeded state), every command verified, read-only on product code. Then
**`/manual-test`**, which proves and changes nothing: it writes `.dev-skills/release/manual-test-brief.md`
so the human can check by hand what no machine decides, `review: auto` items first. A handoff, not a
gate: never blocks the cut, always in the summary.

### Step 4: Triage
Collect every findings doc. The audits (and `refactor` / `write-tests`, for what they found and did not
fix) already filed 🔴/🟡 as `type: rework` tasks via `plan-development` amend, ranked per
**`severity-rubric.md`**; you reconcile and present the combined picture.

- **Reconcile the grain** (**`../_shared/build-pipeline/planning-method.md`**): audits cannot see each
  other — merge tasks for one surface or cause, each finding its own `acceptance` entry; a 🔴 keeps its
  own task. Over **15 open tasks** → confirm the count with the human. Interactive: confirm before the
  fix run. A **destructive** backlog change (cancelling or reopening a `done` task) always stops, in
  both modes.
- **Simplification proposals:** present them numbered; file **only the numbers the human picks** as
  rework (autopilot files none). Unpicked ones go into the summary's «What you should do», never the
  backlog. No severity, never 🔴/🟡, never block the cut.
- A missing production capability (no hard spend cap, error tracking, rate limit) is **not** code
  rework: route it to `/setup-production-environment` and name it so in the summary.

### Step 5: One fix round (no loop)
1. **Fix** — invoke `build-tasks` once over the open rework. You fix nothing yourself.
2. **Re-run** — **only** the steps whose findings were addressed, as fresh agents: proven, not assumed.
3. **Decide.** Still open → **`needs_human`**, surface it and stop, in both modes; no counter, no second
   round (**`../_shared/build-pipeline/verification-method.md`**). Open 🟡 do not block — record them
   for the human's call.

### Step 6: Cut (the only outward-facing step)
No open 🔴 and no `--skip-ship` → invoke `cut-release`: clean tree + no open blocker, then docs +
version + changelog + release notes, tag, commit, PR — **always confirmed, in both modes** — stopping
before production. If `cut-release` is unavailable, report the release audit-clean and ready to cut by
hand.

### Done: summary + handoff
Build `.dev-skills/release/release-summary.md` (**`report-template.md`**), decisions-first: verdict,
open blockers and waivers (the human's action list), rework filed, each step's verdict, the hands-on
briefing, what shipped — rolled up, never re-derived. Refresh the **project documentation map** block
in the root `CLAUDE.md` (idempotent, between the markers, **`../_shared/agent-guide.md`**; also under
`--skip-ship`). Hand off the human's two items: the `manual-test` pass and, when going live,
`/setup-production-environment` — never auto-run from here.

## Rules

1. **Conduct, don't duplicate** — agents do the work; `build-tasks` fixes, `cut-release` cuts.
2. **Repo steps sequentially and alone, each finished before the next; audits in parallel.**
3. **Audits never fix and never install** — what is missing is a finding. Code → `build-tasks`;
   tooling → `setup-dev-environment`; production → `setup-production-environment`.
4. **One fix round, then a decision.** Re-run only what was addressed, once; still open = `needs_human`.
5. **Only a 🔴 blocks the cut.** Majors filed, minors logged; severity per the rubric, not taste.
6. **Simplification proposals are filed only on the human's explicit pick**, in both modes.
7. **The cut always stops for the human**, in both modes, and before production.
8. **Going live is not part of this run** — `setup-production-environment` is invoked by hand.
9. **Resume, don't restart.** Reuse clean verdicts and in-flight rework; never re-run a settled step
   without reason.
10. **release-summary.md is always rolled up** from the step outputs and the cut result.
11. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
