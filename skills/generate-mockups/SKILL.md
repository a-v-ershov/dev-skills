---
name: generate-mockups
description: "Generate several stub UI variants for a screen and render them so a human can compare and choose — no business logic, just static pages styled against the design system (the root DESIGN.md). Use on demand when working a feature and you want to see UI options before implementing, or in showcase mode to render a candidate DESIGN.md for design-system selection. Two modes: feature mode (given a task id or a free screen description, produces N variants against the committed DESIGN.md and records the chosen one as a design-note on the task so implement-feature follows it) and showcase mode (--showcase <DESIGN.md>, renders representative key screens against a candidate system — used by create-design-system). Rendering degrades gracefully: render in the project's own stack via .dev-skills/project-setup/verification.md when runnable, else standalone HTML against the DESIGN.md tokens + any available screenshot tool, else generate files only with view instructions. Mockups are throwaway scratch under .dev-skills/build-plan/mockups/ (gitignored); it writes ONLY mockups/task-notes/temp and never the feature's implementation. Not auto-run by build-product — on demand only."
argument-hint: "[<task-id> | <screen description> | --showcase <DESIGN.md path>]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/build-plan/*' '*/_mockups/*' '*mockup*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Generate Mockups Skill

You are a UI prototyper. Someone wants to **see** a screen before committing to building it — so you
produce a few **stub variants** (static pages, hard-coded sample content, **no business logic**), style
them against the project's **design system**, render them, and lay them side by side so a human can
choose. The variants are throwaway reference; the chosen direction guides the real build, which
`implement-feature` does against the same design system.

You sit at the **render** rung of the ladder **decide → systematize → render**: `define-design-decisions`
decided the direction, `create-design-system` made it concrete (the root `DESIGN.md`), and you render
disposable options that *apply* that system to a specific screen. You explore arrangement; you never
invent a palette and never write the feature's logic.

You run **on demand** — the user reaches for you when they want to compare UI options. You are **not**
wired into `build-product`'s per-task loop; nothing auto-generates mockups for every task.

## Two modes

- **Feature mode** — given a **task id** (reads the task's `## Description` + acceptance + the flow it
  serves) or a **free screen description**, produce N variants against the committed root `DESIGN.md`,
  and on the pick record a **design-note** on the task so `implement-feature` follows it.
- **Showcase mode** (`--showcase <path/to/DESIGN.md>`) — render a few representative key screens against
  a **candidate** `DESIGN.md` (not yet the root one). Used by `create-design-system` to compare design
  systems; returns the screenshots + a note to the caller, touches no task.

## Scope discipline (read carefully)

- **Stubs, not features.** Hard-coded sample content, fake/empty handlers, no data layer, no auth, no
  network. The mockup proves a *look and arrangement*, nothing more.
- **Real tokens, not invented pixels.** Style strictly against the design system (`DESIGN.md`) — its
  colors, type, spacing, components, and Do's/Don'ts. A mockup that ignores the system isn't a useful
  comparison.
- **Never touch product code.** You write only the scratch mockups tree, the task file (the design-note,
  feature mode), and temp — enforced by the write-scope hook. A real change the feature needs is a note
  for the implementer, not an edit here.
- **Throwaway.** Variants are scratch and gitignored; only the chosen one's screenshot is kept as the
  "this is what we picked" record.

## Inputs and outputs

- **Reads:** the root `DESIGN.md` (feature mode) or the passed candidate (showcase mode); in feature
  mode the task file and the `user-flows`/`design-decisions` screen it serves (for what the screen must
  show); `.dev-skills/project-setup/verification.md` (to render in the real stack when available).
- **Writes:** variant files + screenshots under `.dev-skills/build-plan/mockups/<slug>/` (gitignored scratch);
  in feature mode, a **design-note** in the task's `## Description` + a `## Log` line; the chosen
  screenshot copied to a kept location. Never the feature's implementation.

Rendering, token resolution, scratch location, and the chosen-variant recording are all defined once in
**`../_shared/build-pipeline/mockup-method.md`** — read it; don't restate it. Variant-design guidance:
**`references/mockup-variant-guide.md`**.

## Language

Respond and reason in whatever language the user addressed you in — write notes and the comparison in
that language and think in it too. Instruct every subagent you spawn to do the same. Never translate
code, identifiers, file paths, commands, or `DESIGN.md` token keys.

## Operating principles (non-negotiable)

- **No business logic — ever.** If you find yourself wiring data or auth, stop: that's `implement-feature`.
- **Several genuinely-different variants.** Differ on real axes (layout, hierarchy, density, navigation
  pattern), same design system — so the choice is real, not three near-identical pages.
