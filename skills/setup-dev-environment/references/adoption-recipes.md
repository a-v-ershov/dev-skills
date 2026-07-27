# Adopting a UI kit into `DESIGN.md` (recipes)

When `design-decisions` chose to **adopt an existing UI kit** (rather than go bespoke), the kit *is* the
design system — your job is to **codify its public tokens into `DESIGN.md`** so the agent applies the
kit's identity consistently, then offer 1–2 variations as alternate candidates. Pull token values from
the kit's **official** docs/specs (cite the source); do not invent values, and do not install the kit
here (that's `setup-dev-environment`/backlog work — `DESIGN.md` stays tool-neutral).

General recipe (every kit):
1. Map the kit's **color roles** → `colors` (semantic keys: background/surface/primary/accent/error/…).
2. Map its **type scale** → `typography` (one entry per role: display/heading/body/caption/code).
3. Map its **radius** and **spacing** scales → `rounded` / `spacing`.
4. Map its **core components** (button/card/input/nav) → `components`, pointing at the tokens above.
5. Write the prose: **Overview** = the kit's design philosophy in one paragraph; **Do's and Don'ts** =
   the kit's own guardrails (these are usually well documented — adopt them verbatim in spirit).
6. Offer **variations** as separate candidates — e.g. the kit's defaults vs a brand-tinted palette vs a
   tighter/looser type scale — so the human compares within the chosen family.

## Material 3 (Material You)
- Colors: adopt the M3 **color roles** (primary / on-primary / primary-container / surface /
  surface-variant / outline / error …). If a brand seed color is known, note that M3 derives the full
  tonal palette from it — record the seed and the key resolved roles.
- Typography: the M3 **type scale** (display / headline / title / body / label, each large/medium/small).
- Shapes: M3 shape scale (none → extra-large) → `rounded`. Elevation: M3 tonal elevation levels.
- Do's/Don'ts: dynamic color, large touch targets, motion easing — from the M3 guidelines.

## shadcn/ui (Radix + Tailwind)
- Colors: shadcn themes are **CSS variables** (`--background`, `--foreground`, `--primary`,
  `--muted`, `--accent`, `--destructive`, `--border`, `--ring`) in HSL. Map each variable → a
  `colors` role (keep both light and dark if the theme defines them; note the dark set in prose).
- Radius: the theme's `--radius` → `rounded` scale. Typography: usually Tailwind defaults + a chosen
  font — record the font and the Tailwind type steps used.
- Components: shadcn component variants (button: default/secondary/ghost/destructive/outline) → the
  `button` group's variants in prose.

## Tailwind UI / a Tailwind theme
- Colors: the configured `theme.extend.colors` palette → `colors` (by role). Spacing/radius: Tailwind's
  default scale (or the `theme.extend` overrides) → `spacing` / `rounded`.
- Typography: the `fontFamily` + the type steps in use → `typography`.

## Radix (primitives + Radix Colors)
- Colors: a **Radix Colors** scale (e.g. `slate`, `grass`, `tomato`, each 1–12 steps with semantic
  meaning: 1–2 backgrounds, 3–5 component backgrounds, 6–8 borders, 9–10 solid, 11–12 text). Map the
  steps to roles in prose so the agent uses the right step for the right job.
- Radix primitives are unstyled — the `components` mappings + Do's/Don'ts carry the styling intent.

## Existing project (reverse-engineer the realized system)
In `project_type: existing`, the kit is already wired. Read the **actual** config `map-codebase`
charted — `tailwind.config`, `components.json` + the CSS variables, a Material theme file, design-token
JSON, a Storybook — and codify the **as-built** tokens into an AS-IS `DESIGN.md` (cite the file each
value came from). Then propose TARGET candidates only where the user wants to evolve it; log the
difference as drift.
