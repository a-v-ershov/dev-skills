# Review method (shared — spec pipeline)

The adversarial review stage of each phase. A **separate** reviewer hunts what is wrong or missing in
the draft and **returns its findings in its final message** — no file, no edits to the draft, no merge
stage. The phase applies the findings itself and records the changes in the research doc's
`## Forks / Decisions log`.

## How to run it

**Delegate to the `spec-reviewer` agent** (Agent tool, `subagent_type: spec-reviewer`) — a fresh
reviewer that did not draft this. It carries the method: two jobs (**check the draft against its
inputs and itself**; **name the gaps**), the taxonomy + severity below, the return format.
Definition: `agents/spec-reviewer.md`.

Hand it the **draft path**, the **phase name**, the **paths of the prior phases' research docs** and
**this phase's specific probes**. It returns synchronously: findings, most severe first, plus the
🔴/🟡/⚪ counts.

## The reviewer does not go online

**Offline by design** (`Read`, `Grep`, `Glob` only — no `WebSearch`, no `WebFetch`), so it doesn't
double the phase's network cost. It audits citations **on their face**:

- a claim that needs a source (a price, a limit, a market number, "X still exists") with **no** `[S…]`
  reference → 🟡 *unverified claim*;
- an `[S…]` whose `## Sources` entry is a blog, an aggregator or a vendor's own page where the claim
  demands a primary or independent one → 🟡 *weak source*;
- a source dated well before a fast-moving fact (pricing, model versions, free tiers) → 🟡 *stale
  source*.

The phase spends a **reserved fetch** (see `research-method.md`) on the one or two that change a
decision and labels the rest unverified in the Forks / Decisions log. Contradictions, unsupported
leaps, gaps and placeholders need no network.

## Inconsistency types to hunt

Generic: internal contradiction; unsupported claim; a conclusion that does not follow from the doc
itself; a vendor metric passed off as objective; a citation of the wrong *kind* for its claim.

Spec-specific:

- A feature / requirement that traces to **no validated need**.
- A user flow that needs a capability **not in the product requirements**.
- A success metric with no signal / target / measurement.
- An audience or persona too vague to act on ("enterprises", "everyone").
- A fork resolved with weak or no justification.
- A claim that contradicts a prior phase's approved artifact — read it (that is what the prior-doc
  paths are for).
- An unfilled placeholder or left-in `TODO` / `TBD` / `???` / `<...>`, or an acceptance criterion /
  success metric with no number or observable outcome. (🔴 for an empty placeholder or an
  unmeasurable criterion; 🟡 for a deliberate, labelled "TBD".)

## Severity

- 🔴 **Critical** — wrong enough to change a decision: a false premise the phase rests on, a
  feature with no need, a flow that can't work, a contradiction with an approved prior phase.
- 🟡 **Medium** — a real problem that weakens the doc but doesn't break it: thin justification, a
  missing edge case, an unverified or weakly sourced number.
- ⚪ **Minor** — polish: wording, a softer caveat, a nice-to-have source.

## Return format (no file)

The final message **is** the deliverable: findings only, at most **7**, most severe first. Format:
`review-format.md`.

## Hand-off

The **fix stage** applies the findings to `<artifact>.research.md`: 🔴 per the mode (interactive —
stop and ask; autopilot — resolve and log, see `pipeline-config.md`), 🟡 by the phase's judgement, ⚪
if cheap. Each applied finding is logged in the `## Forks / Decisions log` — the review's only trace.
