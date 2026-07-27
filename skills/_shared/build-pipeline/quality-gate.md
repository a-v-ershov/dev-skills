# Quality gate (shared — build pipeline)

The **quality gate** is the fast, deterministic feedback loop the build pipeline runs on every task:
linter + formatter + type-checker + test-runner, behind **one command**, that **blocks the commit**
when it is red. It is the cheap layer that catches the obvious in seconds — before the expensive,
adversarial `verify-feature` drive/prove runs — and the **accumulating test suite is the regression
net** that keeps a later task from silently breaking an earlier one.

This doc defines the gate once. `setup-dev-environment` builds it; `implement-feature`, `verify-feature`
and `build-tasks` enforce it. They reference this file rather than restating the rule.

## What the gate runs

One command (`make check` or the stack's equivalent — recorded in `.dev-skills/project-setup/verification.md`)
that runs, fast and deterministically:

- **Format** — the formatter in check mode (e.g. `ruff format --check`, `prettier --check`).
- **Lint** — the linter (e.g. Ruff, ESLint).
- **Type-check** — the type-checker in strict mode (e.g. `mypy --strict`, `tsc --noEmit`).
- **Test** — the test-runner over the accumulated suite (e.g. `pytest`, `vitest`). Run the tests
  relevant to the change for speed, then the **whole suite** before the commit (the regression pass).

The concrete tools come from the stack `design-architecture`/`design-dev-architecture` already chose —
the gate **executes** that decision, it does not re-pick tools.

## Zero-tolerance config

The gate is only effective for AI-written code if it cannot be silently sidestepped:

- **Fail on suppressions.** A new `eslint-disable` / `# type: ignore` / `# noqa` in a diff fails the
  gate; silencing a rule requires a deliberate, human-authored override, never a drive-by comment.
- **Fail on new warnings**, not only errors. Strict type-checking on (`--strict`) — it catches the
  implicit-any / untyped-dict patterns agents default to when unsure of a contract.

## Where it is configured vs enforced

- **Configured by `setup-dev-environment`** (repo-local, so auto-applicable): the tool configs, the
  `make check` target, a **pre-commit hook** that runs the gate and blocks the commit on red, and a
  Claude Code **Stop / PostToolUse hook** in `.claude/settings.json` that runs the gate after edits and
  feeds the failures back to the agent.
- **Enforced at three points:**
  1. `implement-feature` self-check — runs the gate before handing off; does not hand off on red.
  2. `verify-feature` — its authored tests become part of the suite the gate runs.
  3. `build-tasks` — the **full gate must be green before the checkpoint commit**; a red gate routes
     the task back to `implement-feature` (counts as a round), it is never committed red. The
     pre-commit hook is the belt-and-suspenders backstop.

## Make failures actionable

When the gate fails, the message must carry the specific finding, file, line, and a one-line remedy —
a coding agent loops back on a structured failure message and fixes most issues without a human. The
throughput failure mode is not "the gate is too strict", it is "the gate's messages are not actionable".

## Greenfield caution

On a fresh project, zero-tolerance from day one is correct, but introduce strictness **deliberately for
the chosen stack** and keep the messages actionable — otherwise the implement↔verify loop stalls on a
churn of style fixes instead of converging on behavior.
