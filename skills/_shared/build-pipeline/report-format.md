# Closing report format (shared — all three pipelines)

Every skill in this set ends its run with a report to a human who did not watch it work. Two rules
govern that report, and they exist because both were violated repeatedly in the field.

## 1. End with «What you should do»

The **last** block of any closing report is a numbered list of what the human has to do, in the
imperative, one line each. Nothing else goes in it.

```
## What you should do

1. Open http://localhost:3100/library and check the upload progress bar reads sensibly on a slow file.
2. Decide on T045 — I could not reproduce the 404; the options are "leave it" or "spend hours on it".
3. Nothing else. The rest is done and proven.
```

Rules for the block:

- **Imperative, addressed to the human.** "Open X and check Y", not "the upload flow remains
  unverified".
- **One line per item, no jargon from this skill set.** Not `needs_human`, not `spec_sync`, not
  `review: auto`, not "the gate is red" — say what those *mean for them*: "one task is stuck and needs
  your decision", "the spec now disagrees with what was built".
- **Only what actually requires a person.** If nothing does, the block is one line: "Nothing — this is
  finished." An empty block is a good outcome, not a failure to fill it in.
- **Say what happens if they do nothing**, where that matters ("until you decide, every `make reset`
  breaks the Disk connection the same way").
- **In the user's language**, like the rest of the report (`glossary.md`).

Why: measured in the field, the single most common user turn after a long run was some form of *"so
what do I actually need to do?"* — after reports that were accurate, complete, and unreadable.
"Гард здесь не формальность. не понял? нужно ли что-то править?" is what a correct report that skipped
this block produces.

## 2. Timings must add up, or say why they don't

When a report gives stage timings, it also gives the number that reconciles them with the total.

```
Time: build 36m · verify 35m39s · fix 9m07s · solve 20m04s · waiting on you 58m39s · total 2h39m29s
```

- **Wall-clock, always** — these are honest elapsed times, and they include every stretch spent waiting
  on a permission prompt, an `AskUserQuestion`, or the human being away.
- **The waiting is its own line item.** A report whose parts sum to 1h40m under a 2h39m total invites
  exactly one question, and it is a fair one. Name the gap instead of leaving it to be found.
- **Report the numbers flat, with no verdict attached.** "Slow" is a judgement the human makes; your
  job is to make the arithmetic checkable.

## 3. Status on demand, not only at the end

A long run must be able to answer "what are you doing right now?" without finishing first. That means
state is written **before** the expensive step starts, not after it ends — a task marked `in_progress`
before its agent is spawned, a progress line regenerated as the run advances
(`backlog-format.md`). A board that says nothing is in progress while an agent has been
running for fifty minutes is a bug in the bookkeeping, not in the human's patience.
