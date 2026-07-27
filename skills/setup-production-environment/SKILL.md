---
name: setup-production-environment
disable-model-invocation: true
description: "Turn the spec's deployment and analytics decisions into a real production environment, and put the product live. The outward-facing sibling of setup-dev-environment: where that one makes the local inner loop real, this one makes the PRODUCTION side real — the deploy platform and release channel, the production database with its migrations and backups, the configuration and secrets set in the target environment (not just in a local .env), hard spending caps on every paid provider, the analytics events and error tracking the architecture committed to, and optionally CI + branch protection. Not tied to a stack: what production needs is derived from THIS project's technologies and from .dev-skills/project-spec/architecture.research.md, never from a fixed list. Every gap is sorted into three groups and only then acted on: what the skill does itself in the repo, what it can do through an already-authorized provider CLI (an external, often irreversible action — only on an explicit yes, one at a time), and what only the human can do in a provider's dashboard (with the exact steps and what to bring back). Ends by deploying and smoke-testing the LIVE version — readiness is proven by the deployed product actually coming up and its short path working, never by 'the config looks right' — and writes a runbook in plain language: what to press to ship, how to tell it worked, what to do next time, how to roll back. Run it by hand whenever production changes; it is never auto-run by the release phase. Audits only audit — anything production needs installed is installed here."
argument-hint: "[--no-deploy] [<area>: platform | data | config | money | observability | ci]"
---

# Setup Production Environment Skill

You are the engineer who makes the production side real. `setup-dev-environment` made the inner loop
runnable on one machine; you make the product **live for real people** — the platform, the production
data, the configuration in the target environment, the spending caps, the telemetry — and then you
**deploy it and prove it comes up**.

Most of your work does not live in the repository. It lives on a deploy platform and in providers'
dashboards, where an agent has no access unless a CLI is installed and already authorized. That single
fact shapes everything below: you **sort before you act**, you never touch an external service without
an explicit yes, and you finish with a plain-language runbook rather than a report, because the human
has to be able to do this again next month without you.

You **execute the spec, you do not re-decide it.** The platform, the database, the regions, the budget,
and the analytics plan were settled in `design-architecture`. If one of them turns out to be wrong,
say so and stop — that is a spec change (`/design-architecture`), not a call to make here.

## Scope discipline (read carefully)

- **Everything production-related belongs here.** Hosting, domain and TLS, the production database and
  its migrations, backups and restore, environment variables and secrets in the target environment,
  hard spending caps, rate-limit configuration, analytics and error tracking, CI and branch
  protection, and the deploy itself. The `audit-*` skills **only audit** — they never install or
  configure anything. When an audit needs something that does not exist in production, it is a finding
  and it comes back here.
- **Three groups, always** (below). Nothing external happens before the plan is approved and, for each
  external action, an explicit yes on that action.
- **Never print a secret's value** — in the plan, the log, the runbook, or the chat. Name the variable
  and where it goes. A leaked key is rotated at the provider, never merely deleted.
- **The human owns the money and the data.** You never decide the production/test data split, the
  domain, or a spending limit; you show what's missing, they decide and pay.

## Inputs and outputs

- **Reads:** `.dev-skills/project-spec/architecture.research.md` — your contract: the **Deployment &
  environments** section (platform, environments, domain & TLS, secrets, backups, and its *manual setup
  checklist*), the **Analytics & telemetry** section (question → metric → event, error visibility,
  privacy), and the **threat model** (which surfaces need rate limiting and caps) — plus `adr/*`. Then
  `.dev-skills/project-setup/verification.md` (how the stack is driven) and **the code itself** for the
  list of environment variables it actually reads.
- **Writes:** repo-local deploy config (platform config file, `Dockerfile`, `.env.example`, CI
  workflow), `.dev-skills/project-setup/production-setup.md` (the record — done / your turn / open) and
  `.dev-skills/project-setup/production-runbook.md` (the plain-language deploy instruction). Both are
  committed project documentation. Never product feature code — a code change production needs is a
  task for `run-task`.

The full per-category checklist (what "ready" means for each area, and how it is derived from the
stack): **`references/production-checklist.md`**.

## Language

Respond and reason in whatever language the user addressed you in — write the plan, the questions, the
record, and the runbook in that language and think in it too. Never translate code, identifiers,
commands, environment-variable names, or file paths. (Commit messages stay English — the `commit` skill.)

## Modes

Read `.dev-skills/build-plan/.build-config.md` for `mode` (**`../_shared/build-pipeline/build-config.md`**).

- **interactive** — present the three-group plan and wait for approval; then one explicit yes per
  external action.
- **autopilot** — may apply group ① (repo-local) without asking. **Group ② and the deploy still stop
  for an explicit yes, in both modes** — they are external and often irreversible. Autopilot never
  turns "deploy to production" into a silent step.

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
Read the contract above. Then **probe, never recall**, which provider CLIs are installed *and
authorized* — `gh auth status`, `vercel whoami`, `supabase projects list`, `fly auth whoami`,
`eas whoami`, `railway whoami`, `wrangler whoami`, whatever this project's providers are. That probe is
what decides the boundary between group ② and group ③, so it is done first and its result is shown to
the human in one line. An area argument narrows the run to that area; `--no-deploy` stops before Stage 6.

If `architecture.research.md` has no **Deployment & environments** section, stop and offer
`/design-architecture` — production set up against no decision is production set up against your guess.

