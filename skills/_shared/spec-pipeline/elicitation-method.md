# Elicitation method (shared — spec pipeline)

How any spec phase runs its **Elicit** stage: an iterative interview that extracts the human's
real context instead of accepting the first vague answer. Loaded by the elicitation stage of each
phase skill. The *dimensions* to cover live in each skill (its persona's questions); the
*interview technique* is here. The standalone, reusable form of this technique is the
**`gather-context`** skill — the front intake phase of the pipeline and an on-demand "grill".

The goal is a **shared understanding**: the human and the AI end up meaning the same thing by the
same words, so the doc this phase writes is what the human actually wanted built. Maximize the
context you gather — but bounded by that goal (see *Stop condition*), not by a question quota.

## The core loop

You are not running a questionnaire. The human says something; **you decide the next question**
from what they just said, to go one level deeper on the thing that matters most. Ask, listen, let
the answer reshape the tree of what's still open, ask again. The interview ends when nothing
material is still unknown — not after N questions.

## Principles (non-negotiable)

- **One thread at a time — but batch the independent, already-sharp forks.** Pursue one dimension
  (one fork) to the bottom before moving on; depth is what gets real answers, where a wall of vague
  open questions gets shallow ones. That applies to *open* questions. When several forks are
  *independent* — no one depends on another's answer — and each already reduces to a small set of
  options with a recommendation, present them together in one structured prompt rather than one slow
  round-trip each (see *Choosing how to ask*). Never batch a question whose framing depends on an
  unanswered one — keep dependency order (next principle).
- **Walk the decision tree, resolving dependencies in order.** Later questions depend on earlier
  answers — settle the upstream decision first, then ask the ones it unlocks. Never ask a question
  whose answer an earlier answer already implies; never ask in an order that forces the human to
  guess about something you haven't established yet.
- **Always offer your recommended answer.** With every question, propose the answer you'd pick and
  one line of why, so the human can affirm with a word ("yes" / "yes, but X") instead of composing
  prose. This is the speed unlock — a good default turns a hard question into a quick confirmation.
  Make the recommendation real (take a position), not a menu of equal options.
- **Self-answer from evidence before asking.** If a question can be answered by reading — the repo,
  the prior phase's research doc, the project brief, or light research — read it and answer it
  yourself, then ask only to confirm or correct. Never spend the human's attention on something you
  could have looked up. State what you found: "The brief says X, so I'm assuming Y — correct?"
- **Push past the first answer.** The first answer is the polished one; the real context is in the
  second and third. When an answer is generic ("users", "make it fast", "like everyone else"), ask
  the follow-up that forces specificity — a name, a number, a concrete example, a real situation.
- **Surface ambiguity by imagining the alternatives.** Before asking about an underspecified point,
  generate two or three plausible readings of it yourself. If they would lead to *different*
  products, you've found a real fork — ask the question that splits them (ideally as the options of
  one structured question), not a vague open one. If they'd converge on the same build, don't ask.
