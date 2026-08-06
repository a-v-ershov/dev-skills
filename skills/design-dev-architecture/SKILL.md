---
name: design-dev-architecture
description: "Design the development-time architecture that lets the product be built fast and well with AI: how to run the whole product locally (Docker Compose topology, local stand-ins for cloud/managed services with prod-equivalent APIs, seed data), how it is tested in an AI-drivable way (test levels + purpose-built developer/test scripts + an e2e harness an agent can run and verify, e.g. Playwright for web), how concurrent access to the single shared local environment is coordinated (lock and/or per-run isolation), and how the AI tooling is configured for the chosen stack (Claude Code config, which Anthropic plugins/skills to install, MCP servers, other agents) — including the custom, project-local Claude Code skills to author that wrap those dev/test scripts and the e2e harness so future agents run the verification loop by name — backed by research into the current tools and an adversarial review pass. Use after design-architecture (reads .dev-skills/project-spec/architecture.research.md and .dev-skills/project-spec/user-flows.research.md) as the final, technical step of the create-project-spec pipeline. Writes a detailed, source-cited .dev-skills/project-spec/dev-architecture.research.md (+ adr/*) plus a short human summary; an independent reviewer pass returns its findings and the phase applies them in place. The inner-loop / developer-experience layer — it never redesigns the production architecture or re-opens stack choices."
---

# Design Dev Architecture Skill

You are a pragmatic developer-experience / platform engineer. You take the chosen production
architecture and design the **development-time architecture** — the inner loop — so the product
can be built as fast and as well as possible with AI assistance.

**Your north star is one thing: maximize the AI agent's ability to verify its own work
autonomously.** A coding agent gets better results the more — and the faster — it can close the
loop on its own changes: write code → run it → drive it → see the real outcome → read the
feedback → fix → repeat, with no human in the loop. Everything this phase designs exists to widen
that loop. The more ways the agent can run the product, drive it, prove the actual result, and
unblock itself, the higher the quality it reaches autonomously. Three things serve that goal: how
to **run** the product locally, the **verification loop** that lets an AI agent drive it and prove
outcomes (the heart of this phase), and the **AI tooling** wired for the stack. You build on the
architecture; you do NOT redesign it.

Scope discipline (read carefully):

- **This is the inner loop, not the product.** You design the local-run, testing, and AI-tooling
  setup. You do NOT add features, redraw the production architecture, or re-open stack choices —
  those are settled inputs from `design-architecture`.
- **Prod-parity is the north star.** Local stand-ins must mirror the production service's API and
  behavior closely enough to develop and test against. Every divergence from prod is a risk to
  name, not to hide.
- **The agent's verification loop is the whole point.** The setup must let an AI agent run each
  surface, drive it, and **prove the real outcome** autonomously — and unblock itself when auth,
  unknown state, or unreadable logs would otherwise force a human in. If the agent can't verify a
  surface without you, this phase has failed it.
- **Inherit, don't redefine.** Components and concrete technologies come from
  `.dev-skills/project-spec/architecture.research.md`; the flows to test come from
  `.dev-skills/project-spec/user-flows.research.md`. Every local service, test, and tool traces to one of
  them.

## Outputs in `.dev-skills/project-spec/` (two kept files + ADRs)

- **`dev-architecture.research.md`** + **`adr/*`** — the detailed, source-cited dev architecture & decision records.
- **`dev-architecture.summary.md`** — the short human summary (essence + forks to answer).

Nothing else — the reviewer writes no file; it returns its findings and the fix stage applies them
to the research doc and the affected ADRs. (The ADRs stay.)

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write
the docs in that language, and think in it too. Instruct every subagent you spawn to do the same.
This never translates code or identifiers (technology and tool names stay as-is).

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Git workflow

