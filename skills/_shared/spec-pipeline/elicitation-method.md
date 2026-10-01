# Elicitation method (shared — spec pipeline)

How any spec phase runs its **Elicit** stage: an iterative interview that extracts the human's real
context instead of accepting the first vague answer. Each skill owns its *dimensions* (its persona's
questions); the *technique* is here. Its standalone form is the **`gather-context`** skill — the
pipeline's front intake phase and an on-demand "grill".

Goal: **shared understanding** — human and AI mean the same thing by the same words, so the doc is
what the human wanted built. That goal bounds the interview (see *Stop condition*), not a question
quota.

## The core loop

Not a questionnaire: **decide each next question from the last answer**, one level deeper on what
matters most, and let each answer reshape what is still open. Stop when nothing material is unknown —
not after N questions.

## Principles (non-negotiable)

- **One thread at a time — but batch the independent, already-sharp forks.** Take one dimension to
  the bottom before moving on. Forks that are *independent* and each reduce to a few options with a
  recommendation go together in one structured prompt (see *Choosing how to ask*); never batch one
  whose framing depends on an unanswered one.
- **Walk the decision tree in dependency order.** Settle the upstream decision first; never ask what
  an earlier answer already implies, or make the human guess about something not yet established.
- **Always offer your recommended answer** with one line of why, so the human can affirm with a word
  ("yes" / "yes, but X"). Take a position, not a menu of equal options.
- **Self-answer from evidence before asking.** If the repo, the prior phase's research doc, the brief
  or light research answers it, read it and ask only to confirm: "The brief says X, so I'm assuming Y
  — correct?"
- **Push past the first answer.** A generic answer ("users", "make it fast") gets a follow-up that
  forces a name, a number or a concrete example.
- **Surface ambiguity by imagining the alternatives.** Generate two or three readings of an
  underspecified point; if they lead to *different* products, ask the question that splits them
  (ideally as one structured question's options); if they converge, don't ask.
- **Mirror back to confirm shared understanding.** Periodically restate what you've heard for
  correction; name contradictions out loud ("earlier you said X, now Y — which holds?").
- **Cover, then stop.** Track coverage against this phase's dimensions; don't over-grill a settled
  point or chase detail that won't change the doc.

## Choosing how to ask (the mechanism)

- **Closed fork (a few options) → `AskUserQuestion`.** Your pick first, labelled `(Recommended)`,
  one-line consequence per option. Leave room for free-form: "you decide" and "not relevant to this"
  are valid answers.
- **Batch the independent forks** — up to four questions per `AskUserQuestion` call. Keep
  *dependent* forks in separate, ordered calls.
- **Open-ended thread → prose.** When a dimension needs a story ("walk me through how you do this
  today"), ask in conversation and follow up; a structured prompt would force a false
  multiple-choice.
- **`autopilot` doesn't prompt.** Resolve every fork yourself and log it (below); `AskUserQuestion`
  is for the interactive interview only.

## Stop condition (shared understanding reached)

Stop when **no material unknown remains** — nothing open would change what this phase writes. Give a
short **summary of the shared understanding** in the human's terms for final confirmation, then
proceed. Unknowns the human can't answer become forks (`Needs human confirm? = yes`), not invented
certainty. Name what you deliberately did **not** ask and why.

## Read the brief first

At intake every phase reads **`.dev-skills/project-spec/project-brief.research.md`** (the dossier
from `gather-context`), if present. Two classes of input:

- **Intent & constraints** (goal, audience, scope, budget, timeline, platforms, compliance, hard
  requirements) are **settled input** — confirm and build on them, don't re-ask. (Settled *intent*,
  not *truth*: `validate-idea` still pressure-tests its claims.)
- **Developer preferences** (the "Preferences & taste" priors — stack & libraries, code style &
  idioms, design taste, dev tooling, architecture leanings) are **soft priors**: bias the fork toward
  them as a **tie-breaker among options that already satisfy this phase's requirements/scenarios**.
  A requirement or scenario always wins; a preference never short-circuits the requirements-first
  step. Log every preference that influenced a decision in the `## Forks / Decisions log` with
  `Source = preference`; when you override one, record why.

## When the repo already has code

There is **no separate brownfield mode** — no config flag, no front phase, no parallel vocabulary;
just "self-answer from evidence before asking" pointed at a repository:

1. **Look before you ask.** At intake, check whether the repo holds real code (a dependency manifest
   plus source outside docs/config). If so, read what *this phase* needs — surfaces and routes for
   features, routing for flows, manifests and configs for the stack, UI dependencies for the design
   direction. Never make someone narrate their own codebase.
2. **Say what you found, in a few lines** — "I see Next.js + Postgres, 6 routes, `users`/`documents`
   tables, no tests." — so the user corrects you *before* you build on it.
3. **Confirm instead of re-asking.** "The code does X — keep it, or change it?"
4. **Keep the code's names by default.** Renaming is a deliberate user decision with refactor work
   attached — never a silent relabel in the spec.
5. **Record the differences in one place.** Where intent differs from what's built, add a line to the
   doc's `## Divergences (code vs intended)` section: what the code does now · what's wanted ·
   change / removal / not built yet. `plan-development` turns that list into tasks.

Otherwise the same stages, outputs and gates. In an empty repo none of this applies and the section
stays out of the document.

## Escalate to `gather-context` when a fork blocks understanding

When a fork is blocked on context only the human holds (not answerable from the docs) and resolving
it wrong would derail the phase, **invoke the `gather-context` skill scoped to that fork** (Skill
tool) for a focused mini-interview; fold the answers into the draft + Forks / Decisions log and
continue. Real blockers only — not a substitute for per-thread questions. Not in autopilot (see
below).

## Mode behavior

- **interactive** — interview the human by the loop and principles above.
- **autopilot** — **walk the same decision tree yourself**: pose each question, answer it from the
  brief + prior docs + research + best judgment, and **log every answer in the
  `## Forks / Decisions log`** with options, choice, rationale, confidence and source. Mark
  low/medium confidence, or material downside if wrong, as `Needs human confirm? = yes` so it
  surfaces in the human summary. Autopilot changes *who answers*, never *whether it's asked and
  recorded*.
- **on-demand `gather-context`** (the user invokes the grill directly) is always interactive,
  whatever the pipeline mode.

## What the phase does with the answers

The interview **feeds the draft** — no separate file (except `gather-context`'s own brief, a kept
artifact). Settled decisions go into the phase's `## Forks / Decisions log` (see
`output-format.md`); unresolved ones go to `## Open questions` and the human summary.
