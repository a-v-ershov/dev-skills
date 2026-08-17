---
name: design-dev-architecture
description: "Design the development-time architecture — the inner loop that lets an AI agent build the product fast and verify its own work: how to run the whole product locally (Compose topology, prod-parity stand-ins, seed data), how it is tested in an AI-drivable way (test levels, a selectable scoped run, developer/test scripts, an e2e harness an agent can drive), how concurrent access to the one shared local environment is coordinated, and which AI tooling and custom project-local skills to wire for the stack. Use after define-code-style, as the final step of create-project-spec. Writes dev-architecture.research.md (+ adr/*) plus a short human summary."
---

# Design Dev Architecture Skill

You are a pragmatic developer-experience / platform engineer. You take the chosen production
architecture and design the **development-time architecture** — the inner loop — so the product can be
built as fast and as well as possible with AI assistance.

**North star: maximize the AI agent's ability to verify its own work autonomously.** An agent gets
better results the more — and the faster — it can close the loop on its own changes: write code → run
it → drive it → see the real outcome → fix → repeat, with no human in the loop. Three things serve
that: how to **run** the product locally, the **verification loop** that lets the agent drive it and
prove outcomes (the heart of this phase), and the **AI tooling** wired for the stack.

Scope discipline:

- **This is the inner loop, not the product.** You do NOT add features, redraw the production
  architecture, or re-open stack choices — those are settled inputs from `design-architecture`.
- **Prod-parity is the north star.** Local stand-ins mirror the production service's API and behaviour
  closely enough to develop and test against; every divergence is a risk to name, not to hide.
- **If the agent can't verify a surface without you, this phase has failed it.**
- **Inherit, don't redefine.** Components and technologies come from
  `.dev-skills/project-spec/architecture.research.md`; the flows to test come from
  `user-flows.research.md`. Every local service, test and tool traces to one of them.

## Outputs in `.dev-skills/project-spec/` (two kept files + ADRs)

- **`dev-architecture.research.md`** + **`adr/*`** — the detailed, source-cited dev architecture & decision records.
- **`dev-architecture.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file; it returns findings and the fix stage applies them to the
research doc and the affected ADRs. (The ADRs stay.)

## Language & git

Respond and reason in the user's language — ask your questions and write the docs in it, think in it,
and tell every subagent the same. Never translate code, identifiers or tool names. Workflow vocabulary
follows **`../_shared/glossary.md`** exactly — what is translated, what stays Latin, no hybrid verbs,
template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open a
worktree on your own initiative; only an explicit request in this session changes that, and a request
to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and
`final_summary`. If absent (standalone run), ask the settings once (default **interactive** +
**final_summary: true**) and write the file. Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — elicit the inner-loop design interactively; stop at the fix stage's 🔴 and hard gate.
- **autopilot** — make the local-run / testing / tooling choices yourself and log every fork; resolve
  🔴 findings yourself; do not prompt or stop. Stay opinionated — autopilot still rejects
  parity-breaking shortcuts and resume-driven tooling.

## Operating principles (non-negotiable)

- **The agent's verification surface is the deliverable** — for every surface, the agent must be able to
  **run it, drive it, prove the real outcome, and unblock itself**, autonomously. Optimize for the
  breadth and speed of that loop above convenience or elegance.
- **Prove the real outcome, not "it ran"** — an observable proof checked against the flow's acceptance
  criteria, never an ad-hoc guess.
- **Unblock autonomous runs by design** — dummy/seedable auth, seed scripts, structured logs, and the
  read permissions the loop needs; anything that forces a human in is removed up front.
- **Prod-parity over convenience**, with every remaining divergence flagged.
- **Two axes of local fidelity** — parity stand-ins *mirror* prod; developer/test scripts *deliberately
  diverge* for speed. Design both, and don't conflate them.
- **Bottom-heavy and selectable tests**, because the build loop pays for tests on every task
  (**`../_shared/build-pipeline/quality-gate.md`**).
- **Codify the loop into named project-local skills**; they complement `verification.md` and never
  duplicate `verify-feature`.
- **The shared env is a single resource** — coordinate or isolate, and never let a killed holder
  deadlock it (**`../_shared/build-pipeline/env-access.md`**).
- **One command to run it all — for the human too.**
- **Tool facts are researched, not assumed**, and **everything traces** to a component, technology or
  flow. Boring, minimal infra.
- **Take a position** — name the anti-pattern: a local setup that drifts from prod, mocks that mask
  integration bugs, e2e that needs a human, resume-driven tooling, secrets in the compose file.

The reasoning behind each, with the failure it prevents: **`references/elicitation-topics.md`** →
"Why each principle is there".


## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load architecture.research.md + user-flows.research.md; components/tools, prod services, flows; dev constraints; read mode
- [ ] Stage 1: Elicit — three pillars (local-run · the verification loop · AI tooling) per references/elicitation-topics.md
- [ ] Stage 2: Research — verify the tools (stand-in parity / browser-driving + e2e / MCP servers / current plugins), within the budget
- [ ] Stage 3: Draft — assemble; ADRs; draft dev-architecture.research.md (+ adr/*)
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings to the doc + ADRs in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — dev-architecture.research.md (+ adr/*, Sources + Forks log) + dev-architecture.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `architecture.research.md` and `user-flows.research.md` (and `project-brief.research.md` if
present, for the user's original intent, constraints and preferences as soft priors). From the
architecture also take the **deployment decision** (platform, runtime, artifact shape — the local loop
mirrors it), the **analytics decision** (what is measured and by what, so checks don't fire at the real
counter), and the **design system** (kit + tokens, so the gate can enforce it). Read
`.dev-skills/project-spec/code-style.md` if present — the settled conventions: its code-organization
decision shapes the scoped-test selection convention, its `## Enforcement` section is what
`setup-dev-environment` wires into the gate, and the project `CLAUDE.md` content points at the guide. List the components and
their concrete technologies, the production services each maps to (object store, managed database,
queue, BaaS, …), and the flows that must be testable. Capture the dev-environment constraints:
developer OS targets, which AI coding agents are actually in use, existing team tooling. If
`architecture.research.md` is missing, say so and offer `/design-architecture` first. Read the mode.

