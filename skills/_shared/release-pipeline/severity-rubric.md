# Severity rubric (shared — release pipeline)

How an audit ranks a finding, and what blocks the release. Every `audit-*` skill ranks against this
rubric — against the **contract** (the spec's scenarios / threat model / decisions / flows), never
against taste. Defined once here; the audits and `release-product` reference it.

## The three levels

- 🔴 **Blocker** — the release must not go out with this open. The system **violates its contract** in a
  real, proven way: an exploitable vulnerability on a live path, a measured breach of a quality-attribute
  scenario (p95 over budget, cost over budget), a broken cross-feature user flow, a WCAG-A failure on a
  core journey. Blockers gate the release.
- 🟡 **Major** — a real, proven problem that **degrades** the system without breaking its contract: a
  scenario met but with no margin, a vulnerability behind auth with low exploitability, a slow
  non-critical path, large-scale duplication in an active module. Filed as a rework task; does **not**
  by itself block the release (the human / orchestrator decides whether to hold).
- ⚪ **Minor** — polish with no contract impact: a nit, a nice-to-have hardening, a cosmetic a11y
  improvement off the core path. Recorded in the findings doc; **not** filed as a task.

## What blocks the release

- **Any open 🔴 blocks.** It must be fixed (a `build-tasks` rework run) and the audit re-run clean, or
  explicitly waived by the human with the waiver logged in the findings doc.
- **🟡 majors are filed, not blocking.** They become rework tasks; `release-product` surfaces the count,
  but a release may be cut with open majors at the human's call (logged).
- **⚪ minors never block.**

## Guard against over-engineering (anti-sycophancy, in reverse)

A reviewer asked to find problems will always find some — that is the documented failure mode. The
rubric is the guard:

- **Flag against the contract, not against an ideal.** "A stricter CSP would be nicer" is not a finding
  unless a threat in the model demands it. "Could be faster" is not a finding unless a scenario sets a
  budget it misses.
- **No finding without proof.** Severity follows evidence (a measured number, a reproduced exploit, a
  failing rule), not a hunch. An unproven worry is a note to investigate, not a 🔴.
- **Speculative hardening is ⚪ at most.** Defense-in-depth ideas with no threat behind them do not block
  a release and do not become tasks unless the human asks.

The throughput failure mode of an audit is not "too lenient" — it is a wall of 🟡/⚪ noise that buries
the one 🔴 that mattered. Rank ruthlessly.
