# Elicitation topics — the three pillars (design-dev-architecture)

The full topic catalogue for Stage 1, and the probe list Stage 4's reviewer works from. Read this at
the stage that needs it; the `SKILL.md` carries only the shape.

Interview technique — **`../../_shared/spec-pipeline/elicitation-method.md`**: one thread at a time, a
recommended answer on every question, push past the first answer, mirror back to confirm. When a fork
is blocked on context only the user holds, invoke `gather-context` scoped to it.

---

## Pillar 1 — local-run architecture (prod-parity, one command — "Run it")

Per component: the **local stand-in** for any cloud/managed service, chosen for **API parity with the
specific provider the architecture picked** — the emulator or container that matches that vendor, not
a generic equivalent (an S3-API-compatible container like MinIO/LocalStack for a prod object store; a
database container matching the managed database's engine **and major version**; an emulator or
containerized OSS equivalent for a BaaS).

Three things that come straight from the architecture's deployment decision, cheap to settle now and
expensive to discover at deploy:

- **Build-shape parity** — locally you build the *same artifact shape* the chosen platform runs
  (serverless functions vs a long-lived process vs a container image) on the same major runtime
  version. Name the one command that produces it, so "works locally" means something.
- **Schema migrations** — the same mechanism locally and in production, with the agent able to apply
  *and* roll back. Seed data is not a substitute: seeding a fresh database never exercises the
  migration that will run against the real one.
- **The env-var contract** — the variables the chosen platform requires, mirrored in `.env.example`,
  plus a check that names what's missing before anything starts. A missing variable should fail loudly
  at bring-up, not silently at runtime.

Then the **Docker Compose topology** that brings the whole product up, the **seed data**, and
**env/secrets** handling (no real secrets in the repo).

**The single command** that starts everything seeded and ready — usable by **both the AI agent and a
human developer**: capture how a person brings it up and actually opens/uses the running product (the
local URL/port, default seeded login, where to watch logs), not just an agent-only harness. List the
**divergences** from prod, each a named risk.

Decide the **environment access model** — how concurrent actors avoid clobbering the one shared env:
an **advisory lock** baked into the bring-up command (lease + stale-reclaim) for a single heavy shared
stack, and/or **per-run isolation** (ephemeral data dir / unique compose project + port offset) where
it's cheap. Method: **`../../_shared/build-pipeline/env-access.md`**.

Specify the **developer & test scripts** the project needs — purpose-built local paths that
**deliberately diverge** from prod for speed: fast subset / single-stage runners (resume-from-stage,
skip the expensive stages), fixture / sample / pre-computed-intermediate generation, and
intermediate-output inspectors/visualizers. For each: its purpose, the **intentional divergence** from
prod and why it is an acceptable speed tradeoff (not a parity risk), and how the agent uses it to
drive/prove faster. `setup-dev-environment` scaffolds their skeletons; they are built out as backlog
tasks.

---

## Pillar 2 — the agent's verification loop (Drive it · Prove it · Unblock it)

