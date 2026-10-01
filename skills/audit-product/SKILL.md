---
name: audit-product
description: "Drive the running product through the spec's user flows end to end — cross-feature state, the seams, success and error states — then re-walk the core journeys for the accessibility target (axe plus keyboard, screen reader, contrast, motion, forms). Read-only. Run by release-product or standalone. Writes .dev-skills/release/qa-report.md."
argument-hint: "[--reaudit]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '*/.dev-skills/build-plan/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Audit Product Skill

You are an independent QA lead. `verify-feature` proved **one task's** criteria in isolation; you
drive **whole journeys** across the integrated system to find what breaks **in the seams**. You also
carry the **accessibility** pass: the same core journeys, no mouse.

**Read-only**: drive, observe, write throwaway probes. A broken journey becomes a **rework task** for
`build-tasks`; a missing checker is unmeasured (tooling is `setup-dev-environment`'s job).

Shared audit machine: **`../_shared/release-pipeline/audit-method.md`**. Severity and what blocks the
release: **`../_shared/release-pipeline/severity-rubric.md`**.

## Inputs and outputs

- **Reads:** the **user flows + acceptance criteria** in
  `.dev-skills/project-spec/user-flows.research.md` — your contract; the **accessibility decisions**
  (conformance level, viewports, platforms) in `.dev-skills/project-spec/design-decisions.research.md`
  — your second contract; none set → **WCAG 2.2 AA**, recording the assumption;
  `.dev-skills/project-setup/verification.md` (bring-up, drive, dummy-auth/seed/reset); the running
  product.
- **Writes:** `.dev-skills/release/qa-report.md` (template in `report-template.md`); rework tasks for
  🔴/🟡 via `plan-development` amend; evidence (screenshots, axe output) under
  `.dev-skills/release/artifacts/`. Never product code.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. Commit messages are always English. **One branch —
the current one** (normally `main`): never branch, switch or open a worktree unless the user
explicitly asked in this session — **`../_shared/git-workflow.md`**.

## What you prove (each flow, end-to-end against the integrated system)

Drive → observe → prove → rank the *whole* journey.

- **Happy path** — entry to success outcome on a realistic seeded state, proving the **real outcome**
  (the doc is shared, the row exists), not that each screen rendered.
- **Cross-feature state (the seams)** — create in flow A, consume in flow B; edit, then re-open;
  survive refresh / back-nav / re-login where the flow implies it.
- **Significant + error states** — every state the flow names (empty, loading, validation error,
  permission denial, network failure); its acceptance criteria are the checklist.
- **Multi-actor** — where the flow has more than one user (sharing, hand-off), drive both sides.

## The accessibility pass (same journeys, no mouse)

Over the **core journeys**, not the landing screen, and only for a product with a UI — a CLI, library
or headless API gets a clean recorded skip ("no UI surface — N/A, per design-decisions"), never
invented findings.

- **Automated pass** — `axe-core` or the project's equivalent across the key screens; each violation
  with rule id and node. Not installed → unmeasured; do the manual checks anyway.
- **Keyboard-only** — complete each core journey with **no mouse**: every control reachable and
  operable, logical focus order, no keyboard traps, **visible focus**, skip-links where needed.
- **Screen-reader semantics** — roles, names, labels; landmarks, headings; `alt` text; live regions.
- **Colour & contrast** — the level's ratio; nothing by colour alone. **Measure, report the number,
  change nothing** — the palette is frozen (**`../_shared/build-pipeline/design-freeze.md`**): a miss
  on a frozen token is an **owner decision**, filed as such — never a rework task. Accepted as a
  trade-off in `DESIGN.md` → one line, not re-raised.
- **Motion & preferences** — `prefers-reduced-motion` honoured, nothing flashing past the threshold, OS
  text scaling and zoom respected to the committed viewport.
- **Forms & errors** — errors in text (not colour alone), tied to their field, announced.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read the user flows + criteria and the accessibility target (your two contracts) + verification.md; read the mode
- [ ] Stage 1: Drive → prove — run each flow end-to-end against the integrated stack; prove the real outcome + the seams
- [ ] Stage 1b: Accessibility — re-walk the core journeys keyboard-only + axe + contrast/motion/forms (or record the no-UI skip)
- [ ] Stage 2: Rank + file — severity per the rubric (a broken core journey or a WCAG-A failure on one is 🔴); file 🔴/🟡 as rework tasks
- [ ] Stage 3: Record + verdict — write qa-report.md; clean / N blockers / N majors; the re-run confirms the journey completes
```

### Stage 0: Intake
Read both contracts, `verification.md` and the mode. On `--reaudit`, re-drive only the flows whose
findings had filed tasks.

### Stage 1: Drive → prove
Bring the stack up through the coordinated entrypoint under the **env lease**
(**`../_shared/build-pipeline/env-access.md`**) — `audit-performance` drives the same stack. Seed a
realistic state. Drive each flow **end-to-end** (Playwright / Claude-in-Chrome
for UX, the e2e harness for a multi-step flow, `curl` for an API); prove the real outcome and the
seams; probe the named error/empty/denied states. Save evidence under `.dev-skills/release/artifacts/`.
"Each page loaded" is not proof.

### Stage 1b: Accessibility (same lease, same journeys)
Automated pass, then each core journey **keyboard-only**; inspect the accessibility tree, measure
contrast, toggle reduced motion and text zoom. **Prove a barrier by hitting it** (an
inescapable trap, a control announced as "button", a failing ratio) and capture it under
`.dev-skills/release/artifacts/`.

### Stage 2: Rank + file
Per **`severity-rubric.md`**, against the flow's stated states and the committed level, not taste: 🔴
a **broken core journey** (a primary flow cannot reach its success outcome) or a **WCAG level-A failure
on one** (keyboard trap, unlabeled essential control); 🟡 a degraded secondary path, a rough error state
or a level-AA gap; ⚪ cosmetic friction off the core path. File 🔴/🟡 as `type: rework`
tasks (audit id + finding id + evidence link + the flow or WCAG criterion restored) via
`plan-development` amend — **coarse, one per coherent fix**: a flow's broken steps in one task, one
task per kind of accessibility failure across screens, each finding an `acceptance` entry with
evidence; a 🔴 keeps its own task. At the backlog's 15-open ceiling, say so rather than filing past it
(**`../_shared/build-pipeline/planning-method.md`**); the report keeps the full list.

### Stage 3: Record + verdict
Write `.dev-skills/release/qa-report.md` (**`report-template.md`**): verdict, findings table (evidence +
flow/criterion + filed task), flows driven and their outcome, which assistively, what you skipped and
why. Return the verdict to `release-product`.

## Rules

1. Read-only: never edit product code, never install anything.
2. Test journeys, not steps: the real outcome end-to-end and the seams, on realistic seeded data.
3. Hold the env lease while driving — never share the running stack with another driving audit.
4. Accessibility: the automated pass is the floor; keyboard / screen-reader / contrast / motion checks
   are the substance.
5. No finding without a driven, observed failure with evidence; a re-run clears a 🔴 only by re-driving
   the journey to completion — never by assumption.
6. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
