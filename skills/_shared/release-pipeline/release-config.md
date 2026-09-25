# Release config & modes (shared — release pipeline)

Settings that govern the release phase. `release-product` sets them once; each release skill (`refactor`,
`write-tests`, `audit-*`, `simplify-product`, `manual-test`, `cut-release`) reads them and adapts. Every skill is also
runnable standalone, so it falls back gracefully when no config exists.

## The settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: stop at each hard gate — a 🔴 blocker, before filing rework, and before the
    outward-facing `cut-release` — for the human.
  - `autopilot`: resolve ordinary forks itself and **log each** (in the step's findings doc), running the
    chain back-to-back — **except** the three things that always stop (below).
- **`steps`** — which of the release chain's steps are enabled. Default: all applicable, in this fixed
  order: `refactor` → `write-tests` → (`audit-security` · `audit-performance` · `audit-product` ·
  `audit-dependencies` · `simplify-product`, in parallel) → `manual-test`. A step self-skips and
  records why when it does
  not apply (e.g. the accessibility part of `audit-product` on a product with no UI,
  `audit-performance` with no measurable scenario, `audit-dependencies` with no dependency manifest).

There is **no iteration setting.** Findings get one fix round and one re-run of the affected audits;
whatever is still open then is `needs_human` (`audit-method.md` → "One round, then a decision").

## Config file — `.dev-skills/release/.release-config.md`

```
# Release pipeline config

- mode: interactive            # interactive | autopilot
- steps: refactor, write-tests, security, performance, product, dependencies, simplify, manual-test
```

## How a release skill uses it

1. At intake, read `.dev-skills/release/.release-config.md`.
2. **Present:** use `mode` and the enabled `steps`.
3. **Absent (standalone run):** ask the user once (one `AskUserQuestion`, defaults pre-selected:
   interactive + all applicable steps), then write the file so later standalone skills inherit it.

`.dev-skills/release/` is committed project documentation — no special gitignore; the release pipeline
keeps no transient files (every findings doc is kept as the audit trail).

## Three things ALWAYS stop, regardless of mode

Autopilot suppresses ordinary forks, but never these:

1. **`refactor`'s plan.** It rewrites working code; the human approves the transformation list before
   any of it is applied.
2. **A finding still open after the single fix round** — a `needs_human` escalation. The whole point is
   to surface to a human that the release cannot be cut.
3. **`cut-release` itself** — the outward-facing step (version bump, tag, push, PR) always confirms
   before acting, in both modes (the `careful` pattern). It is the release phase's analog of the build
   phase's "critical / destructive change propagation always stops".

Putting the product live is not on this list because it is not part of the release run at all:
`setup-production-environment` is invoked by hand, and confirms every external action on its own.

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged in the step's findings doc with the
  choice, rationale, and confidence.
- **Still do the work.** Autopilot skips human prompts — it does **not** skip the separate-agent audits,
  the evidence standard, red-first in `write-tests`, or the re-run after a fix.
- **Audits are never self-approved.** Even in autopilot each audit runs in a fresh, independent agent and
  proves real outcomes — it does not rubber-stamp.