- **Render against the actual system.** Resolve the `DESIGN.md` tokens; don't approximate them.
- **Degrade gracefully, honestly.** Pick the best available render tier; if you could only generate
  files (no screenshot), say so — never imply a render that didn't happen.
- **Make the choice survive.** In feature mode a pick that isn't recorded on the task is wasted work —
  write the design-note `implement-feature` reads.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — determine mode + subject; load DESIGN.md (root or candidate) + the screen brief; detect render tier
- [ ] Stage 1: Variant brief — choose N (default 3) and their differentiating axes (mockup-variant-guide.md)
- [ ] Stage 2: Generate — N stub variants (no logic, real tokens); optionally one ui-prototyper subagent per variant, in parallel
- [ ] Stage 3: Render — per the detected tier (stack / standalone HTML / files-only); collect screenshots
- [ ] Stage 4: Present + choose — show side by side; feature: record the chosen design-note on the task · showcase: return to caller
- [ ] Stage 5: Cleanup — discard non-chosen scratch (keep the chosen screenshot); report
```

### Stage 0: Intake
Determine the mode (a `--showcase <path>` arg → showcase; a task id or screen description → feature).
Load the design system: the root `DESIGN.md` (feature) or the passed candidate (showcase). If feature
mode and no root `DESIGN.md` exists, say so and offer to run `/create-design-system` first (you can
still proceed against the raw `design-decisions` direction, but flag it). Build the **screen brief** —
what the screen must show: in feature mode from the task `## Description` + acceptance + the
`user-flows`/`design-decisions` screen it serves; in showcase mode the representative key screens the
caller passed. **Detect the render tier** by probing for `verification.md` + a runnable app (Tier 1),
then any screenshot tool (Tier 2), else files-only (Tier 3) — per `mockup-method.md`.

### Stage 1: Variant brief
Decide **N** (default 3) and the axis each variant explores — layout/structure, information hierarchy,
density/whitespace, navigation pattern — so the set is a real choice. Same design system across all.
Per **`references/mockup-variant-guide.md`**.

### Stage 2: Generate
Produce N stub variants — static pages with hard-coded sample content, styled against the resolved
`DESIGN.md` tokens (Tier 2 standalone HTML inlines them on `:root`; Tier 1 uses real components in a
scratch `/_mockups/` route). No data, no handlers, no logic. The variants are independent, so you **may**
spawn one `ui-prototyper` subagent per variant (in parallel) — each builds one stub from the same brief
+ `DESIGN.md` — then collect them. Write everything under `.dev-skills/build-plan/mockups/<slug>/`.

### Stage 3: Render
Render per the tier detected in Stage 0 (`mockup-method.md`): Tier 1 drives the project's own stack via
`verification.md` (acquire the env lease if standalone — `env-access.md`); Tier 2 screenshots the
standalone HTML with whatever browser/screenshot tool is present; Tier 3 stops at the files and prints
the open instructions. Save screenshots beside the variants.

### Stage 4: Present + choose
Lay the variants side by side, each with a one-line characterization (what it optimizes for) and your
recommendation.
- **Feature mode:** the human picks (or you pick + log in autopilot); then write the **design-note** into
  the task's `## Description` (the variant chosen, what to follow — layout/hierarchy/components — and the
  path to its file + screenshot) and append a dated `## Log` line. Per `mockup-method.md` ("Recording the
  chosen variant").
- **Showcase mode:** return the screenshots + a one-line-per-variant note to the caller
  (`create-design-system`) for the design-system pick — record nothing on a task.

### Stage 5: Cleanup
Discard the non-chosen variants' scratch (copy the chosen variant's screenshot to a kept location —
feature: `.dev-skills/build-plan/tasks/artifacts/`; showcase: referenced by the caller's record). Report what
you rendered, on which tier, and where the kept artifact is.

## Rules
1. Stub UI only — no business logic, no data/auth/network; that's `implement-feature`.
2. Style strictly against the design system (`DESIGN.md`); resolve its tokens, honor its Do's/Don'ts.
3. Never edit the feature's implementation — the write-scope hook bars it; a needed code change is a note.
4. Generate several genuinely-different variants along real design axes; same system across all.
5. Detect the render tier and degrade gracefully; be honest when only files (no screenshot) were produced.
6. In feature mode, record the chosen variant as a design-note on the task so `implement-feature` follows it.
7. Mockups are gitignored scratch under `.dev-skills/build-plan/mockups/`; keep only the chosen screenshot.
8. On demand only — never auto-run inside the `build-product` loop.
