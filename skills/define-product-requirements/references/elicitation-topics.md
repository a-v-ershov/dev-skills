# Elicitation topics (define-product-requirements)

The full Stage 1 topic catalogue. Read it when you reach the stage; the `SKILL.md` carries the
shape, the order and the ceiling.

---

## Stage 1 in full
**Interview technique — `../../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it. Work
the product definition across the dimensions below:
1. **Audience** — primary persona (role, context, the job they hire this product to do);
   segments (primary / secondary / explicitly-not); jobs-to-be-done in the user's words.
2. **Features (committed scope)** — the full set being built, **at most 15**. For each: short name +
   one-line capability + the validated need it serves (traceability) + **at least one acceptance
   criterion** (behavioral, testable — Given/When/Then or EARS; the feature-level definition of done,
   an observable outcome, never implementation detail). Group by capability area. Do NOT rank, tier,
   or defer. Challenge anything that traces to nothing — fold it in properly or drop it.
   **Then count.** Over 15: first fold variants and sub-capabilities into the feature they belong to
   (the detail survives as acceptance criteria, nothing is lost), then cut what serves no validated
   need or isn't table-stakes into `## Non-goals`. Still over 15 after both passes, the wedge itself
   is too wide — say so plainly: interactive, put the choice to the user (narrow the wedge, or accept
   a bigger scope and say so); autopilot, cut to the 15 that serve the validated need best and log
   the cut as a fork with `Needs human confirm? = yes`. Never go past 15 silently.
3. **Domain model & glossary** — the core entities the product is about (each: name, the data it
   owns, key relationships) and a glossary of domain terms in one canonical vocabulary. This is the
   *conceptual* model (product concepts), NOT a database schema — the physical schema belongs to
   `design-architecture`. Every feature, and later every flow, refers to these names. An entity a
   feature needs but the model lacks is a gap to close here.
4. **Success metrics** — per goal: signal, target (a number), how measured. Tie to the business
   model where relevant.
5. **Product constraints & non-goals** — budget/timeline/team, platforms/devices, compliance,
   hard non-negotiables, key assumptions; non-goals as scope boundaries (not deferred features).
   Note raw technical expectations (e.g. "must feel instant") to carry forward — do not decide
   architecture here.

- **interactive:** ask, one dimension at a time; challenge weak features in prose.
- **autopilot:** answer each from the validation doc + (stage 2) research + best judgment; record
  every choice in the Forks / Decisions log (especially each feature in-or-out decision) with
  rationale, confidence, source. Mark uncertain ones `Needs human confirm? = yes`.
