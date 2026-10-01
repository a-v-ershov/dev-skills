# CLAUDE.md

**Skills and agents for Claude Code** coding workflows, shipped as a plugin. Structure informed by
[gstack](https://github.com/garrytan/gstack).

> The pipeline map is [`skills/CLAUDE.md`](skills/CLAUDE.md) (loads on demand when you edit `skills/`);
> per-skill detail is each `skills/<name>/SKILL.md` and the `_shared/*.md` methods. Don't restate it here.

## Respond in the user's language

Every skill **responds and reasons in the language the user wrote in** — detected from the message,
nothing to configure. Natural-language text only: never translate code, identifiers, paths, commands
or API names. Skills pass the rule to every subagent they spawn. **Git commit messages are always
English.** Which words are translated is fixed by
[`skills/_shared/glossary.md`](skills/_shared/glossary.md): workflow vocabulary is translated, a short
list stays Latin and uninflected, hybrid verbs are never built, template anchors (section headings,
task fields, config keys) stay verbatim. Every skill's `## Language & git` section points at it; the
agents carry an inline copy.

## Repository layout

This repo is **both the marketplace and the plugin it ships** — the plugin is collapsed into the repo
root, so the marketplace `source` is `"./"`.

```
.claude-plugin/marketplace.json   # marketplace catalog (lists the plugin; source: "./")
.claude-plugin/plugin.json        # the plugin manifest (carries the version)
skills/<name>/SKILL.md            # one dir per skill (+ references/*.md on demand; helper scripts alongside)
skills/_shared/*/*.md             # shared methodology, no SKILL.md (spec/build/release pipelines + agent-guide.md, glossary.md, git-workflow.md)
agents/*.md                       # named subagent roles (auto-discovered)
scripts/*.sh                      # guard-write-scope.sh (hook) · check-skill-size.sh (budget)
```

- `skills/` and `agents/` sit at the plugin root, not inside `.claude-plugin/`.
- Marketplace `source` must start with `./`; a bare `"."` is invalid.
- **Validate any change with `claude plugin validate .`** (test locally via `/plugin marketplace add ./`).

## Versioning — never auto-bump

`version` in `.claude-plugin/plugin.json` is **owned by the user**: never edit it unless explicitly
asked (you may mention that skills changed; consumers see changes via `/plugin update` only after a
bump). `metadata.version` in `marketplace.json` is the marketplace's own number — leave it alone.

## The pipelines (overview)

Three pipelines, each conducted by a thin **orchestrator** that sequences sub-skills (conducts, never
duplicates), plus one manual production step. Full map: [`skills/CLAUDE.md`](skills/CLAUDE.md).

- **Spec** (`create-project-spec`) — idea → buildable spec; writes docs only. Each phase: *elicit →
  research (cited) → draft → adversarial review → merge → research doc + human summary*. With existing
  code, each phase reads it and confirms instead of re-asking.
- **Build** (`build-tasks`) — spec → software; **mutates the repo**. Sequential, one task at a time,
  single working tree. Implementer ↔ independent verifier behind an enforced gate (`make check-fast` +
  `make test-scoped` + hooks) — **only the task's own tests**, never the whole suite.
- **Release** (`release-product`) — product → cut release. `refactor` then `write-tests` change the
  repo sequentially and alone; then the read-only audits fan out in parallel (`simplify-product` rides
  along with never-blocking proposals) and `manual-test` briefs the human. **The whole suite
  (`make check`) runs here.** Findings become coarse rework tasks, one fix round, one re-audit, then
  `cut-release` (gated, stops before production).
- **Production** (`setup-production-environment`) — manual, never auto-run: platform, database,
  config, spend caps, analytics, sorted into **repo · authorized CLI with a yes · human in a
  dashboard**, ending in a live deploy, smoke test and runbook. **An audit never installs or
  configures anything** — this step exists so they don't have to.

Skills are **verbs**, outputs are **nouns**. Artifacts are committed under `.dev-skills/`
(`project-spec/`, `build-plan/`, `project-setup/`, `optimize/`, `release/`) plus the root `DESIGN.md`
(UI projects); only `.dev-skills/build-plan/mockups/` is gitignored.

**`audit-skills`** is the set's own retrospective (manual): by default it reads every recorded
session that ran the plugin (`scan_session.py`; or one session, or a window) and the artifacts,
proposes numbered edits to the skill / agent / `_shared` files that ran, and applies nothing until
the user picks numbers. `release-product` never invokes it.

## Skill & agent authoring conventions

- **Description = discoverability, never free.** Third person, WHAT it does and WHEN to use it, no
  literal trigger phrases. It is loaded in **every** session, so it is capped at **700 characters**
  (aim far lower).
- **Progressive disclosure, enforced.** Thin body + a copyable checklist; catalogues, templates and
  rubrics go in `references/`; methodology lives in `_shared/` — point at it, don't restate it.
  **Body ≤ 15,000 characters**, checked by `scripts/check-skill-size.sh` (run after any edit): after a
  `/compact` the harness re-injects a loaded skill's body clipped at ~20,000 characters, silently,
  mid-sentence — `## Rules` is what gets lost. `references/` is read on demand and never clipped.
- **Persona + anti-sycophancy.** Validation/review/audit skills take a position and name failure
  patterns instead of hedging.
- **Named agents** (`agents/`) carry the subagent roles: `spec-reviewer` and `spec-researcher` are
  self-contained (a plugin agent can't reliably read `_shared/*.md` at runtime);
  `implementer`/`verifier`/`ui-prototyper`/`refactorer`/`test-writer` are thin wrappers that
  `skills:`-preload their procedure skill. `release-product` spawns `refactor` and `write-tests` as
  agents (the refactorer twice, around the human's plan approval) for context isolation.
- **`disable-model-invocation: true`** only where an auto-fire would reach **outside the repository**:
  `setup-production-environment`. A skill another skill invokes via the Skill tool **cannot** carry it
  (`run-task` → `commit`, `setup-dev-environment`; `build-tasks` → `run-task`; `release-product` →
  `build-tasks`, `cut-release`) — so `cut-release` has none; its always-confirm gate and the user's
  permission prompts guard the cut.
- **Write-scope guard hooks** (frontmatter → `scripts/guard-write-scope.sh`) make a prose invariant a
  harness guarantee: `verify-feature` writes tests + `.dev-skills/` only; `generate-mockups` the
  mockups tree only; each release `audit-*`, `simplify-product`, `manual-test`, `groom-backlog`
  `.dev-skills/**` (+ the backlog) only; `audit-skills` skill / agent / command / `CLAUDE.md` files
  only; `write-readme` `README*.md` + `.dev-skills/**` only. Exceptions: `audit-tests` may also edit
  the **run entry points** (`Makefile`/`justfile`, `package.json` scripts, `pyproject.toml`, CI) — tier
  splitting is its job; test-authoring roles may also edit the **test harness config**
  (`playwright.config.*`, `vitest`/`jest`, `pytest.ini`, `conftest.py`, `tsconfig*.json`, eslint, `e2e/`);
  `write-tests` carries **no hook** because its red-first proof must briefly break product code — the
  invariant there is prose (one minimal break, reverted, the revert proven with `git diff`).
  **`allowed-tools` is deliberately unused** — the user's permission prompts stay intact.

## Authoring language

All skill content, this file and repository documentation are **written in English**; responding in
the user's language is runtime behaviour. Commit messages: English.

## Git workflow

- **Never create a feature branch unless explicitly asked** — work on the current branch.
- The same rule ships inside the skills: every skill and git-capable agent carries a compact
  `## Language & git` / `## Git workflow` copy pointing at
  [`skills/_shared/git-workflow.md`](skills/_shared/git-workflow.md); keep them in sync.
- The `.githooks/commit-msg` hook blocks AI-attribution trailers (`Co-Authored-By: Claude`, etc.);
  enable once per clone with `git config core.hooksPath .githooks`. Do not add them.
