# Release config & modes (shared — release pipeline)

Settings that govern the release phase. `release-product` sets them once; each release skill (`audit-*`,
`cut-release`) reads them and adapts. Every skill is also runnable standalone, so it falls back
gracefully when no config exists.

## The settings

- **`mode`** — `interactive` (default) | `autopilot`.
  - `interactive`: stop at each hard gate — a 🔴 blocker, before filing rework, and before the
    outward-facing `cut-release` — for the human.
  - `autopilot`: resolve ordinary forks itself and **log each** (in the audit's findings doc), running
    audit → fix → re-audit back-to-back — **except** the two things that always stop (below).
- **`max_audit_iterations`** — integer, default **3**. The cap on the audit↔fix↔re-audit loop for a
  single audit. When a 🔴 survives this many rounds, the audit escalates to `needs_human` instead of
  looping again.
- **`audits`** — which of the five are enabled. Default: all. Each self-skips and records why if its
  contract is absent or N/A (e.g. `audit-accessibility` on a product with no UI, `audit-performance`
  with no measurable scenario).

## Config file — `.dev-skills/release/.release-config.md`

```
# Release pipeline config

- mode: interactive            # interactive | autopilot
- max_audit_iterations: 3      # cap on the audit↔fix↔re-audit loop before needs_human
- audits: security, performance, product, code-health, accessibility
```

## How a release skill uses it

1. At intake, read `.dev-skills/release/.release-config.md`.
2. **Present:** use `mode`, `max_audit_iterations`, and the enabled `audits`.
3. **Absent (standalone run):** ask the user once (one `AskUserQuestion`, defaults pre-selected:
   interactive + 3 + all applicable audits), then write the file so later standalone skills inherit it.

`.dev-skills/release/` is committed project documentation — no special gitignore; the release pipeline keeps no
transient files (every findings doc is kept as the audit trail).

## Two things ALWAYS stop, regardless of mode

Autopilot suppresses ordinary forks, but never these:

1. **A 🔴 blocker that survives `max_audit_iterations`** — a `needs_human` escalation. The whole point is
   to surface to a human that the release cannot be cut.
2. **`cut-release` itself** — the outward-facing step (version bump, tag, push, PR) always confirms
   before acting, in both modes (the `careful` pattern). It is the release phase's analog of the build
   phase's "critical / destructive change propagation always stops".

## Autopilot rules (non-negotiable)

- **Decide, but never hide.** Every fork the AI resolves is logged in the findings doc with the choice,
  rationale, and confidence.
- **Still do the work.** Autopilot skips human prompts — it does **not** skip the separate-agent audits,
  the evidence standard, or the re-audit after a fix.
- **Audits are never self-approved.** Even in autopilot each audit runs in a fresh, independent agent and
  proves real outcomes — it does not rubber-stamp.