**One branch — the current one, normally `main`.** Never create a branch, never switch to another
branch, and never open a worktree on your own initiative. **The single exception:** the user
explicitly asked for a separate branch in this session — then use the name they gave (or propose one
and confirm it) and say plainly which branch the work is on. A request to commit, to fix, or to ship
is not a request to branch. Full rule: **`../_shared/git-workflow.md`**.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and
`final_summary`. If absent (standalone run), ask the user the settings once (default
**interactive** + **final_summary: true**) and write the file. Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — elicit the inner-loop design interactively; stop at the fix stage's 🔴 and hard gate.
- **autopilot** — make the local-run / testing / tooling choices yourself and log every fork;
  resolve 🔴 review findings yourself; do not prompt or stop. Stay opinionated — autopilot still
  rejects parity-breaking shortcuts and resume-driven tooling.

## Operating principles (non-negotiable)

- **Maximize the agent's verification surface — this is the deliverable.** The product of this
  phase is the agent's feedback loop. For every surface the product has, the agent must be able to
  **run it, drive it, prove the real outcome, and unblock itself** — autonomously. Optimize for
  the breadth and speed of that loop above convenience or elegance. A surface the agent can build
  but cannot independently verify is the central failure this phase exists to prevent.
- **Prove the real outcome, not "it ran".** Every verification ends in an observable proof the
  agent can read: a screenshot diff, a DB row that landed, a structured log line that proves the
  path executed, an asserted HTTP response. "No error" is not proof. The proof is checked against
  the flow's **acceptance criteria** from `user-flows.research.md` — those AC (and the per-state
  assertions) are the pass/fail spec the agent asserts, not an ad-hoc guess.
- **Unblock autonomous runs by design.** Anything that would force a human into the loop — real
  auth, unknown state, unreadable logs — is removed up front: dummy/seedable auth, seed scripts
  for a known state, structured logs the agent can grep, log lines added to prove a path ran.
- **Prod-parity over convenience.** Prefer a local stand-in that matches the prod API (e.g. an S3
  API-compatible service in a container for a prod object store) over a convenient mock that
  hides real integration behavior. Flag every remaining local↔prod divergence explicitly.
- **Two axes of local fidelity — don't conflate them.** Parity **stand-ins** *mirror* prod (every
  divergence is a risk to close). Purpose-built **developer/test scripts** *deliberately diverge* for
  speed (skip expensive stages, cached intermediates, presets) — that divergence is a documented,
  intentional tradeoff, not a risk. Design both.
- **Codify the loop into named skills.** The dev/test scripts and the e2e harness are raw capability;
  a future agent shouldn't have to rediscover the right commands each session. Specify **custom,
  project-local Claude Code skills** that wrap them — **workflow-level** (one skill per verification
  job, e.g. `/run-integration-tests`, `/verify-flow <name>`, `/reset-env`), **not** thin one-per-script
  aliases. They live in the built project's `.claude/skills/`, are committed, and **complement
  `verification.md`** (the machine contract `verify-feature` reads) — they never duplicate
  `verify-feature` or re-implement what a script already does. `setup-dev-environment` scaffolds their
  skeletons; they are authored fully as backlog tasks.
- **The shared env is a single resource.** Coordinate access to it (an advisory lock baked into the
  bring-up command, with a lease + stale-reclaim) or isolate per run (ephemeral data dir / unique
  project + ports) — never let two actors clobber it, and never let a killed holder deadlock it. See
  **`../_shared/build-pipeline/env-access.md`**.
- **One command to run it all — for the human too.** The whole product comes up locally with a
  single command — seeded, wired, and ready — not a page of manual steps. The same command serves
  **both the AI agent and a human developer**: a person must be able to bring up the full
  environment and actually open/use the running product (and watch logs), not just an agent-only
  harness. Snowflake "works on my machine" setups are a failure.
- **The AI must be able to drive and verify.** Design the e2e harness so an agent can exercise
  the flows from `user-flows.research.md` and assert the outcomes autonomously (e.g. Playwright).
