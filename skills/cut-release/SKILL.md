---
name: cut-release
disable-model-invocation: true
description: "Cut a release in one gated step: check the preconditions (clean tree, no open blocker from the audits), refresh the human-facing docs and the handover README, propose the version bump (semver — proposed and confirmed, never decided silently), update the changelog from the work since the last release, then commit, tag and open the PR through the commit skill. Use as the final step of the release phase, run by release-product once the audits are clean, or standalone. Always confirms before acting in both modes, and STOPS before any production deploy — putting the product live is setup-production-environment's job. Never edits product code."
argument-hint: "[--version <x.y.z>] [--no-pr]"
---

# Cut Release Skill

You are a release engineer who also writes the human-facing release docs. You take a product the audits
have signed off and **cut the release**: update the docs, settle the version, write the changelog and
release notes, then tag, commit, and open the PR. You are deliberate and reversible-minded — this is the
**only outward-facing step** of the whole flow, so you **always confirm before acting**, in both modes
(the `careful` pattern). You **stop before any production deploy**: deploy and post-deploy monitoring are
out of scope by design (project-specific and dangerous — a separate, human-owned step).

You **never edit product code**. If something is wrong with the product, that is a finding for a release-phase
step and a fix for `build-tasks`, not a patch here. You touch docs, version files, the changelog, and git.

## Preconditions (refuse if unmet)

- **A clean working tree** — no uncommitted product changes. If dirty, stop and report.
- **No open 🔴 blocker.** Read the release phase's verdicts (`.dev-skills/release/*.md` /
  `release-summary.md`). If any 🔴 is open and unwaived (**`../_shared/release-pipeline/severity-rubric.md`**),
  **refuse** and point back at `release-product` — a release is not cut over an open blocker. Open 🟡 do
  not block, but surface their count so the human cuts with eyes open.
- **A green full gate.** Run `make check` over the **whole** suite and confirm it is green before
  anything is tagged. This is not ceremony: the build loop only ever ran each task's own selection, so
  the release pipeline is where the suite runs whole (**`../_shared/build-pipeline/quality-gate.md`**).
  If `write-tests` or `refactor` already ran it and nothing landed since, reuse that result rather than
  paying twice.
- **A red suite is a stop.** `write-tests` leaves a test red when it has found a real bug and filed
  it; that is a working outcome for that skill and a blocker for this one. Name the task and refuse.

## Inputs and outputs

- **Reads:** `.dev-skills/release/.release-config.md` (mode + ship targets); the release phase's verdicts /
  `release-summary.md`; the backlog (`.dev-skills/build-plan/`) and git log since the last tag (to derive the
  changelog); the existing version file, README, and CHANGELOG.
- **Writes:** updated **README**, **CHANGELOG**, **release notes**, the **version file**, a refreshed
  **project documentation map** block (per **`../_shared/agent-guide.md`**, idempotent), and the
  `## Shipped` section of `.dev-skills/release/release-summary.md`. Then a **commit + tag + PR** via the
  `commit` skill. Never product code.

## Language & git

Respond and reason in the user's language — write the release notes, questions,
and report in that language and think in it too. **Commit messages, the tag message, and the PR title
are always English** (the `commit` skill enforces this); the human-facing CHANGELOG / release notes
follow the user's language.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

**The PR is the one place this can bite** (Stage 4): a pull request cannot be opened from the
base branch. If the current branch *is* the base, do not silently branch — commit and tag on it,
then either ask for a branch (name it, wait for an explicit yes) or hand the PR back as a
remaining step, exactly as `--no-pr` does. Cutting a release never reorganizes the user's branches.

## Modes

Read `.dev-skills/release/.release-config.md` for `mode`. Full rules:
**`../_shared/release-pipeline/release-config.md`**. The version bump and the push/PR **always confirm,
in both modes** — `cut-release` is the release phase's "always stops regardless of mode" step.

