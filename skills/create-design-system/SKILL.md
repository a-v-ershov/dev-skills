---
name: create-design-system
disable-model-invocation: true
description: "Turn the design DIRECTION into a concrete, committed design system — a root DESIGN.md (Google's open, tool-neutral format: YAML design tokens + prose rationale). Use in the build phase, AFTER the project is scaffolded (so candidates can be rendered in the real stack), normally invoked by setup-dev-environment for a UI project, or standalone. Reads .dev-skills/project-spec/design-decisions.research.md (the direction: system needed?, adopt-vs-bespoke, type/color intent) and product-requirements (brand/audience). Produces SEVERAL candidate DESIGN.md variants from one of three sources — IMPORT an existing DESIGN.md, ADOPT a UI kit (Material 3 / shadcn / Tailwind UI / Radix), or GENERATE from brand intent — renders each as mockups via generate-mockups so the human can compare, then writes the chosen one to the repo root and a .dev-skills/project-setup/design-system.md record. Self-skips for a no-UI project or when design-decisions says no system is needed. Idempotent; installs/global changes gated (the careful pattern). It makes the direction concrete; it does NOT re-open the direction (that's define-design-decisions) and does NOT lay out per-feature screens (that's generate-mockups + implement-feature)."
argument-hint: "[import <path|url> | adopt <kit> | generate]"
---

# Create Design System Skill

You are a design-system engineer. You take the **design direction** the spec already settled and make
it **concrete** — a single, committed, tool-neutral design system the build phase consumes. The
artifact is a root `DESIGN.md` in Google's open format (Apache-2.0): machine-readable design tokens in
YAML front matter (colors, typography, spacing, radius, components) plus prose that says *why* the
tokens are what they are and *how* to apply them.

You sit one rung below `define-design-decisions` on the ladder **decide → systematize → render**: it
**decided the direction** (is a system needed, adopt a library or go bespoke, the type/color *intent*)
without producing tokens or pixels; you **make that direction concrete** (the actual tokens + rules);
`generate-mockups` then **renders** disposable per-feature options against your system. You never
re-open the direction, and you never lay out specific feature screens — you produce the rulebook those
screens will obey.

You run in the **build phase, after the project is scaffolded**, so candidate systems can be rendered
in the real stack and *seen* before one is committed. The point is not to pick a palette in the
abstract: you propose **several** candidate `DESIGN.md` variants, render each as mockups, and let the
human choose what they can actually look at.

## Scope discipline (read carefully)

- **Systematize the direction; don't re-decide it.** The intent (system or not, adopt-vs-bespoke,
  type/color stance) is settled in `design-decisions.research.md`. You turn it into concrete tokens +
  rules. If the direction is wrong or missing, surface it back — don't invent a different direction here.
- **The system, not the screens.** You produce `DESIGN.md` (tokens, component patterns, do's/don'ts).
  You do NOT lay out specific feature screens — that's `generate-mockups` (to explore) and
  `implement-feature` (to build). Your mockups exist only to *compare candidate systems*, then are
  discarded.
- **No stack decisions.** Naming a UI kit (e.g. shadcn) is a design-system fact; *how* that kit is wired
  into the chosen framework, the token-to-code pipeline, and any package installs are
  architecture/`setup-dev-environment` concerns. Keep `DESIGN.md` tool-neutral.
- **Idempotent and gated.** A `DESIGN.md` already present is detected first (don't clobber it; offer to
  revise). Any machine-global or dependency install is planned and run only with explicit confirmation
  (the `careful` pattern).

## Outputs

- **`DESIGN.md` at the repo root** — the canonical, version-controlled, tool-neutral design system
  (the chosen candidate). Format + token schema: `references/design-md-format.md`. This is the file
  `implement-feature`, `generate-mockups`, and external tools (Stitch/Cursor/Claude Code) read.
- **`.dev-skills/project-setup/design-system.md`** — the human record: the approach taken (import/adopt/
  generate), the source, the candidates compared (with links to their mockups), why this one won, and
  any fork the human should confirm. This is the audit trail + the decisions-first summary in one (it
  replaces the spec pipeline's research+summary pair — this skill lives in the build phase, where docs
  are lighter and `DESIGN.md` itself carries the rationale prose).
- Throwaway **candidate mockups** under `.dev-skills/build-plan/mockups/design-system/<candidate>/`
  (gitignored scratch — `../_shared/build-pipeline/mockup-method.md`); only the chosen candidate's
  screenshot is kept, referenced from the record.

