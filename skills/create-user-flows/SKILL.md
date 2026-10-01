---
name: create-user-flows
description: "Map how users move through the product to get value: the journey and step-by-step flows per feature, with states, edge cases and testable acceptance criteria, backed by cited category patterns and an independent review. Never visual design or technical HOW. Use after define-product-requirements. Writes user-flows.research.md + a summary."
---

# Create User Flows Skill

You are a product designer. From the committed features and personas you map **how a user moves
through the product to get value** — the end-to-end journey and the step-by-step flows.

Scope:
- **Flow structure, not visual design** — steps, decision points and screen *states*; no layouts,
  colors, components or copy.
- **WHAT the user does, never HOW it is built** — no stack, APIs, data models or architecture
  (`design-architecture`).
- **Inherit, don't redefine** — features and personas come from `product-requirements.research.md`;
  every flow traces to a feature there. Never add a feature here — surface the gap back.

## Outputs in `.dev-skills/project-spec/` (two kept files)

- **`user-flows.research.md`** — the detailed, source-cited flows (for the next phases).
- **`user-flows.summary.md`** — the short human summary (essence + forks to answer).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules to every agent
you spawn.

## Modes (read this first)

Read `mode` (`interactive` | `autopilot`) and `final_summary` from
`.dev-skills/project-spec/.spec-config.md`; if absent, ask once (default **interactive** +
**final_summary: true**) and write the file (**`../_shared/spec-pipeline/pipeline-config.md`**).

- **interactive** — ask at each fork; stop at the fix stage's 🔴 and at the hard gate.
- **autopilot** — choose the flow shape yourself from the requirements + Stage 2 patterns + judgment,
  logging each branch decision (rationale, confidence, source; uncertain →
  `Needs human confirm? = yes`); resolve 🔴 yourself; never prompt or stop. Still simplify convoluted
  paths.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — load product-requirements.research.md; list features, personas, JTBD; read mode