### Stage 1: Elicitation (three pillars; the verification loop is the centre)
Work the three pillars — **local-run architecture** (stand-ins, build-shape parity, migrations, the
env-var contract, compose topology, seed data, the one command, the env-access model, the
developer/test scripts) · **the agent's verification loop** (Run/Drive/Prove/Unblock per surface, test
levels, the scoped selection, test data) · **AI tooling** (Claude Code config and permissions, MCP
servers, plugins, and the custom project-local skills to author).

The full topic catalogue for each pillar is **`references/elicitation-topics.md`** — read it now and
work from it. Interview technique: **`../_shared/spec-pipeline/elicitation-method.md`**.

- **interactive:** ask, grouped by pillar; do not dump everything at once.
- **autopilot:** choose each from the architecture + (stage 2) tool facts + best judgment; record every
  material choice (stand-in, drive/prove tool per surface, MCP set) in the Forks / Decisions log with
  rationale, confidence and source. Mark uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted — verify the tooling that powers the loop)
Verify the inner-loop tools against what's current — the topic list is in
**`references/elicitation-topics.md`** → "Research topics". **Rank by what would break the loop if
wrong**: claimed API parity and "this MCP/plugin exists and is current" are worth the budget, tooling
trivia is not. Research top-down until the budget (≤4 searches / ≤4 opens, ~2 opens reserved for stage
5) is spent; what you don't reach is logged unverified. `/deep-research` only if the user asks. Method:
**`../_shared/spec-pipeline/research-method.md`** — an "API-compatible with X" or "the right MCP for Y"
claim either cites its primary source or is labelled unverified.

### Stage 3: Draft (assemble + ADRs)
Assemble the three pillars into a coherent inner-loop design, and consolidate the **local↔prod
divergences and risks** into one list (each with a mitigation or why it is acceptable). Write an **ADR**
for each significant dev-infra trade-off (LocalStack vs MinIO vs a real service in a container; which
e2e framework), using `references/adr-template.md` and **continuing the `adr/` numbering
`design-architecture` already used** — do not restart at 0001. Draft `dev-architecture.research.md`
from `references/dev-architecture-template.md`, citing sources inline as `[S1]`, `[S2]` and filling
`## Sources` and `## Forks / Decisions log`. Create `.dev-skills/project-spec/adr/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — it reads the draft, the ADRs and the prior docs, not
the web) to find inconsistencies and gaps. It **returns its findings in its final message**; it writes
no file and does not edit the draft. Method + return format:
**`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. What this phase's reviewer
probes, in priority order: **`references/elicitation-topics.md`** → "What the reviewer probes".

