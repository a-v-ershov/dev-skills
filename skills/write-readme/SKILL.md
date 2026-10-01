---
name: write-readme
description: "Write or refresh the README as a handover document: what the project is, how a stranger clones and runs it, how it is deployed, what they must bring, how to reach a clean seeded state. Every command verified against the repo; the unverifiable is written as unknown. Run by release-product or standalone. Read-only on product code; writes README.md."
argument-hint: "[dev-only | prod-only]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/README.md' '*/README.*.md' '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Write Readme Skill (the handover document)

You write the file a **second person** opens first: *what is this, how do I run it, how do I ship it,
what must I bring?* The test: **a stranger with a fresh clone gets the dev environment running from
this file alone** and knows which steps only they can do; where they would stall, the step is not
finished.

Scope: `README.md` (and an existing sibling like `README.ru.md`), nothing else. It is **not the
runbook** — `production-runbook.md` (from `setup-production-environment`) stays the owner's manual,
pointed at; the README covers a newcomer's dev environment plus an honest account of production.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Write the
README in **the language the project's existing docs use** — none → ask once. Never translate code,
identifiers, commands or paths. Commit messages are always English. **One branch — the current one**
(normally `main`): never branch, switch or open a worktree unless the user explicitly asked in this
session — **`../_shared/git-workflow.md`**.

## Modes

Read `mode` from `.dev-skills/release/.release-config.md` (or `.dev-skills/build-plan/.build-config.md`
outside the release phase); default **interactive**.

- **interactive** — show the outline and the unverified claims before writing; confirm a rewrite.
- **autopilot** — write it and report what could not be verified.

`dev-only` skips the production half; `prod-only` refreshes only the deployment section.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the existing README (if any) + the spec/setup/production records; pick the language
- [ ] Stage 1: Establish the dev path — the real clone→run sequence, verified against the repo, ideally executed
- [ ] Stage 2: Establish the prod path — what deploying actually takes today, and what is missing
- [ ] Stage 3: Establish "what you must bring" — accounts, secrets, licences, data that is not in git
- [ ] Stage 4: Establish the clean state — reset, seed, and any asset the repo does not carry
- [ ] Stage 5: Write / refresh README.md — sections below; every unverified line marked
- [ ] Stage 6: Report — what changed, what could not be verified, what the human must fill in
```

### Stage 0: Intake
Read, in order: the current `README.md` (never blow it away);
`.dev-skills/project-spec/product-requirements.summary.md`; `.dev-skills/project-setup/setup-log.md`
and **`verification.md`** for the real commands; `.dev-skills/project-setup/production-setup.md` and
`production-runbook.md` if present; the root `CLAUDE.md`; the entry points — `Makefile`, manifest
scripts, compose file, `.env.example`, `.gitignore` (**what a clone does not contain**).

### Stage 1: The dev path (verified)
Prerequisites (versions from the manifest or toolchain files, not memory), clone, install, configure,
bring up, and **how they know it worked** (URL, seeded login, what they see). **Run** what is cheap and
non-destructive (`make help`, `docker compose config`, `--version`); otherwise confirm the target exists
in its defining file. Unchecked → `⚠ unverified` in your report, never in the README.

### Stage 2: The prod path (honest)
**Could this person deploy it?** Read `production-setup.md`. Three acceptable outcomes:

- **Deployable** — platform, command, what to watch; point at `production-runbook.md` for detail.
- **Deployable with gaps** — each gap a bullet: account, secret, DNS record, a migration only run locally.
- **Not established** — one line pointing at `/setup-production-environment`. Never reconstruct a
  deployment story from the architecture doc — it records a *decision*, not *what exists*.

### Stage 3: What you must bring
What a clone lacks and cannot generate: provider accounts, API keys and where to obtain each,
licences, a domain, files excluded by `.gitignore`. For each: what it is, where it goes (the variable
name from `.env.example`), whether dev works without it (often degraded — say how).

### Stage 4: The clean state
Reset command, seed command, what the seed contains, and **assets the repo does not carry**
(gitignored fixtures, audio, sample media, a database dump): how they are produced, or plainly that
they must be obtained.

### Stage 5: Write it
Sections, in order; skip any that does not apply:

1. **What this is** — two or three sentences, from the product summary.
2. **Requirements** — with versions.
3. **Run it locally** — the verified sequence, then "you should see …".
4. **Everyday commands** — dev, tests, the gate, reset, from `verification.md`.
5. **What you must bring** — Stage 3.
6. **Deploying** — Stage 2, at its honest level.
7. **Getting back to a clean state** — Stage 4.
8. **Where the documentation lives** — the `.dev-skills/` map and the root `CLAUDE.md`, one line each.

### Stage 6: Report
What changed, every claim you could **not** verify and why, then **«What you should do»**
(**`../_shared/build-pipeline/report-format.md`**) — typically: create the accounts only they can,
confirm the deploy story, or run `/setup-production-environment` if production is unestablished.

## Rules

1. **Every command is verified against the repo**; the unverifiable is written as unknown, never a
   plausible guess ("Deployment: not established in this repository — see `production-setup.md`", not
   an invented `npm run deploy`).
2. **Never write a secret's value** — variable names and where to get one, never the one in `.env`.
3. **Refresh, don't regenerate** — keep the structure and hand-written prose still true, correct drift,
   add what is missing.
4. **Product code is never touched.** A missing script or broken command is a finding, and a task if
   it matters.
