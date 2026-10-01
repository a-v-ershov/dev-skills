---
name: setup-production-environment
disable-model-invocation: true
description: "Turn the spec's deployment and analytics decisions into a live production environment: platform and release channel, production database with migrations and backups, config and secrets, hard spending caps, analytics and error tracking, optional CI. Sorts every gap into repo · authorized CLI with a yes · human in a dashboard; deploys, smoke-tests, writes a runbook."
argument-hint: "[--no-deploy] [<area>: platform | data | config | money | observability | ci]"
---

# Setup Production Environment Skill

You make the product **live for real people** — the outward-facing sibling of `setup-dev-environment`.
Everything production-related is yours: hosting, domain and TLS, the production database with
migrations, backups and restore, environment variables and secrets, hard spending caps, rate-limit
configuration, analytics and error tracking, CI and branch protection, the deploy — then **prove it
comes up**. Most of it lives in providers' dashboards, reachable only through an installed,
already-authorized CLI: **sort before you act**, and leave a runbook the human can follow without you.

## Inputs and outputs

- **Reads:** `.dev-skills/project-spec/architecture.research.md` (as decided by `design-architecture`)
  — your contract: **Deployment & environments** (incl. its *manual setup checklist*), **Analytics &
  telemetry** (question → metric → event, error visibility, privacy), the **threat model** (which
  surfaces need rate limits and caps) — plus `adr/*`; `.dev-skills/project-setup/verification.md` (how
  the stack is driven); **the code itself** for the environment variables it reads.
- **Writes:** repo-local deploy config (platform config file, `Dockerfile`, `.env.example`, CI
  workflow); `.dev-skills/project-setup/production-setup.md` (the record) and
  `.dev-skills/project-setup/production-runbook.md` (the plain-language deploy instruction), both
  committed. Never product feature code — a code change production needs is a task for `run-task`.

Per-category checklist (what "ready" means per area, derived from the stack):
**`references/production-checklist.md`**.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, environment-variable names or paths. Commit messages are always
English (the `commit` skill). **One branch — the current one** (normally `main`): never branch,
switch or open a worktree unless the user explicitly asked in this session —
**`../_shared/git-workflow.md`**.

## Modes

Read `mode` from `.dev-skills/build-plan/.build-config.md` (**`../_shared/build-pipeline/build-config.md`**).

- **interactive** — wait for approval of the three-group plan, then one explicit yes per external
  action.
- **autopilot** — may apply group ① (repo-local) without asking. **Group ② and the deploy still need an
  explicit yes, in both modes**; deploying to production is never a silent step.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the contract (deployment · analytics · threat model); probe which provider CLIs are authorized