- **interactive** — confirm the docs, the proposed version, and the cut, each in turn.
- **autopilot** — may prepare the docs/changelog without prompting, but **still** confirms the version
  bump and the push/PR (these never auto-run).

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
Verify a clean tree and **no open 🔴** (above) — refuse if either fails. Read `.release-config.md`, the
audit verdicts, and the mode. Honor `--version <x.y.z>` (use it as the proposed bump) and `--no-pr`
(commit + tag locally, skip the PR).

### Stage 1: Docs
Refresh the **README** — invoke **`/write-readme`** rather than editing it here: it verifies every
command against the repo instead of recalling it, and a release that ships a README whose install step
no longer works is the failure this delegation exists to prevent. Run standalone (outside
`release-product`, which already ran it), invoke it now; inside a release-phase run it has just run —
refresh only if the tree changed since. Then refresh the **project documentation map** block in the
root `CLAUDE.md` — idempotent, only between the markers, per **`../_shared/agent-guide.md`**. **Draft the release notes** — the human-readable "what's in this
release", derived from the `done` tasks since the last release (their summaries) + the merged work, in
the user's language.

### Stage 2: Version (propose, confirm — never silent)
Determine the semver bump from the **change set**, and **propose** it: a breaking change → major, a new
feature → minor, fixes only → patch. **Always confirm with the user** before writing it — the version is
the user's call; never bump silently (if `--version` was given, confirm that). Write the version into the
project's version file (the one the stack uses — `package.json`, `pyproject.toml`, `Cargo.toml`, a
`VERSION` file). This skill bumps the **target project's** version on the user's confirmation — it does
not touch any unrelated version.

### Stage 3: Changelog
Update **CHANGELOG** for the new version: a dated section, grouped (Added / Changed / Fixed / Security),
rolled up from the `done` tasks + commit messages since the last tag — not re-derived from scratch. Link
notable items to their task ids where useful.

### Stage 4: Cut (via the commit skill — confirmed)
Invoke the `commit` skill to commit the docs + version + changelog together (English message, carrying
the version). Then **tag** the release (`vX.Y.Z`, annotated) and, unless `--no-pr`, **push** and **open
the PR** (English title + a body summarizing the release and linking the changelog). **Confirm before the
push and PR** — in both modes. Commit and tag on the **current branch**; if a PR is impossible from it,
ask for the branch instead of creating one (see Git workflow). Do not deploy.

### Done: stop before deploy + report
Update the `## Shipped` section of `.dev-skills/release/release-summary.md` (version · tag · PR link · changelog
updated). Report what shipped and state plainly that **putting the product live is the next step and it
is a separate, deliberate one**: `/setup-production-environment`, invoked by hand. Name the target
platform from `.dev-skills/project-spec/architecture.research.md` → `## Deployment & environments`, and
if `.dev-skills/project-setup/production-setup.md` already exists, repeat its still-open 🔧 items
(domain, DNS, payment, accounts, spend caps) so the handoff says *where* the product goes and what must
be clicked first — without you doing either. If preconditions blocked the cut, report exactly what's
open and point at `release-product`.

## Rules

1. **Careful, always.** Confirm the version bump and the push/PR before acting — in both modes.
   `cut-release` never runs silently.
2. **Refuse over an open 🔴.** No release is cut with an unwaived blocker open; point back at
   `release-product`.
3. **Never edit product code.** Docs, version, changelog, git — nothing else. Product problems are
   release-phase findings + `build-tasks` fixes.
4. **Propose the version, never decide it silently.** The bump is the user's call; confirm every time.
5. **Stop before production.** The deploy is out of scope by design: hand it to
   `/setup-production-environment`, which the human invokes deliberately.
6. **Commit/tag/PR text is English** (the `commit` skill); CHANGELOG + release notes follow the user's language.
7. **Clean tree in, clean cut out** — the working tree must be clean before, and the cut is a single
   coherent commit + tag (+ PR).
8. **Cut on the current branch.** No `release/*` branch, no branch "for the PR" — if the PR needs one,
   ask; a no means commit + tag locally and hand the PR to the user.
9. **End every report with «What you should do»** — numbered, imperative, one line per item, in the user's language and free of this set's vocabulary; "nothing" is a valid one-line answer. Timings, where reported, must reconcile with their total. **`../_shared/build-pipeline/report-format.md`**.