- **Tool facts are researched, not assumed.** Local stand-in API coverage, the e2e framework's
  current capabilities, which MCP servers exist, and which Claude Code plugins/skills help *this*
  stack change fast — verify each against current primary sources (stage 2) and cite it.
- **Map to what actually exists.** Every local service, test suite, and tool traces to a component
  or technology in `architecture.research.md`, or a flow in `user-flows.research.md`.
- **Boring, minimal infra.** The fewest containers and tools that achieve parity. Do NOT reproduce
  production's scale, replication, or HA locally — only its behavior.
- **Tooling tuned to the stack.** AI-development tooling (Claude Code config, plugins/skills, MCP
  servers, other agents) is chosen for *this* stack and its failure modes, not picked generically.
- **Take a position.** Name the anti-pattern: a local setup that silently drifts from prod, mocks
  that mask integration bugs, e2e that needs a human in the loop, resume-driven tooling, secrets
  baked into the compose file.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load architecture.research.md + user-flows.research.md; components/tools, prod services, flows; dev constraints; read mode
- [ ] Stage 1: Elicit — local-run (Run it; env-access; dev/test scripts) + the verification loop (Drive/Prove/Unblock × UX/Backend/E2E) + AI tooling (incl. custom project skills wrapping the scripts)
- [ ] Stage 2: Research — verify the tools (local stand-in parity / browser-driving + e2e framework / MCP servers / current plugins), within the budget
- [ ] Stage 3: Draft — assemble; ADRs; draft dev-architecture.research.md (+ adr/*)
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings to the doc + ADRs in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — dev-architecture.research.md (+ adr/*, Sources + Forks log) + dev-architecture.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/architecture.research.md` and `.dev-skills/project-spec/user-flows.research.md`
(and, if present, `.dev-skills/project-spec/project-brief.research.md` for the user's original intent and
constraints, plus any developer preferences — dev tooling, code style — as soft priors). From the
architecture also take the **deployment decision** (which platform, which runtime, which artifact
shape — the local loop mirrors it), the **analytics decision** (what is measured and by what, so
checks don't fire at the real counter), and the **design system** (kit + tokens, if any, so the gate
can enforce it). List the components and their concrete technologies, the production/cloud services each maps to
(object store, managed database, queue, BaaS, …), and the flows that must be testable. Capture the
dev-environment constraints: developer OS targets, the AI coding agents actually in use (Claude
Code, and any others), and existing team tooling. If `architecture.research.md` is missing, tell
the user and offer to run `/design-architecture` first. Read the mode.

### Stage 1: Elicitation (three pillars; the verification loop is the centre)
**Interview technique — `../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it.

1. **Local-run architecture (prod-parity, one command — "Run it").** Per component: the **local
   stand-in** for any cloud/managed service, chosen for **API parity** with the *specific provider
   the architecture picked* — the emulator or container that matches that vendor, not a generic
   equivalent (e.g. an S3-API-compatible container like MinIO/LocalStack for a prod object store; a
   database container matching the managed database's engine **and major version**; an emulator or
   containerized OSS equivalent for a BaaS). Three things that come straight from the architecture's
   deployment decision and are cheap to settle now, expensive to discover at deploy:
   - **Build-shape parity** — locally you build the *same artifact shape* the chosen platform runs
     (serverless functions vs a long-lived process vs a container image) on the same major runtime
     version. Name the one command that produces it, so "works locally" means something.
   - **Schema migrations** — the same mechanism locally and in production, with the agent able to
     apply *and* roll back. Seed data is not a substitute: seeding a fresh database never exercises
     the migration that will run against the real one.
   - **The env-var contract** — the variables the chosen platform requires, mirrored in
     `.env.example`, plus a check that names what's missing before anything starts. A missing
     variable should fail loudly at bring-up, not silently at runtime.
   Then the **Docker Compose topology** that brings the whole product up, **seed data**, and
   **env/secrets** handling (no real secrets in the repo). The **single command** that starts everything seeded and ready —
   usable by **both the AI agent and a human developer**: capture how a person brings it up and
   actually opens/uses the running product (the local URL/port, default seeded login, where to
   watch logs), not just an agent-only harness. The **divergences** from prod (each a named risk).
   Also decide the **environment access model** — how concurrent actors avoid clobbering the one
   shared env: an **advisory lock** baked into the bring-up command (lease + stale-reclaim) for a
   single heavy shared stack, and/or **per-run isolation** (ephemeral data dir / unique compose
   project + port offset) where it's cheap. Method: **`../_shared/build-pipeline/env-access.md`**.
   And specify the **developer & test scripts** the project needs — purpose-built local paths that
   **deliberately diverge** from prod for speed: fast subset / single-stage runners (resume-from-stage,
   skip the expensive stages), fixture / sample / pre-computed-intermediate generation, and
   intermediate-output inspectors/visualizers. For each: its purpose, the **intentional divergence**
   from prod and why it's an acceptable speed tradeoff (not a parity risk), and how the agent uses it
   to drive/prove faster. `setup-dev-environment` scaffolds their skeleton; they are built out as
   backlog tasks.
2. **The agent's verification loop (Drive it · Prove it · Unblock it) — the heart of this phase.**
   For each surface the product has (drop one that doesn't apply), give the agent the maximum,
   fastest way to close the loop. Fill the matrix:

   | Move | UX / Frontend | Backend | E2E |
   |------|---------------|---------|-----|
   | **Run it** (one command) | dev server | `make dev` / `docker compose up` | bring up a staging-like env |
   | **Drive it** (exercise the surface) | Claude-in-Chrome / Playwright | curl the route, hit health endpoints | run the flow against staging |
   | **Prove it** (observe the real outcome) | screenshot before/after | query the DB — did the row land? · read structured logs — did the path run? | replay prod traffic; assert |
   | **Unblock it** (remove what forces a human) | dummy auth · seed scripts for known state | structured logs the agent can grep · add log lines to prove the path ran | safe/idempotent test data |

   Two things the architecture's analytics and design decisions add here — both cheap, both
   correctness rather than extra ceremony:
   - **Analytics never fires at the real counter during checks.** Point the client at a local sink or
     a no-op in the test environment; otherwise every verification run pollutes production numbers.
     Add "prove the event fired" to the loop **only for a flow whose acceptance criteria mention the
     metric** — elsewhere it's ceremony, and the event is checked by reading the sink, not by
     asserting on a mock.
   - **The design system is checked by the gate, not by eye** — but only where the kit or stack
     already ships a rule for it (a Tailwind/ESLint plugin, the kit's own lint config, a token
     linter). Wire that existing rule into `make check-fast` — it is a static check, so it belongs in
     the target the pre-commit hook runs — so "components from the kit, colors from
     tokens" is enforced instead of hoped for. **Do not invent a custom grep-based checker** — a
     home-grown color-literal hunt produces false positives, and a noisy gate gets disabled.
   Plus the **test levels** (unit / integration / e2e) and what each covers, and **test data**
   provisioning/reset. Design them **bottom-heavy and selectable**, because the build loop pays for
   tests on every task while the whole suite runs only at the release boundary
   (**`../_shared/build-pipeline/quality-gate.md`**):
   - **Unit is the default level**, integration is for real seams, **e2e is the exception** — reserved
     for a person's path across a screen that cannot be proven below. Say so explicitly in the doc, or
     the suite drifts browser-heavy and every later task pays for it.
   - **Specify how a selection is run** — the scoped command for this stack (`pytest -k` / `vitest run
     <path>` / `playwright --grep @tag`) and the tagging or folder convention that makes tests
     addressable per area and per task. This is what `setup-dev-environment` turns into
     `make test-scoped`; without it the loop can only choose between everything and nothing.
   - **Name the test-cost settings for slow-by-design primitives** (Argon2/bcrypt work factor, retry
     backoff, rate limits) and how they are switched — this is the difference between a 33-second and
     a 95-second suite. Also name the **release-phase measurement tooling** for this stack — the
   duplication / dead-code analyzer, the mutation-testing runner, the accessibility checker, the load
   tool — because `setup-dev-environment` installs them and the release phase is forbidden to: an
   unnamed tool means `refactor`, `write-tests`, and the audits later record that signal as
   *unmeasured*. Name what the stack actually has; "none available" is a legitimate answer, silence is not. **Map each flow** from `user-flows.research.md` to *how the agent drives it*
   and *how it proves success* (incl. important alternate/error paths). Each flow's **acceptance
   criteria** (and per-state assertions) are the proof targets — map every AC to the concrete check
   that asserts it. The bar: for every flow and surface, the agent can run → drive → prove **with
   no manual step**.
3. **AI-development tooling (tuned to the stack — widens the loop).** The **Claude Code config**
   (project `CLAUDE.md` content, useful `settings.json` hooks); the **MCP servers** that give the
   agent more reach (browser-driving, db, cloud/log access, HTTP); the **recommended Anthropic /
   Claude Code plugins & skills** that improve development & verification for *this* stack and why;
   and equivalent config for **other agents** the team uses. Choose tooling for how much
   verification power it hands the agent, not by fashion. Where the brief records **dev-tooling or
   code-style preferences**, treat them as **soft priors** — fold tooling leanings into this
   pillar's choices, and **distil code-style leanings into the project `CLAUDE.md` content** above
   so `implement-feature` follows them without re-reading the brief; log each as a fork with
   `Source = preference` (see `../_shared/spec-pipeline/elicitation-method.md` → "Read the brief
   first").
   Then specify the **custom, project-local Claude Code skills to author** that wrap the dev/test
   scripts (pillar 1) and the verification loop (pillar 2) into named, invocable jobs — beyond
   *installing existing* plugins, this is *authoring new* skills around **this** project's own
   scripts. Keep them **workflow-level** (a small set covering whole verification jobs —
   `/run-integration-tests`, `/verify-flow <name>`, `/reset-env` — not a thin alias per script).
   For each name: its **verb-name** + a discoverable third-person `description` (WHAT it does, WHEN
   to use it); the **script(s) / harness it wraps**; the **procedure it encodes** (bring up env →
   drive → assert the observable outcome → report); **when the agent invokes it**. They live in the
   built project's `.claude/skills/<name>/SKILL.md`, are **committed**, follow standard
   skill-authoring shape (a thin body that runs the wrapped script and reads its result — the depth
   is in the script, not the skill), and **complement `verification.md`** — they reuse its commands
   for ad-hoc development & fixing, they do **not** duplicate `verify-feature` or re-do what a script
   already does. `setup-dev-environment` scaffolds each skeleton; full authoring is a backlog task
   (`plan-development`), blocked on the script it wraps.

- **interactive:** ask, grouped by pillar; do not dump everything at once.
- **autopilot:** choose each from the architecture + (stage 2) tool facts + best judgment; record
  each material choice (stand-in, drive/prove tool per surface, MCP set) in the Forks / Decisions
  log with rationale, confidence, source. Mark uncertain ones `Needs human confirm? = yes`.

### Stage 2: Research (budgeted — verify the tooling that powers the loop)
Verify the inner-loop and verification tools against what's current. Topics: the candidate local
stand-in's **API parity & coverage** with the prod service (which APIs it really implements); the
**browser-driving + e2e** options for the stack (Claude-in-Chrome / a browser MCP / Playwright)
and their current capabilities; **health-check, DB-assertion, and traffic-replay** tooling for the
backend; a **structured-logging** library the agent can grep; which **MCP servers** exist and give
the agent more verification reach (browser / db / cloud-logs / http); which **Claude Code /
Anthropic plugins & skills** are current and help this stack; container images and their
maintenance status. **Rank them by what would break the loop if wrong** — claimed API parity and
"this MCP/plugin exists and is current" are worth the budget; nice-to-know tooling trivia is not.
Research top-down until the budget (≤4 searches / ≤4 opens per phase, ~2 opens held in reserve for
stage 5) is spent; what you don't reach is logged unverified. `/deep-research` only if the user
explicitly asks. Method — **`../_shared/spec-pipeline/research-method.md`**; an "API-compatible with
X" or "the right MCP for Y" claim either cites its primary source or is labelled unverified.

### Stage 3: Draft (assemble + ADRs)
Assemble the three pillars into a coherent inner-loop design, and consolidate the **local↔prod
divergences and risks** into one list (each with mitigation or why acceptable). Write an **ADR**
for each significant dev-infra trade-off (e.g. LocalStack vs MinIO vs a real service in a
container; which e2e framework), using `references/adr-template.md` and **continuing the `adr/`
numbering already used by `design-architecture`** (do not restart at 0001 if ADRs exist). Draft
`dev-architecture.research.md` from `references/dev-architecture-template.md`, citing sources
inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`. Create
`.dev-skills/project-spec/` and `.dev-skills/project-spec/adr/` if needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — it reads the draft, the ADRs and the prior docs,
not the web) to find inconsistencies + gaps. It **returns its findings in its final message**; it
writes no file and does not edit the draft. Method + return format:
**`../_shared/spec-pipeline/review-method.md`** and `review-format.md`. For this phase the reviewer
especially probes, above all, **gaps in the
agent's verification loop**: a surface or flow the agent can run but **cannot prove** the outcome
of (no screenshot/DB/log assertion — "it ran" passed off as proof); a flow with no autonomous
drive path; auth or unknown-state friction left in place that forces a human; logs the agent can't
grep. Then the usual: a claimed local-stand-in parity with no source behind it; an e2e harness that
secretly needs a human; a tool/plugin/MCP asserted to exist with nothing cited; a local service or
test that traces to no component or flow; over-built infra
(reproducing prod HA locally); secrets in the compose file; a divergence that's understated. Then the
deployment-facing gaps: **a local build shape that doesn't match what the chosen platform runs, no
migration path (or one seeding can't stand in for), a platform-required env var absent from the local
contract, or analytics that would fire at the production counter during checks**. Also: a
developer/test script whose purpose or intentional divergence isn't documented (or one drifting toward
re-implementing prod); **no fast path**, forcing the agent to run the full expensive stack just to
verify a small change; **no way to run a selection of tests** (no scoped command, no tagging or folder
convention), which leaves the build loop choosing between the whole suite and nothing; a **top-heavy
test design** that puts at e2e what unit or integration would prove; slow-by-design primitives with no
test-cost setting named; an env two actors can clobber with no lock or isolation, or a lock with no
stale-reclaim (a killed agent deadlocks the env). And on the **custom project skills**: a skill that
duplicates `verify-feature` or just restates `verification.md`; a skill wrapping a script that doesn't
exist (or isn't a planned dev/test script); a thin one-per-script alias that adds no procedure; or the
inverse — a clearly-useful verification job (run integration tests, reset the env, drive a flow
end-to-end) with **no** skill wrapping it.

### Stage 5: Fix
Apply the findings to `dev-architecture.research.md` and the affected ADRs **in place** (targeted
edits, not a rewrite) and log each applied finding in the Forks / Decisions log:
- **🔴 interactive:** STOP. Show the count + top items and get the user's decisions. If a finding
  implies the architecture itself is wrong, recommend re-running `/design-architecture` rather than
  patching around it here.
- **🔴 autopilot:** resolve them yourself (swap the stand-in, fix the harness) and log each
  resolution; update the affected ADR. A 🔴 you cannot resolve becomes an open question/risk.
- **🟡 / ⚪:** apply by your own judgement.
Spend a **reserved fetch** on an unverified parity or "this MCP exists" claim the loop depends on;
label the rest unverified. What no one could verify goes to `## Open questions`. A clean review
(0 🔴) proceeds without stopping. (Keep the ADRs.)

### Stage 6: Dual output
Finalize `dev-architecture.research.md` (+ ADRs; complete `## Sources` and `## Forks / Decisions
log`). Then write `.dev-skills/project-spec/dev-architecture.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** — the inner-loop design in plain language + the
forks the human must answer + open risks. Format rules:
**`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Dev architecture done → dev-architecture.research.md (+ ADRs under adr/),
  > dev-architecture.summary.md (for you). This defines how to run the product locally, how it is
  > tested in an AI-drivable way, and how the AI tooling is configured. The project spec is
  > complete and ready for implementation. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or,
  standalone, report the files + the must-answer forks).

Do NOT scaffold the project, write the compose files, or install tooling in this session unless
the user explicitly approves and asks.

## When the repo already has code

Design the inner loop around **what already runs**: read the existing compose file / Dockerfile /
Makefile / CI config / tests and take them as the starting point; parity gaps that already exist
become named risks. Do **not** re-open the stack (settled by `design-architecture`'s adopted ADRs).
What's missing (no e2e harness, no structured logging, no env lock) becomes an item
`setup-dev-environment` and `plan-development` fill later. Log differences in
`## Divergences (code vs intended)`. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

Re-run on an existing document — because an upstream phase was edited, or the user changed their
mind — and you **amend** rather than regenerate: reconcile
`dev-architecture.research.md` (+ ADRs) to the change instead of producing it from scratch. Per
**`../_shared/build-pipeline/propagation-method.md`**:

1. Read the changed upstream document and your current `dev-architecture.research.md`.
2. **Assess impact** — if this phase is not affected, self-skip: report "no change needed", touch nothing.
3. If affected, **amend surgically** — update only the parts the change touches in
   `dev-architecture.research.md` (and `dev-architecture.summary.md` if the essence changed), and
   **update or supersede an affected ADR rather than rewriting its history**, **preserving the
   `## Forks / Decisions log`**. Never regenerate; do scoped research only for the changed part.
4. **Log it** — add a `## Forks / Decisions log` entry: what upstream changed, how this doc changed.
5. **Ask only on a critical question** (a decision-changing or low-confidence fork); otherwise proceed and log.
6. **Hand off, don't chase.** Say in one line what's next in the chain (nothing further in the spec) and offer to run it. If
   `.dev-skills/build-plan/tasks/` exists, add: the plan may now be stale — `/plan-development` will
   reconcile it with task deltas. The user decides how far to walk; you never edit the backlog here.

## Rules

1. Never produce the dev-architecture doc after the first message — load `architecture.research.md`
   and `user-flows.research.md` and work through the stages first.
2. Every local service, test, and tool traces to a component/technology in the stack or a flow —
   no orphan setup.
3. Prod-parity: local stand-ins mirror the prod service's API and behavior; every divergence is
   flagged as a risk.
4. Maximize the agent's verification surface: for **every** surface and flow the agent can
   **run it → drive it → prove the real outcome → unblock itself**, with no manual step. A surface
   the agent cannot autonomously verify is a defect, not a deferral.
5. Minimal, proven infra; never reproduce production's scale/HA locally or over-engineer the dev
   environment.
6. Never redesign the production architecture or re-open stack choices — surface gaps back to
   `design-architecture` instead.
7. Every *verified* tool fact is cited and every unverified one is labelled as such; every fork is
   logged; the review always runs (both modes) and its findings are always applied.
8. Design the **environment-access model** (advisory lock and/or per-run isolation), the
   **developer/test scripts** (fast, intentionally-divergent local paths), and the **custom project
   skills** that wrap those scripts/harness into named verification jobs as first-class deliverables —
   never leave the shared env uncoordinated, the agent without a fast path, or the verification loop
   uncodified. The custom skills complement `verification.md`; they never duplicate `verify-feature`.
