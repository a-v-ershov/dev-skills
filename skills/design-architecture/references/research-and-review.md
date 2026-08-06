# Research topics and reviewer probes (design-architecture)

Read the relevant half at the stage that needs it; the `SKILL.md` carries only the ranking rule.

## Research topics (Stage 2)

Now that the scenarios exist, verify the candidate technologies that could realize each capability:

- a tool's **current** capabilities;
- pricing & limits at the stated scale;
- maturity / production-readiness;
- deprecations or renames;
- managed-platform coverage — which roles it really collapses;
- independent benchmark claims;
- lock-in / portability facts, against a portability or compliance scenario;
- **for the hosting shortlist — current prices, free-tier ceilings, regions, and reachability /
  payment for the stated audience.** This is the fastest-moving set of facts in the phase, so it
  usually deserves the budget more than a framework comparison does.

Hold vendor metrics to the fact-type standard in
**`../../_shared/spec-pipeline/research-method.md`**: attribute them, never present them as
independent measurement. Carry findings and source links into the options.

## What the reviewer probes (Stage 4)

- a tool choice not justified by a scenario;
- a pricing / limit / "scales to N" claim with no source, or a weak one;
- lock-in that violates a portability or compliance scenario;
- a component tracing to nothing;
- over-engineering — premature microservices, needless datastores;
- a cost estimate that busts the budget scenario.

On **deployment**: no hosting decision at all; a platform that contradicts the stated audience,
residency or payment constraints; a monthly cost that ignores the paid tier the scale forces; no
backup-and-restore path where data loss was called painful; a manual-setup item assumed rather than
listed.

On **measurement**: a committed success metric no component can produce; a third-party analytics tool
where the product's own database already answers the question; user data sent to a third party that
the residency decision forbids.

On **security**, for a security-sensitive product: a missing threat model, an identified threat with
no mitigation, or a trust boundary that doesn't actually hold.

---

## Stage 1 in full
**Interview technique — `../../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at a
time, a recommended answer on every question, push past the first answer, mirror back to confirm. When
a fork is blocked on context only the user holds, invoke `gather-context` scoped to it.

1. **Quality-attribute scenarios.** Force each into concrete, testable form (source → stimulus →
   environment → response → **measure**) across performance/latency, scale/capacity, cost,
   security/privacy, **data residency & compliance**, reliability/availability,
   maintainability/operability. Assign priorities. This rubric judges every later choice.
2. **Operating context (where it will actually run).** Hosting is an architecture decision, not a later
   chore: it bounds which components are even available, and reversing it is a migration with the data
   attached. Ask for **measurable things and never for the project's status** ("is this a real
   project?" is unanswerable and predicts nothing), and never infer a compliance requirement instead of
   asking. Question set, reasoning and traps: **`operating-context.md`** (part 1).
3. **Measurement (how success will be observed).** `product-requirements` committed to success metrics;
   decide here what actually produces them, or they stay aspirations. Order it **question → metric →
   event**, never the reverse — and for a small product the product's own database usually answers
   most of them, with no third-party tool. Question set + traps:
   **`operating-context.md`** (part 2).
4. **Logical capabilities.** Decompose the system into the capabilities it needs (accounts & auth, core
   data, background jobs, file storage, notifications, **analytics/telemetry**…). Name each
   responsibility + the data it owns. Treat them as logical roles — stage 3 may merge several under one
   platform or split one apart. Cut any capability tracing to neither a flow nor a scenario.

- **interactive:** ask, one dimension at a time; do not let the conversation jump to tools here.
- **autopilot:** derive scenarios/capabilities from the spec + best judgment; log each material
  assumption (e.g. an inferred scale target) in the Forks / Decisions log with confidence. Mark
  uncertain ones `Needs human confirm? = yes`.

---

## Stage 3 in full
Per significant component, present **2–3 integrated options** (structure + concrete tool), evaluate
each against the component's scenarios and the stage-0 constraints (satisfies / strains / cost / ops
burden / lock-in) using the stage-2 facts, and **recommend one**; note where an option collapses or
splits roles. A **stack or architecture preference** from the brief is a **tie-breaker among options
that already satisfy the scenarios** — never a reason to skip a scenario or pick a strained option; log
it as a fork with `Source = preference`.

Then assemble the whole: component map, sync/async boundaries, trust boundaries, the primary flow
traced end-to-end, and a cost & risk sanity check against the budget scenario (busts the budget or the
team can't run it → revisit the options).

**Deployment and analytics are components too**, decided the same way — hosting options weighed against
the stage-1 operating context with their **own ADR**, plus environments, domain, secrets, backups + a
tested restore and the **manual setup checklist**; and which metrics the own database answers vs what
needs a client counter ("none — the database is enough" is a legitimate outcome), how errors surface,
what user data leaves. Both, with their traps: **`operating-context.md`**.

**If the product is security-sensitive**, run the **STRIDE-lite threat model** over that component map
and trust boundaries and feed each mitigation back into the design and the affected ADR (threat-model
section of `architecture-template.md`); otherwise record that you skipped it and why.

Write an **ADR** for each significant, hard-to-reverse decision (`adr-template.md`, numbered
`adr/0001-<slug>.md`). Draft `architecture.research.md` from `architecture-template.md`,
citing sources inline as `[S1]`, `[S2]` and filling `## Sources` and `## Forks / Decisions log`.

---

## Stage 0 in full
Read `user-flows.research.md`, `product-requirements.research.md`, `design-decisions.research.md`, and
`project-brief.research.md` if present (original intent, constraints, and developer preferences as soft
priors). State in one paragraph what the system must do, and list the constraints that bound the
technology choice: product constraints + raw technical expectations (budget, platforms, compliance,
"must feel instant", "data stays in EU"); the **design decisions that carry technical weight**
(media-heaviness, offline/connectivity, realtime UI, target platforms — each becomes a scenario
below); the **adopted UI kit / icon set** if design-decisions named one (a settled dependency — honor
it, don't re-open it); the **committed success metrics** (they drive the measurement dimension); plus
**team skills/size** and **existing investments**. List the gaps. If `user-flows.research.md` or
`design-decisions.research.md` is missing, say so and offer `/create-user-flows` /
`/define-design-decisions` first. Read the mode.
