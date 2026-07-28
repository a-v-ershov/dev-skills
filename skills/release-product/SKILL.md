---
name: release-product
disable-model-invocation: true
description: "Take a built, verified product to a cut release. Use after build-tasks, as the release phase — the third pipeline, after the project-spec and build phases. A thin orchestrator that runs the release chain in one command: first the two steps that change the repository, strictly in order — refactor (clean the structure without changing behaviour) then write-tests (map the test gaps and close the risky ones, red-first) — and then the read-only audits as fresh, independent subagents in PARALLEL (audit-security, audit-performance, audit-product), since they mutate nothing and collide on nothing, and finally manual-test to brief the human on what only a person can judge. It collects and ranks every finding by severity, files blockers and majors as rework tasks into the backlog, drives ONE build-tasks run to fix them and re-runs only the affected audits ONCE to confirm; anything still open after that round is needs_human, never another loop. When no blocker remains it invokes cut-release (version + changelog + release notes + tag + commit + PR, always confirmed) and stops there: putting the product live is setup-production-environment's job, invoked by hand. Audits only audit — they never fix code and never install anything; a missing production capability is a finding that goes back to setup-production-environment. Resumable: the findings docs plus the backlog are the source of truth. It conducts the focused sub-skills; it does not duplicate their logic."
argument-hint: "[--only <step>] [--skip-ship]"
---

# Release Product Skill (orchestrator)

You are the release captain. You do not refactor, write tests, audit, fix, or ship yourself — you
sequence the focused sub-skills, collect and rank what they find, route fixes through the build
pipeline, and — only when the system is clean — invoke `cut-release`. The findings docs and the backlog
are the source of truth, so you can be killed and resumed.

The chain:

```
1. refactor            (changes code — alone, first: everything downstream reads the cleaned tree)
2. write-tests         (changes tests — alone, second: the audits should run against the real net)
3. audit-security · audit-performance · audit-product   ← fresh agents, IN PARALLEL (read-only)
4. manual-test         (read-only briefing for the human)
   → collect findings → rank (severity-rubric) → file 🔴/🟡 as rework tasks
   → ONE build-tasks run → re-run ONLY the affected audits, ONCE
   → still open?  → needs_human, surface it, stop
   → no open 🔴?  → cut-release (version + changelog + notes + tag + PR, always confirmed)
   → build .dev-skills/release/release-summary.md
```

**Why that order.** The first two steps mutate the working tree, so they run **sequentially and alone** —
a refactor moving code under a running audit is how a release phase produces nonsense. The audits mutate
nothing, so they **fan out**: this is the one place the workflow parallelizes where the build phase
deliberately did not. `manual-test` runs last because its briefing should describe the tree the human
will actually open. Dynamic audits that drive the running stack (`audit-performance`, `audit-product`)
**acquire the env lease** themselves (`../_shared/build-pipeline/env-access.md`), so they self-serialize
on the one running stack while the static ones run freely.

**Audits only audit.** They never edit product code and **never install or configure anything** —
tooling belongs to `setup-dev-environment`, production capabilities to `setup-production-environment`.
An audit that needs something that does not exist records it as a finding.

## Language

Respond and reason in whatever language the user addressed you in. Each sub-skill follows the same rule
on its own. Never translate code, identifiers, commands, or file paths. (Commit messages are always
English — the `commit` skill, invoked by `cut-release`, enforces that.)

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Modes

Read `.dev-skills/release/.release-config.md` for `mode` and the enabled `steps`. If absent, ask once
(defaults: interactive + all applicable) and write it. Full rules:
**`../_shared/release-pipeline/release-config.md`**. The audit machine, severity, and report shapes:
**`../_shared/release-pipeline/audit-method.md`**, **`severity-rubric.md`**, **`report-template.md`**.

- **interactive** — present the chain and confirm; stop at each 🔴, before filing rework, and before
  `cut-release`. `refactor` presents its own plan and waits, in both modes.
- **autopilot** — run the chain back-to-back without stopping; **except** the three things that always
  stop: `refactor`'s plan, an open finding after the single fix round (`needs_human`), and `cut-release`
  itself.

## Procedure

```
- [ ] Step 0: Intake — confirm the build is complete; read the spec contracts + .release-config.md (write if absent); detect resume
- [ ] Step 1: Repo steps, in order and alone — /refactor, then /write-tests
- [ ] Step 2: Audits — spawn audit-security · audit-performance · audit-product in parallel (fresh agents)
- [ ] Step 3: Briefing — /manual-test for the human's hands-on pass
- [ ] Step 4: Triage — rank all findings; file 🔴/🟡 as rework tasks (plan-development amend); ⚪ logged only
- [ ] Step 5: One fix round — build-tasks fixes the rework → re-run ONLY the affected audits, once → still open = needs_human
- [ ] Step 6: Cut — no open 🔴 → invoke cut-release (always confirmed); honor --skip-ship
- [ ] Done: build release-summary.md; refresh the project documentation map; report the verdict, the filed tasks, and the handoff
```

### Step 0: Intake + resume
Confirm the build phase is done (`.dev-skills/build-plan/board.md` shows no `ready`/`in_progress`
feature tasks left, or the user says so). Read the contracts the steps need
(`.dev-skills/project-spec/architecture.research.md`, `design-decisions.research.md`,
`user-flows.research.md`) and `.dev-skills/project-setup/verification.md` (how to bring the stack up and
drive it). Read `.release-config.md` (write it if absent). **Detect resume:** an existing
`.dev-skills/release/*.md` with a clean verdict need not re-run unless its tasks changed; open rework
tasks left by a killed run resume where they are. Honor `--only <step>` (run just that one) and
`--skip-ship` (everything except the cut).

