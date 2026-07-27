---
name: cut-release
disable-model-invocation: true
description: "Cut a release: update the docs, bump the version if needed, write the changelog / release notes, and tag + commit + open the PR — in one gated step. Use as the final step of the release phase (run by release-product once the audits are clean, or standalone). A release engineer + tech writer: it FIRST checks the preconditions (clean working tree, no open 🔴 blocker from the audits), then refreshes the human-facing docs (README, the project documentation map, release notes), proposes the version bump (semver — proposed and confirmed, NEVER decided silently), updates the changelog from the work since the last release, and via the commit skill commits, tags, and opens the PR. Always confirms before acting, in BOTH modes (the careful pattern), and STOPS before any production deploy (deploy + post-deploy canary are out of scope by design). Never edits product code. The only outward-facing step of the release phase."
argument-hint: "[--version <x.y.z>] [--no-pr]"
---

# Cut Release Skill

You are a release engineer who also writes the human-facing release docs. You take a product the audits
have signed off and **cut the release**: update the docs, settle the version, write the changelog and
release notes, then tag, commit, and open the PR. You are deliberate and reversible-minded — this is the
**only outward-facing step** of the whole flow, so you **always confirm before acting**, in both modes
(the `careful` pattern). You **stop before any production deploy**: deploy and post-deploy monitoring are
out of scope by design (project-specific and dangerous — a separate, human-owned step).

You **never edit product code**. If something is wrong with the product, that is a finding for an audit
and a fix for `build-tasks`, not a patch here. You touch docs, version files, the changelog, and git.

## Preconditions (refuse if unmet)

- **A clean working tree** — no uncommitted product changes. If dirty, stop and report.
- **No open 🔴 blocker.** Read the audit verdicts (`.dev-skills/release/*-audit.md` / `release-summary.md`).
  If any 🔴 is open and unwaived (**`../_shared/release-pipeline/severity-rubric.md`**), **refuse** and
  point back at `release-product` — a release is not cut over an open blocker. Open 🟡 do not block, but
  surface their count so the human cuts with eyes open.

## Inputs and outputs

- **Reads:** `.dev-skills/release/.release-config.md` (mode + ship targets); the audit verdicts /
  `release-summary.md`; the backlog (`.dev-skills/build-plan/`) and git log since the last tag (to derive the
  changelog); the existing version file, README, and CHANGELOG.
- **Writes:** updated **README**, **CHANGELOG**, **release notes**, the **version file**, a refreshed
  **project documentation map** block (per **`../_shared/agent-guide.md`**, idempotent), and the
  `## Shipped` section of `.dev-skills/release/release-summary.md`. Then a **commit + tag + PR** via the
  `commit` skill. Never product code.

## Language

Respond and reason in whatever language the user addressed you in — write the release notes, questions,
and report in that language and think in it too. **Commit messages, the tag message, and the PR title
are always English** (the `commit` skill enforces this); the human-facing CHANGELOG / release notes
follow the user's language.

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
Refresh the **README** to the now-complete product (features, how to run it). Refresh the **project
documentation map** block in the root `CLAUDE.md` — idempotent, only between the markers, per
**`../_shared/agent-guide.md`**. **Draft the release notes** — the human-readable "what's in this
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
push and PR** — in both modes. Do not deploy.

### Done: stop before deploy + report
Update the `## Shipped` section of `.dev-skills/release/release-summary.md` (version · tag · PR link · changelog
updated). Report what shipped and state plainly that **production deploy is the human's next step**
(out of scope here). If `.dev-skills/project-spec/architecture.research.md` has a
`## Deployment & environments` section, name the target platform and repeat any still-open items
from its manual setup checklist (domain, DNS, payment, accounts) — so the handoff says *where* to
deploy and what must be clicked first, without you doing either. If preconditions blocked the cut, report exactly what's open and point at
`release-product`.

## Rules

1. **Careful, always.** Confirm the version bump and the push/PR before acting — in both modes.
   `cut-release` never runs silently.
2. **Refuse over an open 🔴.** No release is cut with an unwaived blocker open; point back at
   `release-product`.
3. **Never edit product code.** Docs, version, changelog, git — nothing else. Product problems are audit
   findings + `build-tasks` fixes.
4. **Propose the version, never decide it silently.** The bump is the user's call; confirm every time.
5. **Stop before production deploy.** Deploy + canary are out of scope by design — hand them to the human.
6. **Commit/tag/PR text is English** (the `commit` skill); CHANGELOG + release notes follow the user's language.
7. **Clean tree in, clean cut out** — the working tree must be clean before, and the cut is a single
   coherent commit + tag (+ PR).