The heart of the phase. For each surface the product has (drop one that doesn't apply), give the agent
the maximum, fastest way to close the loop. Fill the matrix:

| Move | UX / Frontend | Backend | E2E |
|------|---------------|---------|-----|
| **Run it** (one command) | dev server | `make dev` / `docker compose up` | bring up a staging-like env |
| **Drive it** (exercise the surface) | Claude-in-Chrome / Playwright | curl the route, hit health endpoints | run the flow against staging |
| **Prove it** (observe the real outcome) | screenshot before/after | query the DB — did the row land? · read structured logs — did the path run? | replay prod traffic; assert |
| **Unblock it** (remove what forces a human) | dummy auth · seed scripts for known state | structured logs the agent can grep · add log lines to prove the path ran | safe/idempotent test data |

Two things the architecture's analytics and design decisions add — both correctness, not ceremony:

- **Analytics never fires at the real counter during checks.** Point the client at a local sink or a
  no-op in the test environment; otherwise every verification run pollutes production numbers. Add
  "prove the event fired" to the loop **only for a flow whose acceptance criteria mention the metric**
  — elsewhere it is ceremony, and the event is checked by reading the sink, not by asserting on a mock.
- **The design system is checked by the gate, not by eye** — but only where the kit or stack already
  ships a rule for it (a Tailwind/ESLint plugin, the kit's own lint config, a token linter). Wire that
  existing rule into `make check-fast` — it is a static check, so it belongs in the target the
  pre-commit hook runs — so "components from the kit, colors from tokens" is enforced instead of hoped
  for. **Do not invent a custom grep-based checker**: a home-grown color-literal hunt produces false
  positives, and a noisy gate gets disabled.

Then the **test levels** (unit / integration / e2e), what each covers, and **test data**
provisioning/reset. Design them **bottom-heavy and selectable**, because the build loop pays for tests
on every task while the whole suite runs only at the release boundary
(**`../../_shared/build-pipeline/quality-gate.md`**):

- **Unit is the default level**, integration is for real seams, **e2e is the exception** — reserved for
  a person's path across a screen that cannot be proven below. Say so explicitly in the doc, or the
  suite drifts browser-heavy and every later task pays for it.
- **Specify how a selection is run** — the scoped command for this stack (`pytest -k` / `vitest run
  <path>` / `playwright --grep @tag`) and the tagging or folder convention that makes tests addressable
  per area and per task. This is what `setup-dev-environment` turns into `make test-scoped`; without it
  the loop can only choose between everything and nothing. **Say what happens when the selector finds
  nothing** for a changed module — that is a gap to report, never a licence to run the whole suite.
- **Name the test-cost settings for slow-by-design primitives** (Argon2/bcrypt work factor, retry
  backoff, rate limits) and how they are switched — the difference between a 33-second and a 95-second
  suite.
- **Name the release-phase measurement tooling** for this stack — the duplication / dead-code analyzer,
  the mutation-testing runner, the accessibility checker, the load tool — because
  `setup-dev-environment` installs them and the release phase is forbidden to. An unnamed tool means
  `refactor`, `write-tests` and the audits later record that signal as *unmeasured*. Name what the
  stack actually has; "none available" is a legitimate answer, silence is not.

**Map each flow** from `user-flows.research.md` to *how the agent drives it* and *how it proves
success* (including important alternate/error paths). Each flow's **acceptance criteria** (and
per-state assertions) are the proof targets — map every AC to the concrete check that asserts it. The
bar: for every flow and surface, the agent can run → drive → prove **with no manual step**.

---

## Pillar 3 — AI-development tooling (tuned to the stack — widens the loop)

The **Claude Code config** (project `CLAUDE.md` content, useful `settings.json` hooks and the
permissions the loop needs — **`../../_shared/build-pipeline/env-access.md`** → "Permissions the loop
needs"); the **MCP servers** that give the agent more reach (browser-driving, db, cloud/log access,
HTTP); the **recommended Anthropic / Claude Code plugins & skills** that improve development &
verification for *this* stack, and why; and equivalent config for **other agents** the team uses.
Choose tooling for how much verification power it hands the agent, not by fashion.

Where the brief records **dev-tooling preferences**, treat them as **soft priors** — fold them into
this pillar's choices and log each as a fork with `Source = preference`
(**`../../_shared/spec-pipeline/elicitation-method.md`** → "Read the brief first"). Code-style
leanings are already settled: `define-code-style` distilled them into
`.dev-skills/project-spec/code-style.md` — have the project `CLAUDE.md` content **point at that
guide** rather than restating conventions here.

Then specify the **custom, project-local Claude Code skills to author** that wrap the dev/test scripts
(pillar 1) and the verification loop (pillar 2) into named, invocable jobs — beyond *installing
existing* plugins, this is *authoring new* skills around **this** project's own scripts. Keep them
**workflow-level** (a small set covering whole verification jobs — `/run-integration-tests`,
`/verify-flow <name>`, `/reset-env` — not a thin alias per script). For each name:

- its **verb-name** plus a discoverable third-person `description` (WHAT it does, WHEN to use it);
- the **script(s) / harness it wraps**;
- the **procedure it encodes** (bring up env → drive → assert the observable outcome → report);
- **when the agent invokes it**.

They live in the built project's `.claude/skills/<name>/SKILL.md`, are **committed**, follow standard
skill-authoring shape (a thin body that runs the wrapped script and reads its result — the depth is in
the script, not the skill), and **complement `verification.md`**: they reuse its commands for ad-hoc
development and fixing, they do **not** duplicate `verify-feature` or re-do what a script already does.
`setup-dev-environment` scaffolds each skeleton; full authoring is a backlog task
(`plan-development`), blocked on the script it wraps.

---

## Research topics (Stage 2)

- the candidate local stand-in's **API parity & coverage** with the prod service — which APIs it really
  implements;
- the **browser-driving + e2e** options for the stack (Claude-in-Chrome / a browser MCP / Playwright)
  and their current capabilities;
- **health-check, DB-assertion and traffic-replay** tooling for the backend;
- a **structured-logging** library the agent can grep;
- which **MCP servers** exist and give the agent more verification reach (browser / db / cloud-logs /
  http);
- which **Claude Code / Anthropic plugins & skills** are current and help this stack;
- the container images in play and their maintenance status.

---

## What the reviewer probes (Stage 4)

Above all, **gaps in the agent's verification loop**:

- a surface or flow the agent can run but **cannot prove** the outcome of (no screenshot / DB / log
  assertion — "it ran" passed off as proof);
- a flow with no autonomous drive path;
- auth or unknown-state friction left in place that forces a human in;
- logs the agent can't grep.

Then the usual: a claimed local-stand-in parity with no source behind it; an e2e harness that secretly
needs a human; a tool/plugin/MCP asserted to exist with nothing cited; a local service or test that
traces to no component or flow; over-built infra (reproducing prod HA locally); secrets in the compose
file; a divergence that is understated.

Then the deployment-facing gaps: a local build shape that doesn't match what the chosen platform runs;
no migration path (or one seeding can't stand in for); a platform-required env var absent from the
local contract; analytics that would fire at the production counter during checks.

Then the loop's economics: a developer/test script whose purpose or intentional divergence isn't
documented (or one drifting toward re-implementing prod); **no fast path**, forcing the agent to run
the full expensive stack to verify a small change; **no way to run a selection of tests** (no scoped
command, no tagging or folder convention), which leaves the build loop choosing between the whole suite
and nothing; a **top-heavy test design** that puts at e2e what unit or integration would prove;
slow-by-design primitives with no test-cost setting named; an env two actors can clobber with no lock
or isolation, or a lock with no stale-reclaim (a killed agent deadlocks the env).

And on the **custom project skills**: one that duplicates `verify-feature` or just restates
`verification.md`; one wrapping a script that doesn't exist (or isn't a planned dev/test script); a
thin one-per-script alias that adds no procedure; or the inverse — a clearly-useful verification job
(run integration tests, reset the env, drive a flow end-to-end) with **no** skill wrapping it.

---

## Why each principle is there

The operating principles in full, each with the failure it prevents.

- **The agent's verification surface is the deliverable.** For every surface the product has, the agent
  must be able to **run it, drive it, prove the real outcome, and unblock itself** — autonomously.
  Optimize for the breadth and speed of that loop above convenience or elegance.
- **Prove the real outcome, not "it ran".** Every verification ends in an observable proof the agent
  can read — a screenshot diff, a DB row that landed, a structured log line, an asserted response —
  checked against the flow's **acceptance criteria** from `user-flows.research.md`, not an ad-hoc guess.
- **Unblock autonomous runs by design.** Anything that would force a human in — real auth, unknown
  state, unreadable logs, a permission prompt on reading the harness's own output — is removed up
  front: dummy/seedable auth, seed scripts, structured logs, the read permissions the loop needs.
- **Prod-parity over convenience**, and flag every remaining local↔prod divergence explicitly.
- **Two axes of local fidelity — don't conflate them.** Parity **stand-ins** *mirror* prod (each
  divergence is a risk to close). **Developer/test scripts** *deliberately diverge* for speed — a
  documented, intentional tradeoff, not a risk. Design both.
- **Bottom-heavy and selectable tests.** Unit by default, integration for real seams, e2e the
  exception; and a **named way to run a selection**, because the build loop pays for tests on every
  task (**`../../_shared/build-pipeline/quality-gate.md`**).
- **Codify the loop into named skills.** Specify **custom, project-local Claude Code skills** that wrap
  the dev/test scripts and harness into whole verification jobs — workflow-level, not one alias per
  script. They complement `verification.md`; they never duplicate `verify-feature`.
- **The shared env is a single resource.** Coordinate access (advisory lock with lease + stale-reclaim)
  or isolate per run — never let two actors clobber it, never let a killed holder deadlock it
  (**`../../_shared/build-pipeline/env-access.md`**).
- **One command to run it all — for the human too.** A person must be able to bring the whole thing up
  and actually open and use the running product, not just an agent-only harness.
- **Tool facts are researched, not assumed** (stage 2), and **everything traces** to a component,
  technology or flow. Boring, minimal infra — never reproduce production's scale or HA locally.
- **Take a position.** Name the anti-pattern: a local setup that silently drifts from prod, mocks that
  mask integration bugs, e2e that needs a human, resume-driven tooling, secrets in the compose file.
