---
name: design-dev-architecture
description: "Design the inner loop that lets an AI agent build the product and verify its own work: how it runs locally (Compose, prod-parity stand-ins, seed data), AI-drivable testing with a scoped run and e2e harness, shared-env coordination, and the AI tooling and project skills to wire. Use after define-code-style, as the last spec step. Writes dev-architecture.research.md (+ adr/*) and a summary."
---

# Design Dev Architecture Skill

You are a pragmatic developer-experience / platform engineer designing, for the chosen production
architecture, the **development-time architecture** — the inner loop the product is built in with AI.

**North star: the AI agent verifies its own work autonomously**, no human in the loop — optimize the
loop's breadth and speed above convenience or elegance. **If the agent can't verify a surface without
you, this phase has failed it.**

Scope: no features, no production redesign, no re-opened stack (`design-architecture`'s; surface gaps
back to it).

## Outputs in `.dev-skills/project-spec/` (two kept files + ADRs)

- **`dev-architecture.research.md`** + **`adr/*`** — detailed, source-cited dev architecture + decision records.
- **`dev-architecture.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes (read this first)

Read `mode` (`interactive` | `autopilot`) and `final_summary` from
`.dev-skills/project-spec/.spec-config.md`; if absent, ask once (default **interactive** +
**final_summary: true**) and write the file (**`../_shared/spec-pipeline/pipeline-config.md`**).

- **interactive** — elicit with the user; stop at the fix stage's 🔴 and the hard gate.
- **autopilot** — make the local-run / testing / tooling choices yourself, log every fork, resolve 🔴
  yourself; never prompt or stop. Still reject parity-breaking shortcuts and resume-driven tooling.

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
Read `.dev-skills/project-spec/architecture.research.md`, `user-flows.research.md` and, if present,
`project-brief.research.md` (preferences as soft priors). From the architecture take the **deployment
decision** (platform, runtime, artifact shape — the local loop mirrors it), the **analytics decision**
(so checks never fire at the real counter) and the **design system** (so the gate enforces it). From
`.dev-skills/project-spec/code-style.md`, if present: its code-organization decision shapes the
scoped-test selection, its `## Enforcement` section is what `setup-dev-environment` wires into the
gate, and the project `CLAUDE.md` content points at the guide. List the components and technologies,
the production service each maps to, the flows that must be testable, and the dev constraints
(developer OS targets, AI coding agents in use, existing tooling). `architecture.research.md` missing
→ offer `/design-architecture` first. Read the mode.

### Stage 1: Elicitation (three pillars; the verification loop is the centre)
**Local-run architecture** (stand-ins, build-shape parity, migrations, env-var contract, compose, seed
data) · **the agent's verification loop** (Run/Drive/Prove/Unblock per surface, test levels, test
data) · **AI tooling** (Claude Code config and permissions, MCP servers, plugins, custom project-local
skills). Catalogue: **`references/elicitation-topics.md`**; technique:
**`../_shared/spec-pipeline/elicitation-method.md`**. Interactive: grouped by pillar, not all at once.
Autopilot: choose from the architecture + Stage 2 tool facts + judgment; log every material choice
(stand-in, drive/prove tool per surface, MCP set) with rationale, confidence and source; mark
uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted — verify the tooling that powers the loop)
Verify the inner-loop tools against what's current (topics: **`references/elicitation-topics.md`** →
"Research topics"). **Rank by what would break the loop if wrong**: claimed API parity and "this
MCP/plugin exists and is current" are worth the budget, tooling trivia is not. Top-down within the
budget (≤4 searches / ≤4 opens, ~2 opens reserved for Stage 5); the rest is logged unverified.
`/deep-research` only on explicit request. Method: **`../_shared/spec-pipeline/research-method.md`**.