### Stage 1: Detect state (read-only)
Probe what already exists, and never assume a first run: is the repository connected to a platform, is
there a deploy config in the tree, does a live URL already answer, does a production database exist and
are its migrations applied, which environment variables does the code actually read (extract the list
from the code — this is the list everything else is checked against), which of them carry the
framework's **public** prefix, is an error tracker or analytics client already wired in. Show what you
found in a short summary so the human can correct you before you plan anything.

### Stage 2: Scan (detect only)
Work the checklist in **`references/production-checklist.md`**, built from *this* project's
technologies — platform & release channel · data · configuration & secrets · money · observability ·
CI (optional). Detect only. Nothing is changed and no external service is touched in this stage.

### Stage 3: Sort into three groups
Every gap goes into exactly one group (a single finding may split across two — "remove the hardcoded
key from the code" ① *and* "rotate it at the provider" ② or ③):

- **① I do it myself, in the repo.** Things that live in the repository: the platform config file,
  `.env` in `.gitignore`, a refreshed `.env.example`, a renamed wrongly-public variable, a CI workflow,
  a rate-limit setting in code, the analytics client and error tracker the architecture chose, wired to
  read their keys from the environment.
- **② I can do it through an authorized CLI — with your explicit yes.** Things that normally live in a
  dashboard but the CLI from Stage 0 can reach: set environment variables on the platform, apply
  migrations to the production database, enable branch protection, attach a domain where the CLI can,
  and **the deploy itself**. Every one of these is an **external, often irreversible action**: propose
  it, run it only on a yes **for that action**, and say plainly which ones cannot be undone (a store
  release, a package publish, a migration on live data) **before** running them.
- **③ Only you, in the provider's dashboard.** No CLI path, or it needs the human's account, decision,
  or money: connecting the repository to the platform, buying a domain, turning on **hard** spending
  caps, enabling database backups, confirming the production/test data split. For each: what, why,
  where (a link), and **what to bring back** (usually a value to put in an environment variable).

### Stage 4: Plan → approval
Show the plan **as three groups, in a message that ends the turn** — in some interfaces text written
before a tool call is not visible, and the human must read the plan before approving it. Wait for a
yes. This skill changes the repository and touches external services; nothing happens without it.

### Stage 5: Execute the approved plan
- **Group ①** — small steps, with the project's own check (`make check`) after each: a deploy-config or
  CI change must not break the build. Follow the platform's **current official instructions** rather
  than memory; config formats go stale fast.
- **Group ②** — one action at a time, each after its own yes. Confirm the CLI is still authorized right
  before the call. Name an irreversible action as irreversible before running it.
- **Group ③** — hand the human short, exact steps and **wait where the rest depends on it** (there is
  no point deploying before the environment variables exist).

### Stage 6: Deploy + smoke-test the live version
**There is nothing to verify until the product is deployed.** On a platform with auto-deploy, a
connected repository means a push to the tracked branch ships it and no separate command exists;
everywhere else (a store, a package registry, an installer, a platform without auto-deploy) shipping is
a group ② action: propose the stack's own command and run it **only on an explicit yes**.

Then **prove readiness by observing the live product**: open the deployed version and walk the short
path — it comes up, sign-in works, the main scenario reaches its outcome (web: the page at the real
address renders; mobile/desktop/CLI: install the built artifact and run it once). It does not come up →
that is a finding, not "done". **"The config looks right" and "no errors in the logs" are not proof.**

### Stage 7: Record + runbook
Write `.dev-skills/project-setup/production-setup.md` in three parts: **✅ done / verified** (with what
the smoke test proved) · **🔧 your turn in the dashboard** (group ③ and anything still waiting, with
links) · **❓ still open** (what you cannot see from here — whether a variable was really set, whether
preview really points away from the production database).

Then write `.dev-skills/project-setup/production-runbook.md` and **end the turn with it, not with the
record**: a numbered 3–6 step **"how to ship"** written for this project — who does each step (you in
the dashboard · me by command, say yes) and exactly which button or which command, never "set up the
deploy"; **how to tell it worked** (which address to open, what should be visible); what to do **next
time**, in one line (usually "push to `main`, the rest is automatic"); and **how to roll back**. Expand
each term in parentheses on first use — the reader is often not the person who wrote the code. If
something in ✅/🔧 blocks a step, say which step will hit the wall and why.

## Rules

1. **Execute the spec, never re-decide it.** Platform, database, regions, budget, and the analytics
   plan come from `architecture.research.md`. A wrong decision is a spec change, not a setup call.
2. **Three groups before any action** — repo · authorized CLI with a per-action yes · human in the
   dashboard. Every external and irreversible action is named as such **before** it runs, in both modes.
3. **Detect first, change second.** Nothing is touched before the scan is done and the plan approved.
4. **Never print a secret's value** anywhere — name the variable and its location. A leaked key is
   **rotated** at the provider, never merely deleted from the code.
5. **The checklist comes from this project's stack**, not from a fixed list — "preview", "domain", and
   "spend cap" are web examples; a mobile, desktop, or CLI product has its own.
6. **Readiness is proven live.** The deployed product comes up and its short path works, or it is not
   ready. Config that "looks right" proves nothing.
7. **End with the runbook, not the report.** The record says what state things are in; the runbook says
   what to press. The human must not leave with only a state.
8. **Never decide money, domain, or the production/test split** for the human — show, recommend, let
   them choose and pay.
9. **CI and backups are offered, not required** — they do not gate readiness to deploy, but a product
   whose data loss was called painful does not ship without a tested restore path.
10. **Audits install nothing** — if a `release-product` audit reports a missing production capability
    (no error tracking, no spend cap, no rate limit), it comes back here as the fix.
