# Lanes and timing (run-task)

Two things `run-task` needs in full but not on every line of its main procedure: when the quick
lane is allowed, and how the stages are clocked. Read the relevant half when you reach it.

---

## The quick lane (small, obvious, provably bounded)

The full cycle costs an implementer, a separate verifier, a fix round and two gate runs. That is the
right price for a feature and an absurd one for moving a heading's padding — and when it is charged
anyway, the user starts asking to go around the pipeline entirely ("just do it quickly, without a
task"). Going around it loses the record. So the lane is **inside** the skill, with hard edges.

**Eligible only when ALL of these hold** — you assert them out loud before starting, in one line each:

1. **One concern**, describable in a sentence, with an outcome the user can see for themselves.
2. **Small diff**: about **40 changed lines across at most 3 files**, and no new file that carries
   logic.
3. **Nothing load-bearing**: no schema or migration, no auth / permission / ownership rule, no money,
   no deletion or retention, no public API or CLI contract, no new dependency, no config the
   deployment reads, no `DESIGN.md` token (frozen — **`../../_shared/build-pipeline/design-freeze.md`**).
4. **Provable cheaply**: the existing scoped selection covers it, or one small test does.

Anything failing a bullet takes the full cycle. **Uncertain counts as failing.**

**The lane itself:**

- Stage 0/1 as usual — the task file **is** written (`origin: adhoc`, `lane: quick` noted in the
  `## Log`), the claim is written, the board is regenerated. The record is not what gets skipped.
- The **same implementer agent** builds it. **No separate verifier** — that is the one step the lane
  drops, and dropping it is exactly why the bounds above are narrow.
- Gate: **static gate + this task's scoped selection**, green. Unchanged.
- Acceptance is **always human** (`review: human`): the whole justification for skipping the verifier
  is that a person can see the result in a few seconds. Show the diff and how to look at it.
- Commit as usual, with the task id.

**Escalation is one-way and immediate.** The moment the work crosses a bound — the diff grows, a
migration turns out to be needed, the fix touches auth — stop, say which bound broke, keep the work,
and finish the task through the **full** cycle from Stage 3. Never quietly finish a big change in the
small lane.

---

## Timing the stages

**You** time the work, because nobody else can: an agent cannot see its own clock, and the duration of
a subagent never comes back inside the result you receive — only its text does. So bracket the stages
you dispatch. At Stage 1, and at each boundary of Stages 2–5, take one reading:

```sh
date -u '+%Y-%m-%dT%H:%M:%SZ %s'
```

Keep the epoch seconds and subtract: `build` (Stage 2), `verify` (Stage 3), `fix` (Stage 4 — only when
the fix round actually ran), `solve` (Stage 5), and `total` (Stage 1 → the end). Write them into the
task's `timings` block in **one** edit when the task leaves you, at Stage 8 or at the `needs_human`
stop. Schema and how to read the numbers: **`../../_shared/build-pipeline/backlog-format.md`**.

---

## Spawning and recovering an implementer

**What the spawn prompt must carry.** The agent is fresh and knows nothing you know; a prompt that
passes only a task id makes it rediscover the project. Name: the task file's path · the project
`CLAUDE.md` and its invariants · **what recently changed** — the files the last closed tasks
rewrote, so it reads the current state instead of trusting line numbers in the task description ·
the branch rule and that it must not commit · the test boundary (unit inner loop, no e2e, no
adversarial suite — those are the verifier's; and it runs this task's scoped selection, never the
whole suite).

**If the agent dies before it reports** — an API error, a session limit, an interrupt — that is not a
failed task and not a `needs_human`, and it is not a reason to rebuild from zero. Measured in the
field, thirteen agents died mid-run in two projects, six of them after 18–61 minutes of work, and the
default reaction — respawn with the same brief — paid for that time twice.

The recovery is the task file, because the implementer **writes its journal into `## Log` as it goes**
(`implement-feature`), not at the end. So:

1. Read the task's `## Log` **first** — it is the surviving account of what the dead agent did and what
   it was in the middle of.
2. Check `git status`. Empty tree **and** an empty journal → nothing was lost; spawn a fresh
   implementer with the same brief.
3. Otherwise **resume**: spawn the implementer with the same brief **plus the journal**, and tell it
   explicitly that this is a resume, what is already done, and what to verify rather than redo.
4. If the journal is too thin to resume from, go to Stage 3 and tell the verifier plainly that the
   build is unattested and it must judge completeness too.

Never assume an interrupted build is finished, and never assume it is worthless.

---

## Accepting the work and catching the spec up

### Stage 6: Accept
Look at the **actual diff** and decide whether a person could check anything by hand:

- **Nothing hand-checkable** (the diff is tests, internal logic, config; every criterion was proven by
  the verifier) → accept it yourself, set `review: auto`, and record the one-line reason. Don't
  manufacture a question.
- **Something hand-checkable** → show a short digest and, in interactive, wait:
  > **Built:** <what it does now, in plain language — not file names>
  > **See it yourself:** <the URL/screen · which seeded user · the exact steps>
  > **Already proven:** <what the verifier asserted, one line each>
  In autopilot, record the same digest with `review: auto`.

Deferring acceptance is the human's call. If they ask for changes, that is a **new task** (or a
`rework` one) — not a reopening of this cycle.

### Stage 7: Spec catch-up
If the work changed observable product behavior the spec doesn't describe — a new screen, a changed
rule, an `adhoc` task with no `traces_to` — set `spec_sync: pending` and **propose the concrete
edit**, written out rather than described: the feature line for `product-requirements.research.md`,
the step or screen for `user-flows.research.md`. Interactive: offer it, apply on a yes. Autopilot:
apply and log it. It lands in the **same commit** as the code, so the spec never drifts by a whole
task; then set `spec_sync: done`. If the user declines, leave `spec_sync: pending` — the board
surfaces it and the next planning run will see it. Never block the task on this.

---

## The solve pass

### Stage 5: Solve pass + gate
Direct the **same implementer agent** to a light cleanup **scoped to this task's own diff** — remove
dead or duplicated code it introduced, collapse needless abstraction, drop over-built generality —
strictly **behaviour-preserving** — and a flag, parameter or command named in
`.dev-skills/project-setup/verification.md` **is** behaviour: from inside the diff it looks like an
argument nobody varies, but it is part of the contract the verifier drives the product by.
Pre-existing rot in code this task didn't touch is out of scope: note it as a `rework` task, never
tidy it here. (Agents over-produce and don't feel maintenance cost;
a deliberate pass stops bloat from compounding.)

Then confirm the **static gate** (`make check-fast`) and this task's **scoped test run** are green —
the selection now includes the verifier's tests and the tests of every module this task touched, so
the tidy stays honest. **Do not run the whole suite here**: the build loop never does, and the
release pipeline runs it over everything (**`../../_shared/build-pipeline/quality-gate.md`**). Red is
never committed and never triggers another round — it goes to `needs_human`.