- [ ] Stage 1: Detect state — what is already live: connected repo, deploy config, live URL, prod DB, applied migrations, env vars the code reads
- [ ] Stage 2: Scan — go through the checklist derived from THIS stack; detect only, change nothing
- [ ] Stage 3: Sort every gap into three groups: ① repo · ② authorized CLI, with a yes · ③ human in the dashboard
- [ ] Stage 4: Plan → approval — the three groups as the last message of the turn; wait
- [ ] Stage 5: Execute — ① small steps + green gate · ② one action, one yes · ③ exact steps to the human
- [ ] Stage 6: Deploy + smoke-test the LIVE version (skip with --no-deploy) — it comes up and the short path works
- [ ] Stage 7: Record — production-setup.md (✅ / 🔧 / ❓) + production-runbook.md ("how to ship", in plain language)
```

### Stage 0: Intake
Read the contract; no **Deployment & environments** section → stop and offer `/design-architecture`.
Then **probe, never recall**, which provider CLIs are installed *and authorized* (`gh auth status`,
`vercel whoami`, `supabase projects list`, `fly auth whoami`, `eas whoami`, … — whatever this project
uses). The probe sets the ②/③ boundary: run it first, show the result in one line. An area argument
narrows the run; `--no-deploy` stops before Stage 6.

### Stage 1: Detect state (read-only)
Never assume a first run: is the repository connected to a platform; is there a deploy config; does
a live URL answer; does a production database exist with migrations applied; which environment variables
does the code read (extract the list — everything else is checked against it), which carry the
framework's **public** prefix; is an error tracker or analytics client wired in. Summarize so the human
can correct you before you plan.

### Stage 2: Scan (detect only)
Work **`references/production-checklist.md`** for *this* project's technologies — platform & release
channel · data · configuration & secrets · money · observability · CI (optional). Change nothing; touch
no external service.

### Stage 3: Sort into three groups
Every gap goes into exactly one group (a finding may split: "remove the hardcoded key from the code" ①
*and* "rotate it at the provider" ② or ③):

- **① I do it myself, in the repo** — the platform config file, `.env` in `.gitignore`, a refreshed
  `.env.example`, a renamed wrongly-public variable, a CI workflow, a rate-limit setting in code, the
  analytics client and error tracker the architecture chose, reading their keys from the environment.
- **② Through an authorized CLI — with your explicit yes** — set environment variables on the platform,
  apply migrations to the production database, enable branch protection, attach a domain where the CLI
  can, and **the deploy itself**. Each is **external and often irreversible**: run it only on a yes
  **for that action**, and name the irreversible ones (a store release, a package publish, a migration
  on live data) **before** running them.
- **③ Only you, in the provider's dashboard** — no CLI path, or it needs the human's account, decision
  or money: connecting the repository to the platform, buying a domain, turning on **hard** spending
  caps, enabling database backups, confirming the production/test data split. For each: what, why,
  where (a link), and **what to bring back** (usually a value for an environment variable).

### Stage 4: Plan → approval
Show the plan **as three groups, in a message that ends the turn** (some interfaces hide text written
before a tool call). Wait for a yes.

### Stage 5: Execute the approved plan
- **Group ①** — small steps, the project's `make check` after each (a deploy-config or CI change must
  not break the build); follow the platform's **current official instructions**, not memory.
- **Group ②** — one action at a time, each after its own yes; confirm the CLI is still authorized right
  before the call.
- **Group ③** — short, exact steps to the human; **wait where the rest depends on it** (no deploy before
  the environment variables exist).

### Stage 6: Deploy + smoke-test the live version
**Nothing is verified until the product is deployed.** With auto-deploy, a connected repository ships
on a push to the tracked branch; everywhere else (a store, a package registry, an installer, no
auto-deploy) shipping is a group ② action: propose the stack's own command, run it **only on an
explicit yes**.

Then **observe the live product** on the short path — it comes up, sign-in works, the main scenario
reaches its outcome (web: the page at the real address renders; mobile/desktop/CLI: install the built
artifact and run it once). Not up → a finding, not "done". **"The config looks right" and "no errors
in the logs" are not proof.**

### Stage 7: Record + runbook
Write `.dev-skills/project-setup/production-setup.md` in three parts: **✅ done / verified** (with what
the smoke test proved) · **🔧 your turn in the dashboard** (group ③ and anything still waiting, with
links) · **❓ still open** (what you cannot see from here — whether a variable was really set, whether
preview really points away from the production database).

Then write `.dev-skills/project-setup/production-runbook.md` and **end the turn with it**: a numbered
3–6 step **"how to ship"** for this project — who does each step (you in the dashboard · me by command,
say yes) and exactly which button or command, never "set up the deploy"; **how to tell it worked**
(which address to open, what should be visible); **next time**, in one line (usually "push to `main`,
the rest is automatic"); **how to roll back**. Expand each term in parentheses on first use — the
reader is often not the code's author. If something in ✅/🔧 blocks a step, say which step hits the
wall and why.

## Rules

1. **Execute the spec, never re-decide it** — platform, database, regions, budget and analytics plan
   come from `architecture.research.md`; a wrong one is a spec change (`/design-architecture`): say so
   and stop.
2. **Three groups before any action**; every external or irreversible action is named as such
   **before** it runs, with its own yes, in both modes.
3. **Detect first, change second** — nothing is touched before the scan is done and the plan approved.
4. **Never print a secret's value** — in the plan, log, runbook or chat; name the variable and its
   location. A leaked key is **rotated** at the provider, never merely deleted from the code.
5. **The checklist comes from this project's stack** — "preview", "domain" and "spend cap" are web
   examples; a mobile, desktop or CLI product has its own.
6. **Readiness is proven live**, never by config that "looks right".
7. **End with the runbook, not the report** — the human must leave knowing what to press, not only the
   state.
8. **Never decide money, domain or the production/test split** for the human — show, recommend, let
   them choose and pay.
9. **CI and backups are offered, not required** — they do not gate the deploy, but a product whose data
   loss was called painful does not ship without a tested restore path.
10. **Audits install nothing** — the `audit-*` skills only audit; a production capability a
    `release-product` audit finds missing (error tracking, spend cap, rate limit) comes back here.
11. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
