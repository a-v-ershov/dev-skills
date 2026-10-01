---
name: generate-mockups
description: "Generate several static stub UI variants for a screen against the root DESIGN.md, render them side by side and record the chosen one as a design-note on the task for implement-feature. Use on demand, given a task id or screen description, to compare options before building; arrangement within the settled design system only. Never auto-run by build-tasks."
argument-hint: "[<task-id> | <screen description>]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/build-plan/*' '*/_mockups/*' '*mockup*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Generate Mockups Skill

You are a UI prototyper at the **render** rung of **decide → systematize → render**:
`define-design-decisions` decided the direction (including the UI kit), `setup-dev-environment` made it
concrete (the root `DESIGN.md`), and you render disposable **stub variants** that *apply* that system to
one screen, side by side, so a human can choose before `implement-feature` builds it. You explore
arrangement — never a palette, never the feature's logic.

## Inputs and outputs

- **Reads:** the root `DESIGN.md`; the task file (`## Description` + acceptance) and the
  `user-flows`/`design-decisions` screen it serves — or a free screen description;
  `.dev-skills/project-setup/verification.md` (to render in the real stack when available).
- **Writes:** variant files + screenshots under `.dev-skills/build-plan/mockups/<slug>/` (gitignored
  scratch); a **design-note** in the task's `## Description` + a `## Log` line; the chosen screenshot
  copied to a kept location. Only these and temp (hook-enforced) — never the implementation.

Rendering, token resolution, scratch location and chosen-variant recording are defined once in
**`../_shared/build-pipeline/mockup-method.md`** — read it, don't restate it. Variant design:
**`references/mockup-variant-guide.md`**.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths or `DESIGN.md` token keys. Commit messages are always
English. **One branch — the current one** (normally `main`): never branch, switch or open a worktree
unless the user explicitly asked in this session — **`../_shared/git-workflow.md`**. Pass both rules
to every agent you spawn.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — determine mode + subject; load DESIGN.md (root or candidate) + the screen brief; detect render tier
- [ ] Stage 1: Variant brief — choose N (default 3) and their differentiating axes (mockup-variant-guide.md)
- [ ] Stage 2: Generate — N stub variants (no logic, real tokens); optionally one ui-prototyper subagent per variant, in parallel
- [ ] Stage 3: Render — per the detected tier (stack / standalone HTML / files-only); collect screenshots
- [ ] Stage 4: Present + choose — show side by side; record the chosen design-note on the task
- [ ] Stage 5: Cleanup — discard non-chosen scratch (keep the chosen screenshot); report
```

### Stage 0: Intake
Load the root `DESIGN.md`; none → say so and offer `/setup-dev-environment` first (it writes
`DESIGN.md` from the spec's design decisions), or proceed against the raw `design-decisions`
direction, flagged. Build the **screen brief** — what the screen must show — from the task and the
screen it serves, or from the free description. **Detect the render tier**: `verification.md` + a
runnable app (Tier 1), any screenshot tool (Tier 2), else files-only (Tier 3) — per `mockup-method.md`.

### Stage 1: Variant brief
Decide **N** (default 3) and the axis each explores — layout/structure, information hierarchy,
density/whitespace, navigation pattern (**`references/mockup-variant-guide.md`**).

### Stage 2: Generate
N static stubs with hard-coded sample content and fake/empty handlers, styled against the resolved
`DESIGN.md` tokens (Tier 2 standalone HTML inlines them on `:root`; Tier 1 uses real components in a
scratch `/_mockups/` route). You **may** spawn one `ui-prototyper` subagent per variant in parallel,
each building one stub from the same brief + `DESIGN.md`. Everything under
`.dev-skills/build-plan/mockups/<slug>/`.

### Stage 3: Render
Per the tier (`mockup-method.md`): Tier 1 drives the project's own stack via `verification.md`
(acquire the env lease if standalone — `env-access.md`); Tier 2 screenshots the standalone HTML with
whatever browser/screenshot tool is present; Tier 3 stops at the files and prints the open
instructions. Save screenshots beside the variants.

### Stage 4: Present + choose
Lay the variants side by side, each with a one-line characterization (what it optimizes for) and your
recommendation. The human picks (or you pick + log in autopilot); write the **design-note** into the
task's `## Description` (the variant chosen; what to follow — layout/hierarchy/components; the path to
its file + screenshot) and append a dated `## Log` line (`mockup-method.md` → "Recording the chosen
variant"). A free description with no task → report the pick in the chat.

### Stage 5: Cleanup
Discard the non-chosen scratch, copying the chosen screenshot to
`.dev-skills/build-plan/tasks/artifacts/`. Report what you rendered, on which tier, and where the kept
artifact is.

## Rules
1. Stub UI only — no business logic, data layer, auth or network; that's `implement-feature`.
2. Style strictly against `DESIGN.md`: resolve its tokens (colors, type, spacing, components), honor
   its Do's/Don'ts; never adjust a token — they are frozen
   (**`../_shared/build-pipeline/design-freeze.md`**).
3. Never edit the feature's implementation — a needed code change is a note for the implementer.
4. Several genuinely-different variants along real design axes; the same system across all.
5. Degrade gracefully across tiers; say when only files (no screenshot) were produced — never imply a
   render that didn't happen.
6. In feature mode, record the chosen variant as a design-note on the task — an unrecorded pick is
   wasted work.
7. Mockups are gitignored scratch under `.dev-skills/build-plan/mockups/`; keep only the chosen
   screenshot.
8. On demand only — never auto-run inside the `build-tasks` loop.
