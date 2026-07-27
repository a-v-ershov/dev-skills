---
name: demo-spec
description: "Webinar DEMO variant of the spec pipeline — the REAL staged flow (gather-context → product requirements → architecture → dev-architecture), just compressed, NOT the full create-project-spec. Use only for the vibe-coding course demo. It runs four real, SEQUENTIAL stages with an approval gate between each: (1) gather-context interviews the user AND critically pushes back on what they propose; (2) it drafts the functional/product requirements and stops for ok/not-ok; (3) it proposes an architecture (options + trust boundaries) and stops for ok/not-ok; (4) it proposes the dev-architecture (the verification tooling — e.g. Playwright — the build act later uses) and stops. Shorter than the real pipeline (no research subagents, no adversarial-review subagents, no dual outputs, drops validate-idea/user-flows/design phases) but keeps the staged, gated, critical structure. Writes the same filenames the build/release demos read, so the three acts chain."
argument-hint: "[one-line idea]"
---

# Demo Spec Skill (webinar variant — REAL stages, compressed)

You are running the **demo** version of the spec phase for a live webinar. The point of the
before/after is NOT "fewer questions" — it's that the method has **real stages with gates**: it
interviews you, pushes back on weak ideas, then walks *requirements → architecture → dev-architecture*,
stopping at each so you can say **ok / not-ok** and correct it. The "before" (a co-host getting one
vague blob from *"make me a plan"*) has no stages, no pushback, no gates. That contrast is the demo.

This is **not** `create-project-spec`. You compress it: no research subagents, no adversarial-review
subagents, no dual outputs, and you drop `validate-idea` / `create-user-flows` / the design phases. But
you **keep the four real stages and the gate between each** — that structure is exactly what you're
demonstrating. Do **not** collapse it into one batch of questions and a single file write.

## Language

Respond and reason in whatever language the user addressed you in — ask questions and write the docs
in that language. Never translate code, identifiers, paths, commands, or API names.

## Shape (what stays, what's cut)

- **Stays (the demo):** four sequential stages, each ending in a **hard gate** — you present what you
  produced and STOP for the user's ok/not-ok, applying edits before moving on. Critical persona in the
  interview: take positions, name weak assumptions, propose better framings.
- **Cut (for time):** research subagents, the `spec-reviewer` adversarial pass, the `*.summary.md`
  dual output, and the phases `validate-idea` / `create-user-flows` / `define-design-decisions` /
  `define-design-system`. Each stage is **one focused round**, not the full research+review machine.
- **Target:** a few minutes per stage. Shorter than the real pipeline — but never by skipping a stage
  or a gate.

Interview *style* comes from `../_shared/spec-pipeline/elicitation-method.md` — always offer a
recommended answer with one line of why, push once past a vague first answer, mirror back — applied
shallowly.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Frame — restate the idea in one sentence; say this is the compressed (not full) spec flow
- [ ] Stage 1: gather-context — interview + CRITICALLY push back → short shared-understanding recap → GATE
- [ ] Stage 2: product requirements — draft functional requirements → present → GATE (ok/not-ok, apply edits) → write doc
- [ ] Stage 3: architecture — propose approach (options + trust boundaries + STRIDE-lite) → present → GATE → write doc
- [ ] Stage 4: dev-architecture — propose the verification tooling (Playwright etc.) → present → GATE → write doc
- [ ] Close: recap + say what the full pipeline adds; hand off to demo-build
```

### Stage 0: Frame
Restate the idea (from the argument or ask for it) in one concrete sentence and confirm it. Say in one
line that this is the **compressed** spec flow — the same real stages as `create-project-spec`, minus
the slow research/review machinery and a few phases. This framing is part of the honest before/after.

### Stage 1: gather-context (interview + critical pushback)
Interview the user across a few dimensions — what it really is, who it's for, the core job, in/out of
scope, hard constraints. **Be critical, not a stenographer:** when they propose something, take a
position on it — name the weak assumption, the thing that won't work, or a sharper framing ("you said X;
that usually fails because Y — I'd do Z instead — agree?"). One or two `AskUserQuestion` rounds is
enough; each question with a recommended answer. Then give a **short shared-understanding recap** and
**GATE**: "Did I get this right? Correct me before I draft the requirements." Do not proceed until the
user confirms. (This is the compressed stand-in for `gather-context` — no kept brief file.)

### Stage 2: product requirements → gate → write
From the confirmed understanding, draft the **functional requirements**: 3–6 features, each with one
testable Given/When/Then acceptance criterion, plus the one-line audience/domain note. **Present them**
in the chat and **GATE**: "Here are the functional requirements — ok, or what do you change?" Apply the
user's edits. Only then write **`.dev-skills/project-spec/product-requirements.research.md`** (create the
dir + a `.dev-skills/project-spec/.gitignore` with `*.review.md` if absent). This is what the build act's
task traces to.

### Stage 3: architecture → gate → write
**Propose an architecture** — and where there's a real choice, offer 2 options with a recommendation
(e.g. "Next.js API routes vs a separate FastAPI service — I'd take the first because …"). Ask only the
architecture questions that actually change the design; don't re-interview. State the **stack, the 2–4
key components, the trust boundaries** (what's user-facing, where secrets live, what calls external
APIs), and a **3–5 line STRIDE-lite threat model** (assets → threats → mitigations). **Present** it and
**GATE** (ok / change what?). Apply edits, then write **`.dev-skills/project-spec/architecture.research.md`**.
The threat model here is the contract `demo-release`'s `audit-security` reads — keep it.

### Stage 4: dev-architecture → gate → write
**Propose the inner loop** — the concrete tools that let the AI **verify its own work**, since that's
what the build act pays off: for a web service, a dev server + **Playwright** to drive the UI + `make
check`; for a script, unit tests + a runner. Name the **exact run/drive/prove commands**. **Present** it
and **GATE**. Apply edits, then write **`.dev-skills/project-spec/dev-architecture.research.md`**. Call out
that these are the tools `demo-build`'s verifier will use to catch bugs.

### Close
Give a one-paragraph recap of the spec. State plainly what the **full** pipeline adds that this demo
skipped — cited research per phase, an adversarial self-review per phase, `validate-idea`,
`create-user-flows`, a design system, and the `*.summary.md` outputs — and that a real spec takes hours.
Point at the three files and hand off: `demo-build` builds the first feature next. Do **not** start
building here.

## Rules

1. **Keep the four real stages and the gate between each** — never collapse into one batch + one file.
2. Stage 1 is critical: push back on the user's proposals, don't just record them.
3. Every stage: **present, then stop for ok/not-ok**, apply edits before writing the doc.
4. Architecture offers real options with a recommendation; ask only design-changing questions.
5. dev-architecture names concrete verification tools (Playwright etc.) — the build act depends on them;
   architecture keeps the trust boundaries + STRIDE-lite — the release act depends on them.
6. Compress by cutting research/review/extra-phases, **not** by skipping a stage or a gate.
7. Close by naming what the full pipeline would add — keep the before/after honest.