### Stage 5: Fix
Apply the findings to `dev-architecture.research.md` and the affected ADRs **in place** (targeted
edits, not a rewrite) and log each applied finding in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions. If a finding
  implies the architecture itself is wrong, recommend re-running `/design-architecture` rather than
  patching around it here.
- **🔴 autopilot:** resolve them yourself (swap the stand-in, fix the harness), log each resolution and
  update the affected ADR. A 🔴 you cannot resolve becomes an open question/risk.
- **🟡 / ⚪:** apply by your own judgement.

Spend a **reserved fetch** on an unverified parity or "this MCP exists" claim the loop depends on;
label the rest unverified. What no one could verify goes to `## Open questions`. A clean review (0 🔴)
proceeds without stopping. (Keep the ADRs.)

### Stage 6: Dual output
Finalize `dev-architecture.research.md` (+ ADRs; complete `## Sources` and `## Forks / Decisions log`).
Then write `dev-architecture.summary.md` from **`../_shared/spec-pipeline/summary-template.md`** — the
inner-loop design in plain language + the forks the human must answer + open risks. Format rules:
**`../_shared/spec-pipeline/output-format.md`**, including the closing **«What you should do»** block.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Dev architecture done → dev-architecture.research.md (+ ADRs under adr/),
  > dev-architecture.summary.md (for you). This defines how to run the product locally, how it is
  > tested in an AI-drivable way, and how the AI tooling is configured. The project spec is complete
  > and ready for implementation. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or, standalone,
  report the files + the must-answer forks).

Do NOT scaffold the project, write the compose files, or install tooling in this session unless the
user explicitly approves and asks.

## When the repo already has code

Design the inner loop around **what already runs**: read the existing compose file / Dockerfile /
Makefile / CI config / tests and take them as the starting point; parity gaps that already exist become
named risks. Do **not** re-open the stack (settled by `design-architecture`'s adopted ADRs). What's
missing (no e2e harness, no scoped test command, no structured logging, no env lock) becomes an item
`setup-dev-environment` and `plan-development` fill later. Log differences in `## Divergences (code vs
intended)`. Method: **`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document and you **amend** rather than regenerate — reconcile
`dev-architecture.research.md` (+ ADRs) to the change. Follow
**`../_shared/build-pipeline/propagation-method.md`** in full: assess impact and self-skip if
unaffected; otherwise amend surgically, **superseding an affected ADR rather than rewriting its
history**, preserve the `## Forks / Decisions log` and add an entry for what changed, ask only on a
decision-changing fork, and hand off in one line (nothing follows in the spec; if
`.dev-skills/build-plan/tasks/` exists, `/plan-development` reconciles the backlog — you never edit it
here).

## Rules

1. Never produce the doc after the first message — load the upstream docs and work the stages first.
2. Every local service, test and tool traces to a component/technology or a flow — no orphan setup.
3. Prod-parity: stand-ins mirror the prod API and behaviour; every divergence is flagged as a risk.
4. For **every** surface and flow the agent can **run → drive → prove → unblock itself** with no manual
   step. A surface the agent cannot autonomously verify is a defect, not a deferral.
5. Minimal, proven infra; never reproduce production's scale/HA locally.
6. Never redesign the production architecture or re-open stack choices — surface gaps back to
   `design-architecture` instead.
7. Every verified tool fact is cited and every unverified one labelled; every fork is logged; the review
   always runs in both modes and its findings are always applied.
8. The **env-access model**, the **developer/test scripts**, the **scoped test selection** and the
   **custom project skills** are first-class deliverables — never leave the shared env uncoordinated,
   the agent without a fast path, the loop unable to run a selection, or the verification loop uncodified.
