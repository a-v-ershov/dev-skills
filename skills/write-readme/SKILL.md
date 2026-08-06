---
name: write-readme
description: "Write or refresh the repository README as a handover document — what the project is, how another person clones it and gets the dev environment running, how a release is deployed to production, what they must bring themselves (accounts, secrets, licences), and how to get back to a clean seeded state. Use in the release phase (run by release-product before the manual-test briefing) or standalone whenever someone else has to run the project. Every command it writes is verified against the repo, never recalled: an unverified step is written as unknown rather than filled in with something plausible. Read-only on product code — it writes README.md and its own record, nothing else."
argument-hint: "[dev-only | prod-only]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/README.md' '*/README.*.md' '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Write Readme Skill (the handover document)

You write the file a **second person** opens first. Not a marketing page and not a feature list — the
document that answers, in order: *what is this, how do I run it, how do I ship it, and what do I have
to bring myself?*

The test this document has to pass is concrete: **someone who has never seen the repository clones it
and gets the dev environment running from this file alone**, and knows exactly which of the remaining
steps only they can do. Every project in this set eventually needs it — to hand work to a colleague,
to publish somewhere, or simply because the owner will be six months older when they next deploy.

## Scope discipline

- **You verify, you do not recall.** Every command in the README is read out of the repo — the
  `Makefile`, the package manifest's scripts, `verification.md`, the compose file — and, where it is
  cheap and safe, **run** to confirm it exists and starts. A command nobody checked is the single most
  common defect in a README, and it fails on the one person the file exists for.
- **Unknown is written as unknown.** "Deployment: not established in this repository — see
  `production-setup.md`" is a correct line. Inventing a plausible `npm run deploy` is not.
- **Read-only on the product.** You write `README.md` (and, if the project already keeps one, a
  translated sibling like `README.ru.md`) and nothing else. A missing script is a finding, not
  something you write here — file it as a task like anything else.
- **No secrets, ever.** Names of variables, never values; where to get one, never the one in `.env`.
- **This is not the runbook.** `production-runbook.md` (from `setup-production-environment`) is the
  owner's operating manual; the README **points at it**, and carries only what a newcomer needs to get
  as far as a running dev environment plus an honest account of what production takes.

## Language & git

Respond and reason in the user's language, and write the README in **the language the project's
existing docs use** — if the repo has none, ask once; a handover file in the wrong language is worse
than a short one. Code, identifiers, paths and commands are never translated. Workflow vocabulary
follows **`../_shared/glossary.md`**.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open a
worktree on your own initiative. Full rule: **`../_shared/git-workflow.md`**.

## Modes

Read `.dev-skills/release/.release-config.md` (or `.dev-skills/build-plan/.build-config.md` when run
outside the release phase) for `mode`; default **interactive**.

- **interactive** — show the outline and the list of unverified claims before writing; confirm a
  rewrite of an existing README.
- **autopilot** — write it and report what could not be verified.

An argument narrows the job: `dev-only` (skip the production half — nothing is deployed yet),
`prod-only` (refresh just the deployment section).

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
Read, in this order: the current `README.md` (never blow it away — it may hold hand-written prose worth
keeping); `.dev-skills/project-spec/product-requirements.summary.md` for what the product *is* in one
paragraph; `.dev-skills/project-setup/setup-log.md` and **`verification.md`** for the real commands;
`.dev-skills/project-setup/production-setup.md` and `production-runbook.md` if they exist; the root
`CLAUDE.md`; and the repo's own entry points — `Makefile`, package manifest scripts, compose file,
`.env.example`, `.gitignore`.

`.gitignore` matters more than it looks: it tells you **what a clone does not contain**, which is
exactly the part a newcomer trips over.

### Stage 1: The dev path (verified)
Write the sequence a stranger runs: prerequisites (with versions, read from the manifest or the
toolchain files — not from memory), clone, install, configure, bring up, and **how they know it
worked** (the URL, the seeded login, what they should see).

Verify it. Where a step is cheap and non-destructive, **run it** — `make help`, `docker compose
config`, `--version` probes — and where it is not, at minimum confirm the target exists in the file
that would define it. Mark anything you could not check with a visible `⚠ unverified` in your report
(not in the README — the README either states a verified step or says it is unknown).

### Stage 2: The prod path (honest)
Answer one question plainly: **could this person deploy it?** Read `production-setup.md`. Three honest
outcomes, and all three are acceptable:

- **Deployable** — the platform, the command, and what to watch. Point at `production-runbook.md` for
  the detail rather than copying it.
- **Deployable with gaps** — name each gap as a bullet: the account, the secret, the DNS record, the
  migration that has never run anywhere but locally.
- **Not established** — say so in one line and point at `/setup-production-environment`. Do not
  reconstruct a deployment story from the architecture doc: the architecture records a *decision*, and
  the README describes *what exists*.

### Stage 3: What you must bring
The list of things a clone genuinely does not contain and cannot generate: provider accounts, API keys
and where to obtain each, licences, a domain, any data file excluded by `.gitignore`. For each: what
it is, where it goes (the variable name from `.env.example`), and whether the dev environment works
without it (many do, in a degraded mode worth naming).

### Stage 4: The clean state
How to get back to a known-good local state — the reset command, the seed command, what the seed
contains, and **what to do about assets the repository does not carry**. If the project has fixtures,
audio, sample media or a database dump that is gitignored, say how they are produced, or say plainly
that they must be obtained. A newcomer who cannot recreate the fixtures cannot run the tests.

### Stage 5: Write it
Sections, in this order, and skip any that genuinely does not apply:

1. **What this is** — two or three sentences, plain language, from the product summary.
2. **Requirements** — with versions.
3. **Run it locally** — the verified sequence, then "you should see …".
4. **Everyday commands** — the handful that matter (dev, tests, the gate, reset), from `verification.md`.
5. **What you must bring** — Stage 3.
6. **Deploying** — Stage 2, at its honest level.
7. **Getting back to a clean state** — Stage 4.
8. **Where the documentation lives** — the `.dev-skills/` map and the root `CLAUDE.md`, one line each.

Refresh in place: keep the existing structure and hand-written prose where it is still true, correct
what has drifted, and add what is missing. A README rewritten from scratch every release loses the one
paragraph a human wrote by hand.

### Stage 6: Report
Say what changed, list every claim you could **not** verify and why, and end with the
**«What you should do»** block (**`../_shared/build-pipeline/report-format.md`**) — typically: fill in
the accounts only they can create, confirm the deploy story, or run
`/setup-production-environment` if production is still unestablished.

## Rules

1. **Every command is verified against the repo**; anything unverifiable is written as unknown, never
   as a plausible guess.
2. **Never invent a deployment story.** "Not established" is a correct README line.
3. **Never write a secret's value**, and never copy `.env` into the document.
4. **Refresh, don't regenerate** — hand-written prose that is still true survives.
5. **Product code is never touched.** A missing script or broken command is a finding to report, and a
   task if it matters.
6. **The test of the file is a stranger with a fresh clone.** If they would stall at any step, that
   step is not finished.
