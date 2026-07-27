# Mockup rendering method (shared — build pipeline)

How a UI mockup is produced and shown. A **mockup** is a throwaway, static page (or a few) with **no
business logic** — its only job is to make a UI option *visible* so a human can compare and choose.
`generate-mockups` is the engine. This file defines the *how* once — the rendering tiers, the token
resolution, where mockups live, and how a chosen variant is recorded — so the skill doesn't restate it.

The governing constraint: dev-skills has **no browser/screenshot tooling of its own**, and it must
not depend on any external plugin (gstack's `browse`/`design-shotgun` are a *separate* marketplace).
So rendering **detects what's available and degrades gracefully** — it is never blocked by missing
tooling; in the worst case it generates the files and tells the human how to open them.

## Two things a mockup is NOT

- **Not the implementation.** A mockup has no data layer, no auth, no real handlers — hard-coded
  sample content only. It is reference, discarded after the choice; the real feature is built by
  `implement-feature` against the committed `DESIGN.md`.
- **Not pixel-invented.** It renders against the project's **design system** — the root `DESIGN.md`
  tokens. The mockup shows *that system applied to this screen*, never a freehand palette, and never an
  alternative design system (that is settled in the spec).

## The three rendering tiers (detect, then degrade)

At intake, probe in this order and pick the first that's available — record which tier you used so the
output is honest about how it was rendered.

### Tier 1 — render in the project's own stack (preferred when it exists)
If `.dev-skills/project-setup/verification.md` exists and the app is scaffolded and runnable, render the
variants as **real pages/components in the project's own dev server** and screenshot them via the
**run / drive / prove** commands that contract already documents (`verification-method.md`). This is
the truest "real rendered code" and reuses existing machinery rather than inventing any. It drives the
one shared stack, so it **acquires the env lease** first (`env-access.md`) — when invoked inside
`run-task`/`setup-dev-environment` the lease is already held and inherited; a standalone run
acquires/releases it itself. Put the throwaway variant pages behind a scratch route or a `/_mockups/`
path and never wire them into the real navigation.

### Tier 2 — standalone static HTML + any screenshot tool
When there is **no runnable app yet** (a feature is mocked before its stack exists, or the scaffold
doesn't boot yet), generate **self-contained static HTML/CSS** — one
file per variant, no framework, no build step, no logic. Inline the design system as CSS custom
properties on `:root` (token resolution below) so the HTML reflects the real system and opens in any
browser. If **any** generic browser/screenshot tool is available in the session (a Playwright/Puppeteer
MCP, Claude-in-Chrome, a headless-screenshot CLI on PATH — detected at runtime, never required and
never a named hard dependency), screenshot each file for side-by-side comparison. The screenshot is a
bonus; the HTML is the deliverable.

### Tier 3 — generate-only (the always-available floor)
If neither a runnable app (Tier 1) nor any screenshot tool (Tier 2) is present, **generate the variant
files and stop** — then tell the human exactly how to view them ("open
`.dev-skills/build-plan/mockups/<slug>/variant-a.html` in your browser; tell me which you prefer"). This
degrades to zero infra: the skill is never blocked, it just does less automatically. State plainly that
auto-screenshots were unavailable — never imply a render that didn't happen.

> Detect, don't assume — the same discipline `setup-dev-environment` uses. Tier 1 is the default in a
> built project; Tier 2 is the fallback while the stack isn't runnable yet.

## Token resolution (`DESIGN.md` → CSS)

`DESIGN.md` holds machine-readable tokens in YAML front matter with reference syntax like
`{colors.primary}` (see `setup-dev-environment/references/design-md-format.md`). To render a Tier-2
standalone variant, resolve the token graph into flat CSS custom properties on `:root`:

- Flatten each token path to a variable: `colors.primary` → `--colors-primary`, `typography.body.fontSize`
  → `--typography-body-fontSize`.
- Resolve `{path}` references to the value they point at (one pass over the resolved map; a reference to
  a reference resolves transitively).
- Emit `:root { --colors-primary: #…; … }` and write the markup using `var(--colors-primary)`.

This is a small deterministic transform — keep it as instructions here, **not** a committed script,
unless it later proves to need one (the repo adds infra reluctantly; today it has exactly one script,
the write-scope guard).

## Where mockups live (scratch, gitignored)

Mockups are disposable comparison artifacts — several throwaway variants per subject. They are
**not committed product code**:

- Write them under `.dev-skills/build-plan/mockups/<slug>/` — `<slug>` is the task id (e.g. `T012`) or a
  short slug derived from the screen description when there is no task.
- Each variant is `variant-{a,b,c}.{html|tsx|…}` plus its screenshot `variant-{a,b,c}.png` when a tier
  produced one.
- The tree is **gitignored**: ensure `.dev-skills/build-plan/.gitignore` contains `mockups/` (create the
  `.gitignore` with that line if absent — the build pipeline otherwise keeps no transient files, so
  this is the one gitignore it adds anywhere in the three pipelines).
- The single screenshot of the **chosen** variant *may* be copied to a committed location as the "this
  is what we picked" record — `.dev-skills/build-plan/tasks/artifacts/`, next to verifier evidence. The
  other variants are discarded.

## Recording the chosen variant

A mockup only earns its keep if the choice survives into the build. Write a short **design-note into
the task's `## Description`** — the section `implement-feature` already reads — naming the chosen
variant, what to follow (layout, hierarchy, component usage), and the path to its file + screenshot.
Then append a dated `## Log` line, e.g. `- <ts> [generate-mockups] 3 variants for T012; chose B → see
.dev-skills/build-plan/tasks/artifacts/T012-variant-b.png`. No backlog-schema change — it uses the existing
`## Description` + `## Log` fields, and only the task file is edited. Mocking a screen with no task
behind it, report the pick in the chat — there is nowhere to record it.

## Generating meaningfully-different variants

Generate **N** variants (default 3) that differ along real axes, not cosmetics — layout/structure,
information hierarchy, density/whitespace, navigation pattern — so the comparison is a genuine choice,
not three near-identical pages. All variants use the **same** design system (tokens) — they explore
*arrangement*, not palette. Full guidance: `../../generate-mockups/references/mockup-variant-guide.md`.

For speed, the variants are independent, so they may be generated **in parallel** — spawn one
`ui-prototyper` subagent per variant (each builds one stub against the same DESIGN.md + brief) and
collect them. Parallel generation is an optimization, not a requirement; a single agent producing all N
in sequence is fine for small N.

## Write scope (never touch product code)

The mockup work writes **only** under the scratch mockups tree, the task file (for the design-note and
log line), and `/tmp`. It must **never** edit the feature's implementation — enforce this
with the shared `scripts/guard-write-scope.sh` PreToolUse hook, scoped to those paths (the same guard
`verify-feature` uses to stay out of product code).
