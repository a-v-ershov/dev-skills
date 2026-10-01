# Closing report format (shared — all three pipelines)

Every skill in this set ends its run with a report to a human who did not watch it work. These rules
govern that report.

## 1. End with «What you should do»

The **last** block of any closing report is a numbered list of what the human has to do, in the
imperative, one line each. Nothing else goes in it.

```
## What you should do

1. Open http://localhost:3100/library and check the upload progress bar reads sensibly on a slow file.
2. Decide on T045 — I could not reproduce the 404; the options are "leave it" or "spend hours on it".
3. Nothing else. The rest is done and proven.
```

It answers the commonest question after a long run — *"so what do I actually need to do?"* Rules:

- **Imperative, addressed to the human.** "Open X and check Y", not "the upload flow remains
  unverified".
- **One line per item, no jargon from this skill set.** Not `needs_human`, not `spec_sync`, not
  `review: auto`, not "the gate is red" — say what those *mean for them*: "one task is stuck and needs
  your decision", "the spec now disagrees with what was built".
- **Only what actually requires a person.** If nothing does, one line: "Nothing — this is finished."
  That is a good outcome, not a failure to fill the block.
- **Say what happens if they do nothing**, where that matters ("until you decide, every `make reset`
  breaks the Disk connection the same way").
- **In the user's language**, like the rest of the report (`glossary.md`).

## 2. Timings must add up, or say why they don't

When a report gives stage timings, it also gives the number that reconciles them with the total.

```
Time: build 36m · verify 35m39s · fix 9m07s · solve 20m04s · waiting on you 58m39s · total 2h39m29s
```

- **Wall-clock, always** — including every wait on a permission prompt, an `AskUserQuestion`, or an
  absent human.
- **The waiting is its own line item** — name the gap instead of leaving parts that don't sum to the
  total.
- **Report the numbers flat, no verdict.** "Slow" is the human's judgement; make the arithmetic
  checkable.

## 3. Simpler to understand beats more complete

The KPI of the whole report: **the human understands the result on one read, without a follow-up
question.** Completeness lives in the artifact doc; the report is the briefing.

- **Lead with the outcome.** The first line answers "what happened / what did you find" — the verdict
  before the journey, not the method.
- **Detail that does not change what the human does next goes to the doc**; the report links to the
  committed findings/summary doc instead of retelling it.
- **The set's vocabulary only where the glossary requires an anchor.** Elsewhere, say what things mean
  for the reader — the «What you should do» rule applied to the whole text.

## 4. Status on demand, not only at the end

A long run must answer "what are you doing right now?" without finishing first: write state **before**
the expensive step starts, not after it ends — a task marked `in_progress` before its agent is spawned,
a progress line regenerated as the run advances (`backlog-format.md`).
