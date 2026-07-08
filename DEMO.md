# Buildloop — webinar demo runbook

> **Temporary demo bundle.** This is a stripped-down teaching variant of Buildloop for a live
> vibe-coding webinar. It is **not** the real method. It lives on branch `buildloop-simple-demo` and is
> **temporarily merged into `main`** so it installs cleanly on another machine (`/plugin marketplace add
> a-v-ershov/buildloop` pulls the default branch) — revert/remove it after the webinar. Three demo
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

- **`demo-spec [idea]`** — the **real staged flow, compressed**: four sequential stages with a gate
  between each — (1) **gather-context** interview + critical pushback → recap gate; (2) **functional
  requirements** presented → ok/not-ok gate → write doc; (3) **architecture** proposed (options + trust
  boundaries + STRIDE-lite) → gate → write doc; (4) **dev-architecture** (the verification tooling, e.g.
  Playwright) → gate → write doc. Under `.buildloop/project-spec/`. Cuts only the slow machinery (research
  subagents, adversarial review, dual outputs) and the extra phases (validate-idea, user-flows, design) —
  never a stage or a gate. The architecture doc carries the trust boundaries + STRIDE-lite so Act 3 has a
  contract; the dev-architecture doc names the concrete verification tools so Act 2 can run.
- **`demo-build [feature]`** — builds **one** feature with the **real** `implementer` + `verifier`
  agents. Writes a single throwaway task file (no kanban), spawns the implementer, then the **separate**
  verifier that authors adversarial tests and finds bugs. **Hard-capped at 2 implement↔verify
  iterations** (usually 1 is enough). Does not commit unless asked.
- **`demo-release [--with-performance]`** — spawns the **real** `audit-security` (the star of the act)
  as a fresh, read-only subagent in **report-only** mode (no rework tasks, no fixes, no ship, no version
  bump), and renders its findings as a green/red **pre-deploy checklist** — the point being it *finds
  real security problems* (leaked keys, missing auth, injection). `audit-performance` is optional via
  `--with-performance`.

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

- The merge into `main` is **temporary**, only to make cross-machine install easy — plan to revert it
  (drop the demo skills + `DEMO.md`, restore the version) once the webinar is done. The real skills stay
  untouched by the demo ones either way.
- The demo skills say out loud what the real pipeline adds — don't let "compressed for demo" read as
  "this is all there is".
