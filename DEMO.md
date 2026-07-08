# Buildloop — webinar demo runbook

> **Branch `buildloop-simple-demo` only.** This is a stripped-down teaching variant of Buildloop for a
> live vibe-coding webinar. It is **not** the real method and must never merge to `main`. Three demo
> skills — `demo-spec`, `demo-build`, `demo-release` — show the same before/after arcs the real
> pipelines do, but fast enough for a live slot. Where the mechanism itself is the "wow" (the
> independent verifier, the real audits) the demo keeps it **real**; only the slow surrounding
> machinery is stripped.

## The three acts (before → after)

Each act is a pair: the co-host does the **before** live (a cold chat, a naive prompt), then Alexander
shows the **after** with a demo skill. The example project throughout is a **service that generates SEO
articles** (with a user dashboard). Alexander provides that project repo separately (the "заготовка").

| # | Act | Before (co-host, live) | After (demo skill) | The payoff to show |
|---|-----|------------------------|--------------------|--------------------|
| 1 | **PRD** | `"make me a plan for an SEO article service"` → vague blob | `demo-spec` | Claude **interrogates** the idea → a slim but checkable spec |
| 2 | **Build + verify** | `"add feature X"` → "works, ship it" | `demo-build` | A **second, independent agent finds real bugs** in the first's work |
| 3 | **Deploy checklist** | just deploy and hope | `demo-release` | A **pre-deploy checklist** catches leaked keys / missing auth / slow queries |

## What each demo skill does (and deliberately skips)

- **`demo-spec [idea]`** — a fast, shallow PRD grill: 3–6 sharp questions (batched, each with a
  recommended answer), then writes slim `product-requirements` / `architecture` / `dev-architecture`
  docs under `.buildloop/project-spec/`. Skips gather-context, validate-idea, user-flows, the design
  phases, research subagents, and adversarial review. ~5–15 min. The architecture doc carries the trust
  boundaries + a STRIDE-lite note so Act 3 has a contract; the dev-architecture doc names the concrete
  verification commands so Act 2 can run.
- **`demo-build [feature]`** — builds **one** feature with the **real** `implementer` + `verifier`
  agents. Writes a single throwaway task file (no kanban), spawns the implementer, then the **separate**
  verifier that authors adversarial tests and finds bugs. **Hard-capped at 2 implement↔verify
  iterations** (usually 1 is enough). Does not commit unless asked.
- **`demo-release [--audit …]`** — spawns the **real** `audit-security` + `audit-performance` as
  fresh, read-only subagents **in parallel**, in **report-only** mode (no rework tasks, no fixes, no
  ship), and renders their findings as a green/red **pre-deploy checklist**.

## Run order & timing strategy

The honest bits still take real time (the verifier writes and runs tests; the audits probe the stack).
For the live slot:

1. **Pre-run everything before the webinar** on the SEO-service repo and keep the transcripts/logs.
2. **On air**, either:
   - re-run a **small** slice live (e.g. `demo-spec` grilling — that's interactive and fast), and/or
   - **kick off** the slow act live (`demo-build` on a feature with an obvious error path), narrate the
     mechanism for ~5 min while it works, then **cut to the pre-run log** for the payoff (the verifier's
     caught bugs / the checklist) rather than waiting for completion.
3. Say the honest line each time: *"in a real build this runs across a full kanban backlog, task after
   task; the full spec takes hours with research and review; here it's compressed for the demo."*

## Setup for the demo project

- Install this branch's plugin into the SEO-service repo (`/plugin marketplace add ./` from this repo on
  the `buildloop-simple-demo` branch, or copy `skills/` into the project's `.claude/skills/`).
- **Act 2 needs a verification contract** — `.buildloop/project-setup/verification.md` (how to bring the
  stack up + drive/prove a surface). Either run the real `setup-dev-environment` once on the SEO repo, or
  let `demo-build` write a minimal one inline. Without it the verifier can't drive the stack.
- **Act 3 needs the project present** so the audits can probe (and the stack up for dynamic checks — the
  audits bring it up themselves).

## Picking the Act 2 feature (so the bug is visible)

Choose a feature with an obvious negative/error path — a form with validation, an auth-gated resource
(dashboard article owned by user A, requested by user B), a quota/limit. That's where the implementer's
happy-path bias shows and the verifier catches it — which is exactly the moment worth showing. Avoid
trivially-correct features; both approaches nail those and there's no contrast.

## Boundaries (keep the demo honest and safe)

- Never merge `buildloop-simple-demo` into `main`. The real skills stay untouched.
- Don't bump the plugin version for the demo (`.claude-plugin/plugin.json` is owned by the user).
- The demo skills say out loud what the real pipeline adds — don't let "compressed for demo" read as
  "this is all there is".
