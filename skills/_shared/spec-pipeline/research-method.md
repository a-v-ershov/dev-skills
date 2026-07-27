# Research method (shared — spec pipeline)

How any spec phase gathers and verifies real-world facts. Loaded by the research stage of each
phase skill. The persona-specific *topics* to research live in each skill; the *method* is here.

## The budget — a hard cap, not a judgement call

Research is the pipeline's most expensive stage, and most of that cost is network latency rather
than thinking. So the depth is **capped up front**, not decided in the moment:

- **Per phase: at most 4 `WebSearch` calls and at most 4 `WebFetch` opens.** That is the phase's
  whole allowance. **Reserve ~2 of the fetches** for re-checking a point the review disputes (the
  fix stage), so the phase does not have to choose between verifying the draft and verifying the
  correction.
- **Spend it on decision-changing facts only.** Rank this phase's open factual questions by "would
  a wrong answer here change what we build?" and research from the top down until the budget is
  gone. Everything below the line is answered from what you already know, logged in the
  `## Forks / Decisions log` with `Confidence = med|low` and no source. That is a legitimate
  outcome, not a failure — an unverified fact that is *labelled* unverified costs nothing; an hour
  of link-reading does.
- **Zero is a valid budget.** If nothing in the phase hinges on an external fact, skip research
  entirely and say so, rather than inventing a reason to search.
- **`/deep-research` only on the user's explicit request.** It is outside the budget and costs many
  minutes. Never reach for it on your own initiative, however contested the landscape looks.

## How to run it

**Delegate to the `spec-researcher` agent** (Agent tool, `subagent_type: spec-researcher`), so the
searching and link-reading stay out of the phase's main context. The agent carries this method — the
budget above, the search rules and verification-standard below, and the return format.
Definition: `agents/spec-researcher.md`. In the spawn prompt, give it **this phase's open factual
questions, ranked**, and **the remaining budget**:

- It **works synchronously and returns findings before exiting** — it does not spawn background
  sub-agents and does not return until the findings (or "no reliable data") are in hand.
- It **stops when the budget is exhausted**, even with questions left open, and says which ones it
  did not get to. Spending the budget is the stop condition; certainty is not.
- It returns findings **grouped by topic** — each a one-line description + a **primary-source link**;
  anything unverifiable is "no reliable data" (a finding, not a failure). It writes no file.

## Search rules

- **One query per claim.** Fan out to a second angle only when the first result is ambiguous or
  contradicts what the phase assumed — not as a matter of routine. Independent queries run in
  parallel, so a batch of distinct claims costs one round-trip, not four.
- **Open a page only when the snippet cannot answer it.** Spend a `WebFetch` on prices, limits,
  versions, and "does this still exist" — the facts where a stale secondary source actually misleads.
  For everything else the search result is enough.
- **Refute only the load-bearing facts.** Actively look for why a fact might be wrong (outdated,
  renamed, a marketing number) for the handful the phase's decision rests on. Not for every claim.
- **Cite what you verified; mark what you didn't.** Every researched fact carries a primary-source
  link. A conflict *between* sources is itself a finding — record it. Anything asserted from
  training knowledge is marked unverified rather than dressed in a plausible link. Account for
  today's date.

## Verification standard by fact type (applies within the budget)

- **Comparisons / superlatives** ("X is the leader in Y"): check the *current* properties of
  *all* named competitors, not just the hero of the claim.
- **Names / versions / entities:** confirm it exists and is *current* (not discontinued/renamed).
- **Numbers / prices / limits:** primary source only; a secondary aggregator alone is not enough.
- **Vendor metrics:** attribute them ("by the vendor's own estimate, on these tasks"), never as
  an independent measurement.
- **Dates:** distinguish announced / released / GA / regional availability.

## What the phase does with the findings

Research **feeds the draft** — it does not become a separate file. Weave verified facts into the
detailed doc inline and list every source in the doc's `## Sources` section (see
`output-format.md`). When research resolves a fork, log it in the `## Forks / Decisions log` with
its source.
