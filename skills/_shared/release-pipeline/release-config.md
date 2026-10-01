# Release config & modes (shared — release pipeline)

`release-product` sets these once; each release skill (`refactor`, `write-tests`, `audit-*`,
`simplify-product`, `manual-test`, `cut-release`) reads them and falls back gracefully when run
standalone with no config.

## The settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: stop at each hard gate — a 🔴 blocker, before filing rework, and before the
    outward-facing `cut-release` — for the human.
  - `autopilot`: resolve ordinary forks itself and **log each** (in the step's findings doc), running
    the chain back-to-back — **except** the three things that always stop (below).
- **`steps`** — which steps are enabled. Default: all applicable, in this fixed order: `refactor` →
  `write-tests` → (`audit-security` · `audit-performance` · `audit-product` · `audit-dependencies` ·
  `simplify-product`, in parallel) → `manual-test`. A step that does not apply self-skips and records
  why (e.g. the accessibility part of `audit-product` with no UI, `audit-performance` with no
  measurable scenario, `audit-dependencies` with no dependency manifest).

There is **no iteration setting.** One fix round, one re-run of the affected audits; whatever is still
open is `needs_human` (`audit-method.md` → "One round, then a decision").

## Config file — `.dev-skills/release/.release-config.md`

```
# Release pipeline config

- mode: interactive            # interactive | autopilot
- steps: refactor, write-tests, security, performance, product, dependencies, simplify, manual-test
```

## How a release skill uses it

1. At intake, read `.dev-skills/release/.release-config.md`.
2. **Present:** use `mode` and the enabled `steps`.
3. **Absent (standalone run):** ask once (one `AskUserQuestion`, defaults pre-selected: interactive +
   all applicable steps), then write the file so later standalone skills inherit it.

`.dev-skills/release/` is committed project documentation — no gitignore, no transient files (every
findings doc is kept as the audit trail).

## Three things ALWAYS stop, regardless of mode

1. **`refactor`'s plan.** It rewrites working code; the human approves the transformation list before
   any of it is applied.
2. **A finding still open after the single fix round** — a `needs_human` escalation: the release
   cannot be cut.
3. **`cut-release` itself** — the outward-facing step (version bump, tag, push, PR) always confirms
   before acting, in both modes (the `careful` pattern); the release analog of the build phase's
   "critical / destructive change propagation always stops".

Going live is not on this list: it is not part of the release run. `setup-production-environment`
is invoked by hand and confirms every external action itself.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged in the step's findings doc with
  choice, rationale and confidence.
- **Still do the work.** Autopilot skips human prompts — **not** the separate-agent audits, the
  evidence standard, red-first in `write-tests`, or the re-run after a fix.
- **Audits are never self-approved.** Each audit runs in a fresh, independent agent and proves real
  outcomes.