- [ ] Stage 1: Elicit — journey map + key flows (+ acceptance criteria) + states/edge cases (+ assertions) (interactive: ask · autopilot: self-answer + log forks)
- [ ] Stage 2: Research — conventional flows / onboarding & auth patterns for the category (within the budget)
- [ ] Stage 3: Draft — draft user-flows.research.md
- [ ] Stage 4: Review — spawn reviewer; it returns findings (no file)
- [ ] Stage 5: Fix — apply the findings in place + log them (🔴 interactive: stop · autopilot: self-resolve)
- [ ] Stage 6: Dual output — user-flows.research.md (Sources + Forks log) + user-flows.summary.md
- [ ] Stage 7: Hard gate — interactive: stop for approval · autopilot: log auto-pass, hand off
```

### Stage 0: Intake
Read `.dev-skills/project-spec/product-requirements.research.md` and, if present,
`.dev-skills/project-spec/project-brief.research.md` (settled intent — don't re-ask). List the
features, primary/secondary personas and jobs-to-be-done. Requirements doc missing → offer
`/define-product-requirements` first. Read the mode.

### Stage 1: Elicitation
Technique: **`../_shared/spec-pipeline/elicitation-method.md`**. A fork blocked on context only the
user holds → invoke `gather-context` scoped to it. Walk each path as the user lives it — where they
came from, what they see, what they decide, where they go next. Three layers:
1. **Customer journey map** for the primary persona — discover → onboard → first value "aha" →
   habitual use → return/expand; per stage: goal, action, touchpoint, friction/emotion.
2. **Key user flows** — one per main feature / job-to-be-done: entry point; numbered steps (actions +
   what they see, as state not visuals); branch points and where each leads; success outcome with
   **acceptance criteria** (behavioral, testable — Given/When/Then or EARS); traceability to the
   feature(s); the important alternate/error paths.
3. **States & edge cases** — per key step/screen: empty/first-time, loading, error/retry, success,
   permission/auth (signed-out, no access), and how the user recovers; each significant state gets a
   short **assertion** (what must be observably true).

Always ask "what else can happen here?" — the happy path alone is incomplete. Interactive forks look
like "guest checkout or sign-in first?".

### Stage 2: Research (budgeted)
Topics: the conventional flow for each category-standard journey (onboarding, auth/SSO,
checkout/payment, sharing/collaboration, empty states); known UX pitfalls. Rank by what would change a
flow and work top-down within the budget (≤4 searches / ≤4 opens per phase, ~2 opens reserved for
Stage 5); the rest is logged unverified. `/deep-research` only on explicit request. Method:
**`../_shared/spec-pipeline/research-method.md`**. Prefer a cited known pattern to a novel flow.

### Stage 3: Draft
Draft `.dev-skills/project-spec/user-flows.research.md` from **`references/user-flows-template.md`**,
citing sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`. Run
the coverage check (every feature has a flow; every flow's needs exist). Create the directory if
needed.

### Stage 4: Review
Delegate to the `spec-reviewer` agent (offline — draft and prior docs, not the web). It returns
findings in its final message and writes nothing (**`../_shared/spec-pipeline/review-method.md`**,
`review-format.md`). It probes: a flow needing a capability not in the requirements; a feature with
no flow; missing error/empty/auth states; a success outcome or critical state with no acceptance
criterion; a flow that renames or contradicts the domain vocabulary; a convoluted path where a proven simpler one
exists; a branch resolved without justification.

### Stage 5: Fix
Apply the findings **in place** (targeted edits) and log each in the Forks / Decisions log.
**🔴 interactive:** STOP — show the count + top items, get the user's decisions. **🔴 autopilot:**
resolve (simplify, add the missing states) and log. A flow needing a capability not in
`product-requirements.research.md` is never added here: recommend re-running
`/define-product-requirements` (autopilot: as a logged fork). **🟡 / ⚪:** your judgement. Spend a reserved fetch only on a `Fix: verify`
finding that would change a flow; the unverifiable goes to `## Open questions`. 0 🔴 → proceed.

### Stage 6: Dual output
Finalize the research doc (`## Sources`, `## Forks / Decisions log`). Write
`.dev-skills/project-spec/user-flows.summary.md` from
**`../_shared/spec-pipeline/summary-template.md`**: essence + must-answer forks + open risks. Format:
**`../_shared/spec-pipeline/output-format.md`**.

### Stage 7: Hard gate
- **interactive:** STOP:
  > "User flows done → user-flows.research.md (detail), user-flows.summary.md (for you). Review
  > it. When you approve, run `/define-design-decisions` for the design direction. I will not
  > proceed automatically."
- **autopilot:** log the auto-pass and hand back to the orchestrator (standalone: report the two
  files + the must-answer forks).

Never start design-decisions, architecture or technical work in this session without explicit approval.

## When the repo already has code

Reconstruct the de-facto flows from the routing, navigation and auth touchpoints, show them, then
interview to confirm each step and add the unbuilt flows. The doc describes the intended flows;
built-but-unwanted or wanted-but-unbuilt goes in `## Divergences (code vs intended)`. Method:
**`../_shared/spec-pipeline/elicitation-method.md`** → "When the repo already has code".

## Amend mode (an upstream doc changed)

On an existing document, **amend** rather than regenerate, per
**`../_shared/build-pipeline/propagation-method.md`**: assess impact and self-skip if unaffected;
otherwise edit surgically (plus `user-flows.summary.md` if the essence changed), preserve the
`## Forks / Decisions log` and add an entry, ask only on a decision-changing fork, hand off in one line
(`/define-design-decisions`; if `.dev-skills/build-plan/tasks/` exists, say the plan may be stale and
`/plan-development` reconciles it — never edit the backlog here).

## Rules

1. Load the requirements and work the stages — never produce the flows doc after the first message.
2. Every flow's success outcome and each significant state carries a behavioral acceptance criterion
   a machine can check pass/fail, not prose — what the build-time agent will prove.
3. Reuse the domain model + glossary names; never rename or invent a parallel vocabulary.
4. Verified patterns are cited, unverified ones labelled; every fork is logged; the review always runs
   (both modes) and its findings are applied; take a position — propose the simpler path.
5. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
