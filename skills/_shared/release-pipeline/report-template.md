# Report templates (shared — release pipeline)

Two shapes: the per-audit findings doc (`.dev-skills/release/<noun>-audit.md`, written by each `audit-*`) and
the combined release summary (`.dev-skills/release/release-summary.md`, built by `release-product`). Fill in;
delete the italic guidance.

## Per-audit findings doc — `.dev-skills/release/<noun>-audit.md`

```
# <Domain> audit — <product>

- Date: <YYYY-MM-DD>
- Contract: <path to the spec doc + the items proved against>
- Verdict: **<clean | N blockers | N majors>**  ·  Iteration: <n>/<max_audit_iterations>

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

## Filed for rework
- <count> tasks across <audits> — see .dev-skills/build-plan/board.md

## Audits run
| audit | verdict | blockers | majors | doc |
|-------|---------|----------|--------|-----|
| security | clean | 0 | 2 | security-audit.md |
| …        |       |   |   |                  |

## Shipped (if cut-release ran)
- version <x.y.z> · tag <…> · PR <link> · changelog updated
```

Roll up; do not re-derive — concatenate each audit's verdict + the cut-release result.