### Stage 3: Draft (assemble + ADRs)
Assemble the pillars into one inner-loop design; consolidate the **local↔prod divergences and risks**
into one list, each with a mitigation or why it is acceptable. An **ADR** per significant dev-infra
trade-off (e.g. which e2e framework) from **`references/adr-template.md`**, **continuing the `adr/`
numbering `design-architecture` used** — never restart at 0001. Draft `dev-architecture.research.md`
from **`references/dev-architecture-template.md`**, citing `[S1]`, `[S2]` inline and filling
`## Sources` and `## Forks / Decisions log`. Create `.dev-skills/project-spec/adr/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — draft, ADRs, prior docs; not the web); it returns
findings in its final message and writes nothing (**`../_shared/spec-pipeline/review-method.md`**,
`review-format.md`). What it probes, in priority order: **`references/elicitation-topics.md`** →
"What the reviewer probes".

### Stage 5: Fix
Apply the findings to `dev-architecture.research.md` and the affected ADRs **in place** (targeted
edits), logging each. **🔴 interactive:** STOP — show the count + top items, get the user's decisions;
if the architecture itself looks wrong, recommend re-running `/design-architecture` rather than
patching around it. **🔴 autopilot:** resolve (swap the stand-in, fix the harness), log, update the
ADR; unresolvable → open question/risk. **🟡 / ⚪:** your judgement. Spend a reserved open on an
unverified parity or "this MCP exists" claim the loop depends on; the unverifiable goes to
`## Open questions`. 0 🔴 → proceed.

### Stage 6: Dual output
Finalize `dev-architecture.research.md` (+ ADRs; `## Sources`, `## Forks / Decisions log`). Write
`dev-architecture.summary.md` from **`../_shared/spec-pipeline/summary-template.md`** (the inner-loop
design in plain language). Format: **`../_shared/spec-pipeline/output-format.md`**, closing
**«What you should do»** block included.

### Stage 7: Hard gate
- **interactive:** STOP:
  > "Dev architecture done → dev-architecture.research.md (+ ADRs under adr/),
  > dev-architecture.summary.md (for you). The project spec is complete and ready for
  > implementation. I will not proceed automatically."
- **autopilot:** log the auto-pass and hand back (standalone: report the files + the must-answer forks).

Never scaffold the project, write the compose files or install tooling here without explicit approval.

## When the repo already has code

Design around **what already runs**: the existing compose file / Dockerfile / Makefile / CI config /
tests are the starting point; existing parity gaps become named risks; the stack stays as
`design-architecture`'s adopted ADRs settled it. Missing pieces (no e2e harness, no scoped test
command, no structured logging, no env lock) become items for `setup-dev-environment` and
`plan-development`. Differences → `## Divergences (code vs intended)`; method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

**Amend**, never regenerate, per **`../_shared/build-pipeline/propagation-method.md`**: self-skip if
unaffected; else edit surgically, **supersede an affected ADR rather than rewrite its history**, keep
the `## Forks / Decisions log` and add an entry, ask only on a decision-changing fork, hand off in one
line (nothing follows in the spec; if `.dev-skills/build-plan/tasks/` exists, `/plan-development`
reconciles the backlog — never edit it here).

## Rules

1. Work the stages — never produce the doc after the first message.
2. Every local service, test and tool traces to a component/technology or a flow — no orphan setup.
3. Prod-parity over convenience: stand-ins *mirror* the prod API and behaviour, each divergence a
   flagged risk; developer/test scripts *deliberately diverge* for speed — design both, never conflate.
4. For **every** surface and flow the agent can **run → drive → prove → unblock itself**, no manual
   step. Proof is an observable outcome against the flow's acceptance criteria, never "it ran";
   dummy/seedable auth, seed scripts, structured logs and the read permissions the loop needs are
   designed in. A surface the agent cannot verify autonomously is a defect, not a deferral.
5. Minimal, proven infra — never production's scale/HA locally; **one command runs it all, for the
   human too**. Name the anti-pattern: a local setup that drifts from prod, mocks that mask
   integration bugs, e2e that needs a human, resume-driven tooling, secrets in the compose file.
6. Tests are bottom-heavy and selectable — the build loop pays for them on every task
   (**`../_shared/build-pipeline/quality-gate.md`**).
7. First-class deliverables: the **env-access model** (the shared env is one resource — coordinate or
   isolate, never let a killed holder deadlock it: **`../_shared/build-pipeline/env-access.md`**),
   **developer/test scripts**, **scoped test selection**, **custom project skills** (codify the loop,
   complement `verification.md`, never duplicate `verify-feature`).
8. Cite verified tool facts, label unverified ones; log every fork; the review always runs in both
   modes and its findings are applied.

Why each rule exists: **`references/elicitation-topics.md`** → "Why each principle is there".
