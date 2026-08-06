# Report templates (shared — release pipeline)

Two shapes: the per-step findings doc (`.dev-skills/release/<noun>-audit.md` from each `audit-*`, and the
same shape for `refactor.md`, `test-gaps.md`, `manual-test-brief.md`) and the combined release summary
(`.dev-skills/release/release-summary.md`, built by `release-product`). Fill in; delete the italic
guidance.

## Per-step findings doc — `.dev-skills/release/<noun>-audit.md`

```
# <Domain> audit — <product>

- Date: <YYYY-MM-DD>
- Contract: <path to the spec doc + the items proved against>
- Verdict: **<clean | N blockers | N majors>**  ·  Round: <first | after the fix round>

## Findings

| id | sev | finding | evidence | contract item | filed task |
|----|-----|---------|----------|---------------|------------|
| S1 | 🔴  | <one line> | artifacts/<file> | <scenario / threat id> | T0NN |
| S2 | 🟡  | …          | …                | …                      | T0NN |
| S3 | ⚪  | …          | …                | …                      | —    |

## Checked
- <contract item> → <how it was probed> → <proven outcome>

## Skipped (and why)
- <item> — <reason: out of scope / contract absent / not measurable here>

## Sources
- <only for world-claims the audit leaned on>
```

The findings table is the heart: every row carries **proof** (an evidence link) and a **contract item**
(what it traces to). A row with neither is a hunch, not a finding — drop it or downgrade to a note.

## Combined release summary — `.dev-skills/release/release-summary.md`

Built by `release-product` at the end of a run — decisions-first, for the human:

```
# Release summary — <product> <version>

## Verdict
**<ready to cut | blocked>** — <one line>

## Must act (open blockers + waivers)
- 🔴 <finding> → task T0NN <status>
- waived: <finding> — <who waived it, why>

## Owned by setup-production-environment
- <missing production capability — no spend cap / no error tracking / variable unset> — not a code fix

## Filed for rework
- <count> tasks across <steps> — see .dev-skills/build-plan/board.md

## Steps run
| step | verdict | blockers | majors | doc |
|------|---------|----------|--------|-----|
| refactor | done | 0 | 1 | refactor.md |
| write-tests | 3 gaps closed, 1 bug filed | 1 | 0 | test-gaps.md |
| security | clean | 0 | 2 | security-audit.md |
| …        |       |   |   |                  |

## Hands-on pass (manual-test)
- <count> items waiting for a person — see manual-test-brief.md; <count> of them accepted as review: auto

## Shipped (if cut-release ran)
- version <x.y.z> · tag <…> · PR <link> · changelog updated

## What you should do
1. <imperative, one line, in the user's language — no pipeline jargon>
2. …
   (the hands-on pass above · `/setup-production-environment` when the product goes live · nothing, if
   nothing genuinely needs a person)
```

Roll up; do not re-derive — concatenate each step's verdict + the cut-release result. The **«What you
should do»** block is always last and always present, even when it says there is nothing:
**`../build-pipeline/report-format.md`**.
