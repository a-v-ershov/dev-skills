---
name: demo-spec
description: "Webinar DEMO variant of the spec pipeline — a fast, shallow PRD grill for live before/after demos, NOT the real create-project-spec. Use only for the vibe-coding course demo: it interviews the user with a handful of sharp, on-screen questions and writes a SLIM spec set (product requirements + architecture + dev-architecture) in ~5–15 minutes instead of hours. It deliberately skips the heavy machinery the real pipeline runs — no gather-context/validate-idea/user-flows/design phases, no research subagents, no adversarial review, no dual-output-per-phase. The point is to SHOW the grill (Claude interrogating the idea) versus a naive one-line 'make me a plan' prompt. Produces the same filenames the build/release demos read, so the three acts chain."
argument-hint: "[one-line idea]"
---

# Demo Spec Skill (webinar variant — SHALLOW ON PURPOSE)

You are running the **demo** version of the spec phase for a live webinar. Your job is to make the
**before/after** land: the "before" is a co-host typing *"make me a plan for an SEO article service"*
into a cold chat and getting a vague wall of text; the "after" is **you interrogating the idea** with
a few sharp questions and turning it into a slim but real spec. The interrogation IS the demo — keep
it visible, pointed, and fast.

This is **not** `create-project-spec`. You skip everything that makes the real pipeline take hours.
Say so out loud at the end so the audience knows the real thing is deeper.

## Language

Respond and reason in whatever language the user addressed you in — ask questions and write the docs
in that language. Never translate code, identifiers, paths, commands, or API names.

## Hard bounds (do not exceed — this is a timed demo)

- **~3–6 questions total**, across the whole run — not per section. Batch independent forks into a
  single `AskUserQuestion` call (up to 4 at once). Never run a long serial interview.
- **No subagents.** No research agent, no adversarial-review agent, no `spec-reviewer`. You draft
  directly.
- **No sibling phases.** No `gather-context`, `validate-idea`, `create-user-flows`,
  `define-design-decisions` as separate steps. Fold the essentials inline.
- **Target ~5–15 minutes wall-clock.** If a thread is going deep, cut it and log it as an open
  question instead of chasing it.

## Interview technique (borrow the style, not the depth)

Use the *style* from `../_shared/spec-pipeline/elicitation-method.md` — **always offer a recommended
answer** with one line of why (so the user affirms with a word), push once past a vague first answer,
mirror back briefly — but run it **shallow**: cover each dimension with one good question, take the
recommendation if the user shrugs, move on. You are demonstrating that the tool *interrogates*, not
running the full grill.

## The three dimensions to cover (briefly, in one or two batched prompts)

Cover all three so the spec is real and the later demo acts have something to read — but one pass each.

1. **Product requirements** — the core feature list (3–6 features) + one testable acceptance
   criterion each + who it's for in one line. This is what makes the "before" (a vague blob) look
   thin next to a committed, checkable feature set.
2. **Architecture** — the stack, the 2–4 key components, and where the **trust boundaries** are
   (what's user-facing, where secrets live, what talks to external APIs). Include a 3–5 line
   **STRIDE-lite threat model** — it's the contract `demo-release`'s `audit-security` reads, so the
   deploy-checklist act has something to check against.
3. **Dev-architecture (the inner loop)** — the tools that let the AI **verify its own work**: for a
   web service that's a dev server + Playwright to drive the UI + `make check`; for a script it's unit
   tests + a runner. Name the concrete commands. This is the setup the **build+verify** demo act pays
   off — call that out.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Frame — restate the idea in one sentence; say plainly this is the fast DEMO spec, not the full pipeline
- [ ] Stage 1: Grill — 3–6 sharp questions (batched), recommended answer on each, covering the three dimensions
- [ ] Stage 2: Draft — write the three slim docs under .buildloop/project-spec/ (no review, no research agents)
- [ ] Stage 3: Close — summarize the shared understanding + say what the REAL pipeline would add on top
```

### Stage 0: Frame
Restate the idea (from the argument or ask for it) in one concrete sentence and confirm it. Say, in one
line, that this is the **demo** spec: fast and shallow, and the full `create-project-spec` goes much
deeper (research, adversarial review, more phases). This framing is part of the honest before/after.

### Stage 1: Grill
Run the shallow interview above. Prefer **one or two `AskUserQuestion` calls** with the recommended
option first and a one-line consequence on each. Keep each question pointed — the audience should see
Claude catching an ambiguity the naive prompt glossed over (auth? who owns the data? what does "done"
mean for feature X?). Stop as soon as the three dimensions are covered well enough to draft.

### Stage 2: Draft (slim — the same filenames the demo build/release read)
Create `.buildloop/project-spec/` if absent (drop a `.buildloop/project-spec/.gitignore` with
`*.review.md` if creating the dir). Write three **short** docs — each is a tight section list, not the
full research template:

- **`product-requirements.research.md`** — the feature list with one Given/When/Then acceptance
  criterion each, the audience line, and a one-line domain note. This is the artifact the build act's
  task traces to.
- **`architecture.research.md`** — the stack, the key components, the trust boundaries, and the
  3–5 line STRIDE-lite threat model (assets → threats → mitigations). `demo-release`'s `audit-security`
  reads this as its contract.
- **`dev-architecture.research.md`** — the inner loop: the exact run/drive/prove commands the AI uses
  to check its own work. Keep it concrete (real commands), because the build+verify act relies on it.

Keep each doc to what a reader scans in under a minute. Cite nothing; run no reviewer.

### Stage 3: Close
Give a short shared-understanding summary in the user's terms. Then state plainly what the **real**
pipeline would add that this demo skipped — research with cited sources, an adversarial self-review per
phase, `validate-idea`, `create-user-flows`, a design system — and that a full spec takes hours, not
minutes. Point at the three files. Do **not** start building.

## Rules

1. Shallow by design — 3–6 questions total, no subagents, no sibling phases, ~5–15 min.
2. Always offer a recommended answer; batch independent forks; push once past a vague answer, then move on.
3. Write the three slim docs under the **real filenames** so the build/release demo acts can read them.
4. Include the trust boundaries + STRIDE-lite note in architecture — it's the deploy-checklist's contract.
5. Name concrete verification commands in dev-architecture — the build+verify act depends on them.
6. Close by naming what the full pipeline would add — keep the before/after honest.
