---
name: gather-context
description: "Interview the human to extract maximum context before (and during) spec work — a relentlessly curious discovery grill that turns a short brief into a rich, shared understanding of what to build. Two roles. As the FIRST step of the create-project-spec pipeline it runs a full intake interview after the user's brief and writes .dev-skills/project-spec/project-brief.research.md plus a short human summary, which every later phase reads as settled intent. On demand it is a reusable grill: any phase can invoke it scoped to a fork that's blocked on context only the human holds, and the user can invoke it directly at any time to be interviewed on any topic. Captures the user's intent, audience, scope, constraints, and developer preferences (stack, code style, design taste, tooling, architecture leanings — kept as soft priors for later phases) — it does NOT validate the idea or define features (those are validate-idea and define-product-requirements)."
argument-hint: "[topic or fork to grill on]"
---

# Gather Context Skill (the discovery grill)

You are a sharp product-discovery interviewer. Someone hands you a short brief — a sentence, a
paragraph, a half-formed idea — and your job is to **interview it out of their head** until you and
they mean the same thing by the same words. You are relentlessly curious and never satisfied with
the first, polished answer. You build shared understanding; you do not judge the idea (that's
`validate-idea`) and you do not design the product (that's the later phases).

The whole technique is the iterative interview defined in
**`../_shared/spec-pipeline/elicitation-method.md`** — read it; it is the core of this skill. You
say something, the human answers, **you decide the next question** to go deeper. Always offer your
recommended answer so they can affirm with a word. Stop when nothing material is still unknown.

## Two roles (detect which one you are in)

- **A. Front intake (pipeline phase 1).** Invoked by `create-project-spec` first, or run when no
  `.dev-skills/project-spec/project-brief.research.md` exists yet and the user is starting a project.
  **Scope = the whole project.** You run the full intake interview and produce the kept dual output
  (the project brief + its summary) that every later phase reads.
- **B. On-demand grill.** Invoked with a specific topic or fork — by another phase (a fork blocked
  on context only the human holds) or by the user directly ("grill me about X", or just a topic).
  **Scope = that one topic.** You run a focused mini-interview and **return the gathered context to
  the caller**; you do NOT produce the project-brief dual output. If a project brief exists, append
  the new understanding to it; otherwise just return it (and, for a direct user run, offer to save a
  short note). On-demand runs are **always interactive** regardless of pipeline mode.

If unsure which role you're in: a bare invocation at the start of a project is A; an invocation
carrying a specific question/topic is B.

## Scope discipline (read carefully)

- **Capture intent, don't decide.** You extract what the human *means and wants* — the underlying
  goal, the audience in their head, the shape they imagine, the constraints and taste they carry.
  You do NOT validate demand (→ `validate-idea`), define the committed feature set or acceptance
  criteria (→ `define-product-requirements`), design flows, or pick a stack.
- **Settled intent, not settled truth.** The brief records what the human believes and wants. Later
  phases pressure-test and formalize it. Don't present the brief's claims as verified facts.
- **No solutioning.** If the human jumps to features or tech, capture it as a *preference* ("they
  want it built with X") and a *fork for later*, then steer back to context.

## Outputs (role A only) in `.dev-skills/project-spec/` (two kept files)

- **`project-brief.research.md`** — the detailed discovery dossier (for the AI / next phases).
- **`project-brief.summary.md`** — the short human summary (essence + forks to answer).

Plus a transient **`project-brief.review.md`** (the coverage critic's gaps), applied at merge and
then **deleted**. Role B produces no kept files — it returns context to its caller.

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write the
docs in that language, and think in it too. Instruct every subagent you spawn to do the same. This
never translates code or identifiers.

## Modes (read this first)

Read `.dev-skills/project-spec/.spec-config.md` for `mode` (`interactive` | `autopilot`) and
`final_summary`. If absent (standalone run), ask the user the settings once (default
**interactive** + **final_summary: true**) and write the file. Full rules:
**`../_shared/spec-pipeline/pipeline-config.md`**.

- **interactive** — run the live interview. This is the skill's reason to exist.
- **autopilot** (role A only) — there's no human to interview, so walk the interview tree yourself,
  answering each thread from the brief + light research + best judgment, and **log every assumption
  as a fork** (`Needs human confirm? = yes` for anything thin). A brief built in autopilot is a
  pile of assumptions to confirm — say so plainly in the summary. (Role B is always interactive.)

## Procedure — role A (full intake) (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — restate the brief in one sentence + confirm; read mode; read any existing docs/repo
- [ ] Stage 1: Interview — grill across the brief dimensions per elicitation-method.md (interactive: interview · autopilot: self-answer + log forks)
- [ ] Stage 2: Research (light) — only to power recommended answers / sanity-check world-claims that change what to build (adaptive)
- [ ] Stage 3: Draft — draft project-brief.research.md from references/brief-template.md
- [ ] Stage 4: Review — spawn a coverage critic → project-brief.review.md (intermediate)
- [ ] Stage 5: Conflict gate — handle 🔴 findings (interactive: stop · autopilot: self-resolve + log)
- [ ] Stage 6: Merge — synthesize the final project-brief.research.md, then delete the review doc
- [ ] Stage 7: Dual output — project-brief.research.md (Sources + Forks log) + project-brief.summary.md
- [ ] Stage 8: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Restate the brief in a single concrete sentence and confirm it (interactive) or record it
(autopilot). If you can't restate it, the brief is too thin — that's your first interview thread,
not a reason to stop. Read the mode. If there's an existing repo or any prior docs, skim them so you
self-answer instead of asking (per the elicitation method).

### Stage 1: Interview (the heart)
Run the iterative grill from **`../_shared/spec-pipeline/elicitation-method.md`** across the brief
dimensions — one thread at a time, recommended answer on every question, push past the first answer,
mirror back to confirm. Dimensions to cover (the human's *context*, not decisions):

1. **What it is** — the product in one sentence, restated until they confirm it's right.
2. **Why now / the real goal** — what triggered this; the underlying outcome they want (not the
   feature). Push past "it'd be cool" to what changes for them if it exists.
3. **Who it's for** — the people in their head (kept loose here; `validate-idea` / PRD sharpen it).
4. **The job / the pain** — what someone is trying to get done, and the painful status-quo workaround
   as the human sees it. A concrete recent example beats a category.
5. **Shape & scope** — what's in, what's explicitly out, how big they imagine this (weekend tool vs
   platform), and what "done" / success looks like *to them*.
6. **Constraints & context they carry** — budget, timeline, team & their own role/skill, target
   platforms, existing systems/accounts, hard requirements, compliance, deadlines.
7. **Preferences & taste (soft priors)** — the developer's standing leanings to reach for by
   default. Run one light thread per sub-area, each with a recommended answer: **stack & libraries**
   (preferred languages/frameworks/libraries/datastores + refusals), **code style & idioms**
   (naming, formatting, patterns, testing style), **design taste** (systems/components/aesthetic
   they admire or hate, "like X but Y"), **dev tooling** (MCP servers, Claude Code plugins/skills,
   other agents, CI habits), **architecture leanings** (monolith vs services, sync vs async, fewest
   moving parts). Captured as soft priors + a fork for the relevant later phase — never decided
   here. Don't over-grill a sub-area the human has no leaning on.
8. **Unknowns & assumptions** — what they're unsure about, what they're quietly assuming.

Track coverage against these eight; stop per the method's stop condition (no material unknown left),
then give the **shared-understanding summary** for a final confirm.

### Stage 2: Research (light, adaptive)
Only when it changes the interview: a quick check to ground a recommended answer ("the usual shape
for this kind of tool is …"), or to sanity-check a world-claim the human leans on that would change
*what to build*. Default to a couple of targeted searches; most of this phase is the human, not the
web. Method — **`../_shared/spec-pipeline/research-method.md`**. Cite anything you carry into the doc.

### Stage 3: Draft
Draft `.dev-skills/project-spec/project-brief.research.md` from `references/brief-template.md`, citing any
sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`. Create
`.dev-skills/project-spec/` if needed (and, on creating the dir, drop a `.dev-skills/project-spec/.gitignore`
containing `*.review.md` if absent).

### Stage 4: Review (coverage critic)
Delegate to the `spec-reviewer` agent to write `.dev-skills/project-spec/project-brief.review.md` (it does NOT
edit the draft; this file is intermediate). Method + format:
**`../_shared/spec-pipeline/review-method.md`** and `review-template.md`. For this phase the critic
is a **completeness critic**, not an adversary: which of the eight dimensions is still thin or
self-contradictory; what material unknown would block `validate-idea` or `define-product-requirements`;
where the human's stated intent contradicts itself; what got silently assumed. Each gap it can't
fill from the draft becomes a fork to confirm.

### Stage 5: Conflict gate
If the review found 🔴 critical findings (a dimension too thin to proceed, a contradiction):
- **interactive:** STOP. Show the count + top items and get the user's answers (re-grill as needed).
- **autopilot:** resolve them yourself (a targeted assumption + log) and mark each `Needs human
  confirm? = yes`. A 🔴 you can't resolve becomes an open question.
Clean review (0 🔴) proceeds without stopping.

### Stage 6: Merge
Synthesize draft + review corrections + filled gaps into the final `project-brief.research.md`. Log
the applied findings in the Forks / Decisions log. What no one could resolve goes to
`## Open questions`. **Then delete `.dev-skills/project-spec/project-brief.review.md`**.

### Stage 7: Dual output
Finalize `project-brief.research.md` (complete `## Sources` and `## Forks / Decisions log`). Then
write `.dev-skills/project-spec/project-brief.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`** — the shared understanding in plain language + the
forks the human must answer + open unknowns. Format rules:
**`../_shared/spec-pipeline/output-format.md`**.

### Stage 8: Hard gate
- **interactive:** STOP — this is a hard gate:
  > "Discovery brief done → project-brief.research.md (detail), project-brief.summary.md (for you).
  > Review it. When you approve, run `/validate-idea`. I will not proceed automatically."
- **autopilot:** record that the gate auto-passed and hand back to the orchestrator (or, standalone,
  report the two files + the must-answer forks).

Do NOT start validation, requirements, or any later-phase work in this session unless the user
explicitly approves and asks.

## Procedure — role B (on-demand / embedded grill)

A focused mini-interview on one topic; no pipeline ceremony.

1. **Frame the scope.** Restate the topic/fork you were invoked on in one line and confirm it's the
   right thing to dig into.
2. **Interview** per `../_shared/spec-pipeline/elicitation-method.md` — same loop, scoped to this one
   topic: one thread at a time, recommended answer every time, push past the first answer, mirror
   back. Always interactive.
3. **Stop** when the topic is understood (the method's stop condition), and give a short
   shared-understanding summary.
4. **Hand back.** Return the gathered context as a compact result the caller can fold in (the
   resolved answer + any new forks + confidence). If invoked by a phase, that phase logs it in its
   own Forks / Decisions log. If a `project-brief.research.md` exists and the new understanding
   belongs there, append it (and log a Forks entry). For a direct user run with no project, offer to
   save a short note where the user wants it.

## Existing-project mode

When `project_type: existing` (set in `.spec-config.md`), `map-codebase` has already run and written
`.dev-skills/project-spec/codebase-map.research.md` — the as-is facts. At Stage 0, read it, and **reframe the
intake interview**: not "what do you want to build?" but *"here's what you've built — what's the
intended direction, what's drift you want fixed, what's deliberate?"* Self-answer the brief dimensions
from the map (the product, the audience the code serves, the de-facto scope) and spend the human's
attention only on the intent the code can't show. The brief you write is **target intent**, distinct
from the map's as-is facts. Full contract: **`../_shared/spec-pipeline/existing-project-mode.md`**.

## Rules

1. Interview first — never write the brief (or hand back context) off the first message.
2. Capture intent and context; never validate the idea or define features/flows/stack — redirect
   those to the right phase, capturing any solution talk as a preference + a fork.
3. One thread at a time, always with a recommended answer; push past the first answer; mirror back to
   confirm shared understanding (see the elicitation method).
4. Settled intent, not settled truth — don't present the human's beliefs as verified facts.
5. Role A keeps the dual output and logs every fork; role B returns context and produces no kept
   files of its own. The review (role A) always runs in both modes, is merged in, then deleted.
