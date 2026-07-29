# CLAUDE.md

A collection of **skills and agents for Claude Code** for coding workflows, shipped as a plugin you
can install into any project. Structure informed by [gstack](https://github.com/garrytan/gstack).

> The full pipeline map lives in [`skills/CLAUDE.md`](skills/CLAUDE.md) (loads on demand when you edit
> `skills/`); per-skill detail lives in each `skills/<name>/SKILL.md` and the `_shared/*.md` methods.
> This file holds only what every session needs — don't restate the pipeline detail here.

## Respond in the user's language

Every skill **responds and reasons in the language the user wrote in** — Russian in, Russian out;
English in, English out. Nothing to configure; detect it from the message.

- Natural-language text only — never translate code, identifiers, paths, commands, or API names.
- A skill tells every subagent it spawns the same rule, so the whole flow stays consistent.
- **Exception:** git commit messages are ALWAYS written in English.
- **Which words to translate is fixed by [`skills/_shared/glossary.md`](skills/_shared/glossary.md)**,
  not by taste: the workflow vocabulary is translated (`findings` → замечания, `gate` → контрольная
  точка), a short list stays in Latin script and uninflected (`fork`, `commit`, `backlog`, `mockup`,
  `deploy`, `checklist`, `baseline`, `harness`, `onboarding`, `sanity check`), hybrid verbs are never
  built, and templates' structural anchors (section headings, task fields, config keys) stay verbatim.
  Every skill's `## Language` section points at it; the agents carry a compact inline copy.

## Repository layout

This repo is **both the marketplace and the plugin it ships** — the plugin is collapsed into the repo
root, so the marketplace `source` is `"./"`.

```
.claude-plugin/marketplace.json   # marketplace catalog (lists the plugin; source: "./")
.claude-plugin/plugin.json        # the plugin manifest (carries the version)
skills/<name>/SKILL.md            # one dir per skill (+ references/*.md, load on demand)
skills/_shared/*/*.md             # shared methodology, no SKILL.md (spec/build/release pipelines + agent-guide.md, glossary.md, git-workflow.md)
agents/*.md                       # named subagent roles (auto-discovered — no plugin.json entry)
scripts/*.sh                      # hook helpers (e.g. guard-write-scope.sh)
```

- Component dirs (`skills/`, `agents/`) sit at the **plugin root**, not inside `.claude-plugin/`.
- Marketplace `source` must start with `./`; a bare `"."` is invalid.
- **Validate any change with `claude plugin validate .`** (test locally via `/plugin marketplace add ./`).

## Versioning — never auto-bump

The plugin's `version` (`.claude-plugin/plugin.json`, semver) is **owned by the user**. The agent MUST
NOT edit it on its own initiative — only when the user explicitly asks. Consumers receive changes via
`/plugin update` only once it's bumped, but the agent never drives the bump (may mention skills changed,
nothing more). Keep `metadata.version` in `marketplace.json` in sync when the user does bump.

## The pipelines (overview)

Three sequential pipelines, each conducted by a thin **orchestrator** that sequences focused sub-skills
(it conducts, it does not duplicate), plus one manually-invoked production step that no orchestrator
runs for you. See [`skills/CLAUDE.md`](skills/CLAUDE.md) for the full map.

- **Spec** (`create-project-spec`) — raw idea → buildable spec. Writes docs only. Each phase runs the
  same machine: *elicit → research (cite sources) → draft → adversarial review → merge → research doc +
  human summary*. When the repo already has code, each phase reads it and confirms rather than re-asks.
- **Build** (`build-tasks`) — spec → working software. **Mutates the repo.** Sequential: one task at a
  time, single working tree, no parallelism. Implement ↔ an independent verifier that authors adversarial
  tests, behind an enforced quality gate (`make check` + hooks).
- **Release** (`release-product`) — built product → cut release. Two halves: `refactor` then
  `write-tests` **change the repo, sequentially and alone**; then the read-only audits **fan out in
  parallel** and `manual-test` briefs the human. Findings are filed as rework (never fixed in place),
  one fix round, one re-audit, then `cut-release` (gated, stops before production).
- **Production** (`setup-production-environment`) — a fourth, manually-invoked step, never auto-run:
  everything production-related in one place (platform, database and migrations, config and secrets,
  spend caps, analytics and error tracking), sorted into **repo · authorized CLI with a yes · human in
  a dashboard**, ending in a live deploy, a smoke test, and a plain-language runbook. Its existence is
  what lets the audits stay pure audits: **an audit never installs or configures anything.**

Skills are **verbs**; their outputs are **nouns**. All artifacts are committed project documentation
under `.dev-skills/` (`project-spec/`, `build-plan/`, `project-setup/`, `release/`) plus the root `DESIGN.md`
(UI projects). `.dev-skills/build-plan/mockups/` is the only gitignored item.

## Skill & agent authoring conventions

- **Description = discoverability.** Write the `description` in the third person stating WHAT the skill
  does and WHEN to use it. Claude selects skills from this field — no literal "trigger phrases".
- **Progressive disclosure.** Thin body (~1,500–2,000 words) + a copyable checklist; long
  templates/rubrics go in `references/`. Shared methodology lives in `_shared/` — read it for the *how*,
  don't restate it.
- **Persona + anti-sycophancy.** Validation/review/audit skills adopt a critical persona, take a
  position, and name failure patterns instead of hedging.
- **Named agents** (`agents/`, auto-discovered) carry the pipelines' subagent roles: `spec-reviewer` and
  `spec-researcher` are self-contained (a plugin agent can't reliably read `_shared/*.md` at runtime);
  `implementer`/`verifier`/`ui-prototyper` are thin wrappers that `skills:`-preload their procedure skill.
- **`disable-model-invocation: true`** on side-effecting / outward-facing entry points so they don't
  auto-fire from a cold chat: `commit`, `build-tasks`, `run-task`, `setup-dev-environment`,
  `setup-production-environment`, `refactor`, `cut-release`, `release-product`. Not set on the doc-only
  spec phases, the read-only `audit-*` and `manual-test`, `write-tests`, the build-loop skills, or
  `generate-mockups`.
- **Write-scope guard hooks** (declared in a skill's frontmatter, running `scripts/guard-write-scope.sh`)
  turn a prose invariant into a harness guarantee: `verify-feature` and `write-tests` write tests +
  `.dev-skills/` only; `generate-mockups` the scratch mockups tree only; each `audit-*` `.dev-skills/**`
  + the backlog only; `manual-test` `.dev-skills/**` only.
  **`allowed-tools` is deliberately unused** — we keep the user's permission prompts intact.

## Authoring language

**Write all skill content, this file, and all repository documentation in English.** Responding in the
user's language is runtime behavior, not the language the skills are authored in. Commit messages: English.

## Git workflow

- **Never create a feature branch unless explicitly asked.** Work on the current branch by default.
- The same rule is **shipped inside the skills**, not just applied to this repo: every skill and every
  git-capable agent carries a `## Git workflow` section — one branch, the current one (normally
  `main`), no branch / switch / worktree on the skill's own initiative, the user's explicit request in
  this session being the single exception. The full text lives in
  [`skills/_shared/git-workflow.md`](skills/_shared/git-workflow.md); the per-skill sections are
  compact copies that point at it, so keep them in sync when the rule changes.
- The `.githooks/commit-msg` hook blocks AI-attribution trailers (`Co-Authored-By: Claude`, etc.);
  enable once per clone with `git config core.hooksPath .githooks`. Do not add such trailers.