- **Mirror back to confirm shared understanding.** Periodically restate what you've heard in your
  own words and have the human correct it. Name contradictions out loud ("earlier you said X, now
  Y — which holds?"). Shared understanding is something you *verify*, not assume.
- **Cover, then stop.** Track what you've covered against this phase's dimensions. Don't over-grill
  a settled point or chase detail that won't change the doc.

## Choosing how to ask (the mechanism)

The principles above are *what* to ask; this is *how* to deliver it.

- **Closed fork (a small set of options) → use `AskUserQuestion`.** Put the answer you'd pick first
  and label it `(Recommended)`, and give each option a one-line consequence. The tool pauses and
  lets the human pick with a click instead of composing prose — that is the speed unlock. Always
  leave room for a free-form answer: "you decide" and "not relevant to this" are valid, and the tool
  takes custom input.
- **Batch the independent forks.** `AskUserQuestion` takes up to four questions in one call — when
  several forks are independent, ask them together rather than serially. Keep *dependent* forks in
  separate, ordered calls: you cannot frame a question whose options hinge on one the human hasn't
  answered yet.
- **Open-ended thread → prose.** When a dimension needs a story, not a choice ("walk me through how
  you do this today"), ask in plain conversation and go deep with follow-ups — a structured prompt
  would force a false multiple-choice. Use judgement: a live, thinking dialogue beats both a rigid
  questionnaire and a guessed default.
- **`autopilot` doesn't prompt.** There is no human to ask, so resolve every fork yourself and log
  it (below); `AskUserQuestion` is for the interactive interview only.

## Stop condition (shared understanding reached)

Stop when **no material unknown remains** — nothing still-open would change what this phase
writes. At that point, give a short **summary of the shared understanding** (the picture you've
built, in the human's terms) for a final confirmation, then proceed to the rest of the phase. If
unknowns remain but the human is out of answers, record them as forks (`Needs human confirm? =
yes`) rather than inventing certainty. Name what you deliberately did **not** ask and why, so
"done" doesn't read as "covered everything".

## Read the brief first

Every phase reads **`.dev-skills/project-spec/project-brief.research.md`** (the discovery dossier from
`gather-context`) at intake, if present. Treat it as **two distinct classes of input**:

- **Intent & constraints** (the goal, audience, scope, budget, timeline, platforms, compliance, hard
  requirements) are **settled input** — do not re-ask what the brief already answers; confirm and
  build on it. (Settled *intent*, not settled *truth*: `validate-idea` still pressure-tests its
  claims.)
- **Developer preferences** (the "Preferences & taste" priors — stack & libraries, code style &
  idioms, design taste, dev tooling, architecture leanings) are **soft priors**, not constraints.
  Bias the relevant fork toward them and use them as a **tie-breaker among options that already
  satisfy this phase's requirements/scenarios** — but decide on the merits: a requirement or
  scenario always wins over a preference, and a preference never short-circuits the
  requirements-first step. Log every preference that influenced a decision in the
  `## Forks / Decisions log` with `Source = preference`; when you override one, record why.
  (Preferences are soft by design — the human can be wrong about what fits *this* project.)

## When the repo already has code

There is **no separate brownfield mode** — no config flag, no front phase, no parallel vocabulary.
Working against existing code is just "self-answer from evidence before asking", pointed at a
repository:

1. **Look before you ask.** At intake, check whether the repo holds real code (a dependency manifest
   plus source outside docs/config). If it does, read what *this phase* needs from it — surfaces and
   routes for features, routing for flows, manifests and configs for the stack, UI dependencies for
   the design direction. Never make someone narrate their own codebase to you.
2. **Say what you found, in a few lines.** "I see Next.js + Postgres, 6 routes, `users`/`documents`
   tables, no tests." The user corrects you *before* you build on it — and that costs one message
   instead of a wrong document.
3. **Confirm instead of re-asking.** Each finding becomes a confirmation: "the code does X — is X
   what we're keeping, or do you want it changed?" rather than the greenfield form of the question.
4. **Keep the code's names by default.** The de-facto glossary (tables, models, routes) usually
   disagrees with the vocabulary you'd invent. Renaming is a decision the user makes deliberately,
   with refactor work attached — never a silent relabel in the spec.
5. **Record the differences in one place.** Where intent differs from what's built, add a line to the
   doc's `## Divergences (code vs intended)` section: what the code does now · what's wanted ·
   whether it's a change, a removal, or something not built yet. That short list is what
   `plan-development` later turns into tasks.

Everything else is unchanged: same stages, same outputs, same gates. If the repo is empty, none of
this applies and the section stays out of the document.

## Escalate to `gather-context` when a fork blocks understanding

When a fork is genuinely blocked on context only the human holds — you can't answer it from the
docs, and resolving it wrong would derail the phase — **invoke the `gather-context` skill scoped to
that fork** (via the Skill tool) to run a focused mini-interview, then fold the gathered answers
back into this phase (draft + Forks / Decisions log) and continue. Use it for a real blocker, not
as a substitute for the per-thread questions above. (In autopilot this does not apply — the AI
resolves the fork itself and logs it; see below.)

## Mode behavior

- **interactive** — actually interview the human, by the loop and principles above. This is where
  the technique earns its keep.
- **autopilot** — there is no human in the loop, so **walk the same decision tree yourself**:
  pose each question, answer it from the brief + prior docs + research + best judgment, and **log
  every answer in the `## Forks / Decisions log`** with options, choice, rationale, confidence, and
  source. Mark anything decided at low/medium confidence, or with material downside if wrong, as
  `Needs human confirm? = yes` so it surfaces in the human summary. Autopilot changes *who answers*,
  never *whether it's asked and recorded*.
- **on-demand `gather-context`** (the user invokes the grill directly) is always interactive — the
  whole point is to interview the human — regardless of the pipeline mode.

## What the phase does with the answers

The interview **feeds the draft** — it is not a separate file (except `gather-context`'s own brief,
which is a kept artifact). Every decision the interview settles goes into the phase's
`## Forks / Decisions log` (see `output-format.md`); unresolved ones go to `## Open questions` and
the human summary.
