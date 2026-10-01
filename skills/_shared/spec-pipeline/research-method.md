# Research method (shared — spec pipeline)

How any spec phase gathers and verifies real-world facts. The *topics* live in each skill; the
*method* is here.

## The budget — a hard cap, not a judgement call

The pipeline's most expensive stage (mostly network latency), so depth is **capped up front**:

- **Per phase: at most 4 `WebSearch` calls and at most 4 `WebFetch` opens.** **Reserve ~2 of the
  fetches** for re-checking a point the review disputes (the fix stage).
- **Spend it on decision-changing facts only.** Rank the open factual questions by "would a wrong
  answer change what we build?" and research top-down until the budget is gone. Everything below the
  line is answered from what you know and logged in the `## Forks / Decisions log` with
  `Confidence = med|low` and no source — a legitimate outcome, not a failure.
- **Zero is a valid budget.** If nothing hinges on an external fact, skip research and say so.
- **`/deep-research` only on the user's explicit request.** Outside the budget, costs many minutes;
  never on your own initiative, however contested the landscape looks.

## How to run it

**Delegate to the `spec-researcher` agent** (Agent tool, `subagent_type: spec-researcher`; it carries
this method — definition `agents/spec-researcher.md`) so the searching stays out of the phase's main
context. Spawn prompt: **this phase's open factual questions, ranked**, and **the remaining budget**.

The agent:

- **works synchronously and returns findings before exiting** — no background sub-agents;
- **stops when the budget is exhausted**, even with questions open, and names the ones it skipped —
  spending the budget is the stop condition, not certainty;
- returns findings **grouped by topic** — one-line description + **primary-source link**; anything
  unverifiable is "no reliable data" (a finding, not a failure). It writes no file.

## Search rules

- **One query per claim.** A second angle only when the first result is ambiguous or contradicts the
  phase's assumption. Independent queries run in parallel — one round-trip per batch.
- **Open a page only when the snippet cannot answer it.** Spend a `WebFetch` on prices, limits,
  versions and "does this still exist" — where a stale secondary source misleads.
- **Refute only the load-bearing facts.** Look for why a fact might be wrong (outdated, renamed, a
  marketing number) for the handful the decision rests on.
- **Cite what you verified; mark what you didn't.** Every researched fact carries a primary-source
  link. A conflict *between* sources is itself a finding. Anything from training knowledge is marked
  unverified, never dressed in a plausible link. Account for today's date.

## Verification standard by fact type (applies within the budget)

- **Comparisons / superlatives** ("X is the leader in Y"): check the *current* properties of *all*
  named competitors.
- **Names / versions / entities:** confirm it exists and is *current* (not discontinued/renamed).
- **Numbers / prices / limits:** primary source only; an aggregator alone is not enough.
- **Vendor metrics:** attribute them ("by the vendor's own estimate, on these tasks"), never as an
  independent measurement.
- **Dates:** distinguish announced / released / GA / regional availability.

## What the phase does with the findings

Research **feeds the draft** — no separate file. Weave verified facts into the detailed doc inline
and list every source in `## Sources` (see `output-format.md`). When research resolves a fork, log
it in the `## Forks / Decisions log` with its source.