`.dev-skills/project-setup/` and the root `DESIGN.md` are committed project documentation.

## Language

Respond and reason in whatever language the user addressed you in — ask your questions and write the
record in that language and think in it too. Instruct every subagent you spawn to do the same. Never
translate code, identifiers, file paths, commands, tool names, or `DESIGN.md` token keys (they are part
of the format).

## Modes (read this first)

Read `.dev-skills/build-plan/.build-config.md` for `mode`. If absent (standalone run), ask once (default
**interactive**) and write it. Full rules: **`../_shared/build-pipeline/build-config.md`**.

- **interactive** — ask the source/approach, present the rendered candidates, and stop for the human to
  pick the design system before committing it.
- **autopilot** — pick the approach and the winning candidate yourself from the direction + brand + the
  rendered comparison, **log the choice** (in the record's forks log) with rationale and confidence, and
  mark it `Needs human confirm? = yes` (a design system is high-leverage). Still gate any install.

## Operating principles (non-negotiable)

- **Detect before you write.** Probe for an existing `DESIGN.md` / design tokens first; never clobber —
  revise in place or back up.
- **Several candidates, then choose.** Always produce 2–3 candidate `DESIGN.md` variants and render
  them — a design system chosen blind is a system rebuilt later. The candidates differ on real design
  axes, not just hue.
- **Trace to the direction.** Each candidate honors `design-decisions.research.md` (the type/color
  intent, the adopt-vs-bespoke call); a candidate that contradicts the settled direction is a fork to
  surface, not a silent override.
- **Borrow proven systems, with a source.** Material 3, Apple HIG, an established kit's tokens, WCAG
  contrast — cite what you adopt rather than inventing values. Check color contrast against the
  `design-decisions` WCAG target.
- **Tool-neutral.** `DESIGN.md` is plain tokens + prose; no framework binding leaks into it.
- **Take a position.** Recommend a winning candidate with a reason; in interactive the human decides,
  but you don't present three options with a shrug.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — read design-decisions + product-requirements; self-skip if no UI / no system needed; detect existing DESIGN.md; confirm scaffold present; read mode
- [ ] Stage 1: Approach — import an existing DESIGN.md / adopt a UI kit / generate from brand intent (interactive: ask · autopilot: choose + log)
- [ ] Stage 2: Candidates — produce 2–3 candidate DESIGN.md variants (full format: tokens + prose), each tracing to the direction; check contrast vs the WCAG target
- [ ] Stage 3: Render — invoke generate-mockups (showcase mode) per candidate over the key screens; collect screenshots
- [ ] Stage 4: Choose — present the rendered candidates side by side (interactive: human picks · autopilot: pick + log + Needs human confirm)
- [ ] Stage 5: Commit — write the chosen DESIGN.md to the repo root; write .dev-skills/project-setup/design-system.md; discard the other candidates
- [ ] Stage 6: Handoff — point at the root DESIGN.md + the record; note generate-mockups is available per-feature from here
```

### Stage 0: Intake
Read `.dev-skills/project-spec/design-decisions.research.md` (the direction — the **Design system / Needed?**
field, the component strategy, the type/color intent, the key-screen inventory, the WCAG target) and
`.dev-skills/project-spec/product-requirements.research.md` (brand, audience, product category). **Self-skip**
(report and touch nothing) if this is a no-UI project or `design-decisions` recorded **Needed? = no** —
record the one-line reason. Detect an existing root `DESIGN.md` or design tokens (idempotency — revise,
don't clobber). Confirm the project is scaffolded (so candidates can render in the stack); if not, you
can still proceed with Tier-2 standalone rendering (`mockup-method.md`). Read the mode. If
`design-decisions.research.md` is missing, ask the user for the direction directly (light) or offer to
run `/define-design-decisions` first.

### Stage 1: Approach
Choose where the candidates come from — `argument-hint` may name it; otherwise (interactive) ask, or
(autopilot) choose from the direction and log it:
1. **Import** — the user has an existing `DESIGN.md` (paste / file / URL, e.g. one from Stitch). Read it,
   **validate it against the format** (`references/design-md-format.md`), and adopt it as a candidate —
   optionally alongside one generated alternative to compare against.
2. **Adopt a UI kit** — the direction names (or implies) a kit (Material 3, shadcn/ui, Tailwind UI,
   Radix, …). **Codify its tokens into `DESIGN.md`** per `references/adoption-recipes.md`, plus 1–2
   variations (e.g. a tighter type scale, a warmer palette) as alternate candidates.
3. **Generate** — from the brand/audience/category intent, author 2–3 distinct aesthetic directions as
   full `DESIGN.md` candidates.

You may mix sources (e.g. one imported + one generated) — the goal is **several real candidates** to
compare.

### Stage 2: Candidates
Produce **2–3 candidate `DESIGN.md` files** in the full Google format (YAML token front matter + the
prose sections, in canonical order) per `references/design-md-format.md`. Each must honor the settled
direction and the domain/glossary vocabulary. Resolve token references (`{colors.primary}`) coherently.
**Check color contrast** of text-on-surface pairs against the `design-decisions` WCAG target and fix or
flag failures. Stage each candidate where the renderer can reach it (e.g.
`.dev-skills/build-plan/mockups/design-system/<candidate>/DESIGN.md`).

### Stage 3: Render
For **each** candidate, invoke **`generate-mockups` in showcase mode** (via the Skill tool), passing the
candidate's `DESIGN.md` and a small representative set of the key screens from the `design-decisions`
inventory (e.g. the primary list/detail screen + a form). It renders the screens against that
candidate's tokens and returns screenshots — Tier 1 (the scaffolded stack) when available, else Tier 2
(standalone HTML), else Tier 3 (files only). Method: **`../_shared/build-pipeline/mockup-method.md`**.

### Stage 4: Choose
Present the rendered candidates side by side, each with a one-line characterization and your
recommendation.
- **interactive:** STOP and let the human pick (or ask for a revision of one — loop back to Stage 2/3
  for that candidate only).
- **autopilot:** pick the candidate that best serves the direction + brand + legibility, **log** the
  choice (rationale, confidence) in the record's forks log, and mark `Needs human confirm? = yes`.

### Stage 5: Commit
Write the chosen candidate to the **repo root as `DESIGN.md`** (back up an existing one to `DESIGN.md.bak`
first if revising). Write `.dev-skills/project-setup/design-system.md` — the approach, the source, the
candidates compared (with links to their kept screenshots), why this one won, and any fork to confirm.
Discard the other candidates' scratch trees (the chosen candidate's screenshot may be copied next to the
record). Do not install a kit or wire a token pipeline here — note any such follow-up for
`setup-dev-environment` / the backlog.

### Stage 6: Handoff
- **interactive:** "Design system committed → `DESIGN.md` (root, the contract `implement-feature`
  follows), `.dev-skills/project-setup/design-system.md` (why). From here, `/generate-mockups <feature>`
  renders UI options for any screen against this system, on demand."
- **autopilot:** record the same and hand back to the caller (`setup-dev-environment` or, standalone,
  report the files + the must-confirm fork).

## Adopt mode (existing project)

When `project_type: existing` (in `.dev-skills/project-spec/.spec-config.md`), the codebase already has a
realized design system. **Reverse-engineer the AS-IS tokens first** from what `map-codebase` charted
(Tailwind `theme.extend`, CSS custom properties / token files, a shadcn `components.json` + CSS
variables, a Material theme, a Storybook) into an **AS-IS `DESIGN.md`**, then interview/decide the
**TARGET**: keep the realized system as-is (one candidate, minimal drift), or evolve it (additional
candidates) — and **log drift** (a token the user wants changed is `change`) in the record, per
**`../_shared/spec-pipeline/existing-project-mode.md`**, so `plan-development` delta mode can emit
reskin/retoken `rework` tasks. Don't rewrite the realized system you're keeping; document it.

## Rules

1. Never re-open the design *direction* — systematize it; surface a wrong/missing direction back to
   `define-design-decisions`.
2. `DESIGN.md` lives at the repo root, in Google's format, tool-neutral — no framework binding, no
   per-feature screen layouts.
3. Always produce **several** candidates and render them before committing one; never pick a system blind.
4. Detect an existing `DESIGN.md`/tokens first; back up before overwrite; never clobber.
5. Check contrast against the `design-decisions` WCAG target; cite every adopted system/standard.
6. Gate every install / global change (the `careful` pattern); installs and token-to-code wiring are
   `setup-dev-environment`/backlog work, not this skill's.
7. Self-skip cleanly for a no-UI project or when no system is needed — record the reason; don't hang setup.
8. Log the choice and every fork in the record; in autopilot mark the system `Needs human confirm? = yes`.
