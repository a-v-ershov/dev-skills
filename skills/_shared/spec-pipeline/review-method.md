# Review method (shared — spec pipeline)

The adversarial review stage of each phase. After the draft is written, a **separate** reviewer
hunts what is wrong or missing and **returns its findings in its final message**. It writes no file
and never edits the draft — the phase applies the findings itself, in place.

There is no review artifact and no merge stage: the reviewer's list goes straight into the phase's
fix stage, and what it changed is recorded in the research doc's `## Forks / Decisions log`.

## How to run it

**Delegate to the `spec-reviewer` agent** (Agent tool, `subagent_type: spec-reviewer`) — a fresh,
independent reviewer that did not draft this. The agent carries the reviewer method: its two jobs
(**check the draft against its inputs and itself**; **name the gaps** it left), the inconsistency
taxonomy + severity below, and the return format. Definition: `agents/spec-reviewer.md`.

Hand it: the **draft path**, the **phase name**, the **paths of the prior phases' research docs**,
and **this phase's specific probes**. It works synchronously and returns a findings list, most
severe first, plus the 🔴/🟡/⚪ counts.

## The reviewer does not go online

The reviewer is **offline by design** (`Read`, `Grep`, `Glob` only — no `WebSearch`, no `WebFetch`).
Re-opening every cited source doubles the phase's network cost to re-litigate facts the research
stage already spent its budget on. Instead the reviewer audits citations **on their face**:

- a claim of the kind that needs a source (a price, a limit, a market number, "X still exists")
  carrying **no** `[S…]` reference → 🟡 *unverified claim*;
- an `[S…]` whose entry in `## Sources` is a blog, an aggregator, or a vendor's own page where the
  claim demands a primary or independent one → 🟡 *weak source*;
- a source dated well before a fast-moving fact (pricing, model versions, free tiers) → 🟡 *stale
  source*.

The phase then decides: spend one of its **reserved fetches** (see `research-method.md`) on the one
or two findings that actually change a decision, and label the rest unverified in the Forks /
Decisions log. Everything else a review is worth — contradictions, unsupported leaps, gaps,
placeholders — needs no network at all.

## Inconsistency types to hunt

Generic: internal contradiction; unsupported claim; a conclusion that does not follow from what the
doc itself says; a vendor metric passed off as objective; a citation that is not the right *kind* of
source for its claim (see above).

Spec-specific (also flag these):

- A feature / requirement that traces to **no validated need**.
- A user flow that needs a capability **not in the product requirements**.
- A success metric with no signal / target / measurement.
- An audience or persona too vague to act on ("enterprises", "everyone").
- A fork resolved in the draft with weak or no justification.
- A claim that contradicts a prior phase's approved artifact — read it; that is what the prior-doc
  paths are for.
- An unfilled template placeholder or a left-in `TODO` / `TBD` / `???` / `<...>`, or an acceptance
  criterion / success metric with no number or observable outcome — they silently reach
  implementation. (🔴 for an empty placeholder or an unmeasurable criterion; 🟡 for a deliberate,
  labelled "TBD".)

## Severity

- 🔴 **Critical** — wrong enough to change a decision: a false premise the phase rests on, a
  feature with no need, a flow that can't work, a contradiction with an approved prior phase.
- 🟡 **Medium** — a real problem that weakens the doc but doesn't break it: thin justification, a
  missing edge case, an unverified or weakly sourced number.
- ⚪ **Minor** — polish: wording, a softer caveat, a nice-to-have source.

## Return format (no file)

The reviewer's final message **is** the deliverable. Compact, findings only — at most **7**, most
severe first, so the phase can act on all of them. Format: `review-format.md`.

## Hand-off

The findings go to the phase's **fix stage**, which applies them directly to
`<artifact>.research.md`: 🔴 per the mode (interactive — stop and ask; autopilot — resolve and log,
see `pipeline-config.md`), 🟡 by the phase's own judgement, ⚪ if cheap. Each applied finding is
logged in the research doc's `## Forks / Decisions log` — the only trace the review leaves. There is
no review file to keep, delete, or gitignore.
