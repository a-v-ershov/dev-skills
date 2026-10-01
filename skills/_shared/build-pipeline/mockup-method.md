# Mockup rendering method (shared — build pipeline)

A **mockup** is a throwaway, static page (or a few) with **no business logic** — it makes a UI option
*visible* so a human can compare and choose. `generate-mockups` is the engine; this file defines the
rendering tiers, token resolution, where mockups live, and how a chosen variant is recorded.

dev-skills has **no browser/screenshot tooling of its own** and depends on no external plugin
(gstack's `browse`/`design-shotgun` are a *separate* marketplace), so rendering **detects what's
available and degrades gracefully** — never blocked.

## Two things a mockup is NOT

- **Not the implementation.** No data layer, no auth, no real handlers — hard-coded sample content,
  discarded after the choice; `implement-feature` builds the real feature against `DESIGN.md`.
- **Not pixel-invented.** It renders the root `DESIGN.md` tokens — *that system applied to this
  screen*, never a freehand palette or an alternative design system (settled in the spec).

## The three rendering tiers (detect, then degrade)

At intake, probe in this order and pick the first available — detect, don't assume, as
`setup-dev-environment` does. Record the tier used so the output is honest about how it was rendered.

### Tier 1 — render in the project's own stack (preferred when it exists)
If `.dev-skills/project-setup/verification.md` exists and the app is scaffolded and runnable, render the
variants as **real pages/components in the project's own dev server** and screenshot them with the
contract's **run / drive / prove** commands (`verification-method.md`). It drives the one shared stack,
so **acquire the env lease** first (`env-access.md`) — inherited inside
`run-task`/`setup-dev-environment`, acquired/released by a standalone run. Put the variant pages behind
a scratch route or a `/_mockups/` path, never in the real navigation.

### Tier 2 — standalone static HTML + any screenshot tool
**No runnable app yet** → **self-contained static HTML/CSS**, one file per variant, no framework, no
build step, no logic, with the design system inlined as CSS custom properties on `:root` (token
resolution below). If **any** generic browser/screenshot tool is in the session (a Playwright/Puppeteer
MCP, Claude-in-Chrome, a headless-screenshot CLI on PATH — detected at runtime, never a named hard
dependency), screenshot each file for side-by-side comparison. The HTML is the deliverable; the
screenshot is a bonus.

### Tier 3 — generate-only (the always-available floor)
Neither → **generate the variant files and stop**, and tell the human how to view them ("open
`.dev-skills/build-plan/mockups/<slug>/variant-a.html` in your browser; tell me which you prefer"). Say
plainly that auto-screenshots were unavailable — never imply a render that didn't happen.

## Token resolution (`DESIGN.md` → CSS)

`DESIGN.md` holds machine-readable tokens in YAML front matter with reference syntax like
`{colors.primary}` (see `setup-dev-environment/references/design-md-format.md`). For a Tier-2 variant,
resolve the token graph into flat CSS custom properties on `:root`:

- Flatten each token path to a variable: `colors.primary` → `--colors-primary`, `typography.body.fontSize`
  → `--typography-body-fontSize`.
- Resolve `{path}` references to the value they point at (one pass over the resolved map; a reference to
  a reference resolves transitively).
- Emit `:root { --colors-primary: #…; … }` and write the markup using `var(--colors-primary)`.

Keep this as instructions, **not** a committed script, unless it proves to need one (the repo's only
script is the write-scope guard).

## Where mockups live (scratch, gitignored)

Disposable comparison artifacts, **not committed product code**:

- Under `.dev-skills/build-plan/mockups/<slug>/` — `<slug>` is the task id (e.g. `T012`) or a short slug
  from the screen description when there is no task.
- Each variant is `variant-{a,b,c}.{html|tsx|…}` plus its screenshot `variant-{a,b,c}.png` when a tier
  produced one.
- The tree is **gitignored**: ensure `.dev-skills/build-plan/.gitignore` contains `mockups/` (create the
  `.gitignore` if absent — the only one the three pipelines add).
- The **chosen** variant's screenshot *may* be copied to `.dev-skills/build-plan/tasks/artifacts/`
  (beside verifier evidence) as the record of the pick; the other variants are discarded.

## Recording the chosen variant

Write a short **design-note into the task's `## Description`** (what `implement-feature` reads): the
chosen variant, what to follow (layout, hierarchy, component usage), and the path to its file +
screenshot. Append a dated `## Log` line, e.g. `- <ts> [generate-mockups] 3 variants for T012; chose B → see
.dev-skills/build-plan/tasks/artifacts/T012-variant-b.png`. No backlog-schema change; only the task file
is edited. No task behind the screen → report the pick in the chat.

## Generating meaningfully-different variants

Generate **N** variants (default 3) that differ along real axes — layout/structure, information
hierarchy, density/whitespace, navigation pattern — not cosmetics. All use the **same** design system:
they explore *arrangement*, not palette. Full guidance:
`../../generate-mockups/references/mockup-variant-guide.md`.

Variants are independent: optionally generate them **in parallel**, one `ui-prototyper` subagent per
variant against the same DESIGN.md + brief; one agent doing all N in sequence is fine for small N.

## Write scope (never touch product code)

Mockup work writes **only** the scratch mockups tree, the task file (design-note and log line), and
`/tmp` — **never** the feature's implementation. Enforced by the shared `scripts/guard-write-scope.sh`
PreToolUse hook scoped to those paths (the guard `verify-feature` uses).