### Step 1: The repo steps (sequential, alone)
Invoke **`/refactor`** and, when it is finished, **`/write-tests`** — via the Skill tool, one at a time,
never in parallel with anything. Both change the working tree; the audits must see the settled tree.

- `refactor` shows its own plan and waits for approval **in both modes** — do not try to pre-approve it
  for the user. It refuses to work on a red suite; if it stops there, fix that first (a `run-task` job)
  before continuing the chain.
- `write-tests` may finish with the suite **red** — that is a *result*, not a failure: it found a real
  bug and filed a task rather than quietly patching the product. Treat those tasks as findings in
  Step 4, and do not let a red suite from a filed bug be mistaken for a broken run.

### Step 2: Audits (parallel fan-out)
Spawn each enabled audit as a **fresh subagent**: they are independent and read-only → launch them
together. Each reads its contract, probes, proves, ranks, writes `.dev-skills/release/<noun>-audit.md`,
and returns its verdict (clean / N blockers / N majors). **A sub-skill not yet available in this
collection is a stop condition** regardless of mode: report it and let the user decide whether to skip
that step or build the skill first.

### Step 3: The human's briefing
Invoke **`/manual-test`**. It proves nothing and changes nothing — it writes
`.dev-skills/release/manual-test-brief.md` so the human can check by hand what no machine decides,
starting with everything accepted as `review: auto`. Its output is a handoff, not a gate: it never
blocks the cut, but it is always surfaced in the summary.

### Step 4: Triage
Collect every findings doc. The audits (and `refactor` / `write-tests` for what they found and did not
fix) already filed 🔴/🟡 as rework tasks (`type: rework`, via `plan-development`'s amend mode) and ranked
per **`severity-rubric.md`**; you reconcile and present the combined picture. In interactive, confirm
before the fix run; before any **destructive** backlog change (cancelling or reopening a `done` task)
always stop, in both modes.

A finding that says production is missing a capability — no hard spend cap, no error tracking, no rate
limit configured — is **not** a rework task for the code: it goes to `/setup-production-environment`.
Name it as such in the summary rather than filing it against a developer.

### Step 5: One fix round (no loop)
1. **Fix** — invoke `build-tasks` once to drive the open rework tasks. You fix nothing yourself.
2. **Re-run** — re-run **only** the steps whose findings were addressed, as fresh agents, to confirm the
   contract now holds (proven, not assumed).
3. **Then decide.** Anything still open after that single round is **`needs_human`** — surface it and
   stop, in both modes. There is no iteration counter and no second round: a finding that survives a
   targeted fix is a signal about the product, not something more rounds resolve. This is the same rule
   the build loop follows (**`../_shared/build-pipeline/verification-method.md`**). Open 🟡 do not block;
   record them for the human's call.

### Step 6: Cut (the only outward-facing step)
When no open 🔴 remains (and `--skip-ship` was not set), invoke `cut-release`. It confirms the tree is
clean and no blocker is open, then updates docs + version + changelog + release notes, tags, commits,
and opens the PR — **always with explicit confirmation, in both modes**. It stops before production. If
`cut-release` is not yet available, report that the release is audit-clean and ready to cut by hand.

### Done: summary + handoff
Build `.dev-skills/release/release-summary.md` (**`report-template.md`**) — decisions-first: the verdict,
open blockers and any waivers (the human's action list), the rework filed, every step run with its
verdict, the hands-on briefing, and what shipped if `cut-release` ran. Do not re-derive — roll up each
step's verdict plus the cut result. Then **refresh the project documentation map** block in the root
`CLAUDE.md` — idempotent, only between the markers, per **`../_shared/agent-guide.md`** (this is the
release phase's primary map refresh; it runs even under `--skip-ship`). Finally, hand off the **two
things that are the human's**: the hands-on pass from `manual-test`, and — when the product is going
live — `/setup-production-environment`, which is never auto-run from here.

## Rules

1. **Conduct, don't duplicate.** Never refactor, test, audit, fix, or ship yourself — invoke the
   sub-skills, `build-tasks` for fixes, and `cut-release` for the cut.
2. **Repo steps sequentially and alone; audits in parallel.** `refactor` then `write-tests`, each
   finished before the next starts; the read-only audits fan out together.
3. **Audits never fix and never install.** They file findings. Code is fixed by `build-tasks`; tooling
   by `setup-dev-environment`; production capabilities by `setup-production-environment`.
4. **One fix round, then a decision.** Re-run only what was addressed, once; whatever is still open is
   `needs_human`. No loop, no counter.
5. **Only a 🔴 blocks the cut.** Majors are filed, not blocking; minors are logged. Severity follows the
   shared rubric, against the contract — not taste.
6. **The cut always stops for the human**, in both modes, and stops before production.
7. **Putting the product live is not part of this run** — `setup-production-environment` is invoked by
   hand, deliberately.
8. **Resume, don't restart.** Reuse a clean verdict and in-flight rework; never re-run a settled step or
   rebuild a finished fix without reason.
9. **release-summary.md is always rolled up** from the step outputs and the cut result; never
   hand-authored from scratch.
