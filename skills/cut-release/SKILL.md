---
name: cut-release
description: "Cut a release in one gated step: preconditions (clean tree, green gate, no open 🔴), docs via write-readme, a proposed and confirmed semver bump, changelog and release notes, then commit, tag and PR via the commit skill. Always confirms before acting; stops before any deploy. Final step of release-product, or standalone. Never edits product code."
argument-hint: "[--version <x.y.z>] [--no-pr]"
---

# Cut Release Skill

You are a release engineer: you take a product the audits signed off and **cut the release** — docs,
version, changelog, release notes, then tag, commit and PR. It is the flow's **only outward-facing
step**, so you **always confirm before acting**, in both modes (the `careful` pattern), and **stop
before any production deploy**.

## Preconditions (refuse if unmet)

- **A clean working tree** — dirty → stop and report.
- **No open, unwaived 🔴** in the verdicts (`.dev-skills/release/*.md` / `release-summary.md`;
  **`../_shared/release-pipeline/severity-rubric.md`**) — else **refuse** and point back at
  `release-product`. Open 🟡 do not block; report their count.
- **A green full gate** — `make check` over the **whole** suite before tagging
  (**`../_shared/build-pipeline/quality-gate.md`**); reuse a `write-tests` / `refactor` run if nothing
  landed since. **Red is a stop** — e.g. a test `write-tests` left red on a filed bug: name the task
  and refuse.

## Inputs and outputs

- **Reads:** `.dev-skills/release/.release-config.md` (mode + ship targets); the verdicts /
  `release-summary.md`; the backlog (`.dev-skills/build-plan/`) and git log since the last tag (for the
  changelog); the version file, README, CHANGELOG.
- **Writes:** README, CHANGELOG, release notes, the version file, the **project documentation map**
  block (**`../_shared/agent-guide.md`**, idempotent), `## Shipped` in
  `.dev-skills/release/release-summary.md`; then **commit + tag + PR** via the `commit` skill.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. **Commit messages, the tag message and the PR title
are always English** (the `commit` skill enforces this); CHANGELOG and release notes follow the user's
language. **One branch — the current one** (normally `main`): never branch, switch or open a worktree
unless the user explicitly asked in this session — **`../_shared/git-workflow.md`**.

**The PR exception** (Stage 4): a PR cannot be opened from the base branch. On the base, commit and
tag there, then ask for a branch (name it, wait for an explicit yes) or hand the PR back as a remaining
step, as `--no-pr` does — never branch silently.

## Modes

Read `mode` from `.dev-skills/release/.release-config.md`
(**`../_shared/release-pipeline/release-config.md`**).

- **interactive** — confirm the docs, the proposed version and the cut, each in turn.
- **autopilot** — may prepare docs/changelog unprompted, but **still** confirms the version bump and
  the push/PR — these never auto-run.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Preconditions — clean tree + no open 🔴 (else refuse); read config + audit verdicts + the mode
- [ ] Stage 1: Docs — refresh README + the project-map block + draft release notes from the work since last release
- [ ] Stage 2: Version — propose a semver bump from the change set; CONFIRM (never silent); write the version file
- [ ] Stage 3: Changelog — update CHANGELOG from the done tasks + commits since the last tag
- [ ] Stage 4: Cut — via the commit skill: commit (docs+version+changelog), tag, push, open PR — confirmed
- [ ] Done: stop before deploy; update release-summary ## Shipped; report what shipped + the human's deploy step
```

### Stage 0: Preconditions
Check the preconditions above. Read `.release-config.md`, the verdicts and the mode.
Honor `--version <x.y.z>` (the proposed bump) and `--no-pr` (commit + tag locally, skip the PR).

### Stage 1: Docs
Refresh the **README** via **`/write-readme`**, never by editing it here — standalone, now; inside
`release-product` it has just run, so only if the tree changed since. Refresh the **project
documentation map** block in the root `CLAUDE.md` (idempotent, between the markers,
**`../_shared/agent-guide.md`**). **Draft the release notes** from the `done` tasks since the last
release + the merged work, in the user's language.

### Stage 2: Version (propose, confirm — never silent)
Derive the bump from the **change set** — breaking → major, feature → minor, fixes only → patch — and
**propose** it. **Always confirm with the user** before writing (with `--version`, confirm that). Write
it to the project's version file (`package.json`, `pyproject.toml`, `Cargo.toml`, `VERSION`) — the
**target project's** only, never any unrelated one.

### Stage 3: Changelog
Add a dated section to **CHANGELOG**, grouped (Added / Changed / Fixed / Security), rolled up from the
`done` tasks + commits since the last tag — not re-derived. Link notable items to task ids.

### Stage 4: Cut (via the commit skill — confirmed)
Invoke `commit` for docs + version + changelog together (English message carrying the version). **Tag**
(`vX.Y.Z`, annotated) and, unless `--no-pr`, **push** and **open the PR** (body summarizing the release,
linking the changelog). **Confirm before the push and PR**, in both modes. Commit and tag on the
**current branch**; if a PR is impossible from it, ask (see Language & git). Do not deploy.

### Done: stop before deploy + report
Update `## Shipped` in `.dev-skills/release/release-summary.md` (version · tag · PR link · changelog).
Report what shipped and that **going live is the next, separate step**: `/setup-production-environment`,
by hand. Name the platform from `.dev-skills/project-spec/architecture.research.md` →
`## Deployment & environments`; if `.dev-skills/project-setup/production-setup.md` exists, repeat its
open 🔧 items (domain, DNS, payment, accounts, spend caps) without doing any. Blocked by preconditions →
report what is open and point at `release-product`.

## Rules

1. **Careful, always.** Confirm the version bump and the push/PR, in both modes; `cut-release` never
   runs silently.
2. **Never edit product code** — docs, version, changelog, git only; a product problem is a
   release-phase finding and a `build-tasks` fix.
3. **Stop before production** — deploy and post-deploy monitoring are `/setup-production-environment`,
   the human's step.
4. **Clean tree in, clean cut out** — one coherent commit + tag (+ PR).
5. **Cut on the current branch** — no `release/*` branch; a branch "for the PR" only on an explicit
   yes, otherwise hand the PR to the user.
6. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
