# The `DESIGN.md` format (reference)

`DESIGN.md` is an open, tool-neutral format for describing a design system to coding agents in a
single, version-controllable file. It pairs **machine-readable design tokens** (YAML front matter) with
**human-readable rationale** (markdown prose): the tokens give an agent the exact *what*, the prose
tells it the *why* and *how to apply* — so it renders the brand correctly instead of defaulting to
generic Material/shadcn. Origin: Google Labs' open `DESIGN.md` (Apache-2.0,
`github.com/google-labs-code/design.md`); it works across Stitch, Cursor, Claude Code, etc. The format
is young and may evolve — treat this as a faithful guide, not a frozen schema, and validate an imported
file against the real spec when in doubt.

## File shape

```
---
# YAML front matter — the machine-readable tokens
version: alpha
name: <Design system name>
description: <one line>
colors: { … }
typography: { … }
rounded: { … }
spacing: { … }
components: { … }
---

## Overview          (prose: brand & visual atmosphere — the why)
## Colors
## Typography
## Layout
## Elevation & Depth
## Shapes
## Components
## Do's and Don'ts
```

## Token schema (YAML front matter)

- **`version`** — optional string (current spec: `alpha`).
- **`name`** — required string.
- **`description`** — optional one-line string.
- **`colors`** — key→value map. Values are hex / rgb / oklch / named colors, keyed by **semantic role**
  (`primary`, `surface`, `background`, `accent`, `error`, `onPrimary`, …) — roles, not raw swatch names.
- **`typography`** — named text styles, each with: `fontFamily`, `fontSize`, `fontWeight`,
  `lineHeight`, `letterSpacing`, and optionally `fontFeature`, `fontVariation`. Key by role
  (`display`, `heading`, `body`, `caption`, `code`, …).
- **`rounded`** — corner-radius scale (`none`, `sm`, `md`, `lg`, `full`), values in px/em/rem.
- **`spacing`** — spacing scale (named levels or a numeric step), values as dimensions or numbers.
- **`components`** — named component groups (`button`, `card`, `input`, `nav`, …), each mapping
  properties (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`,
  `width`, …) to **token references**.

### Token references

A value may reference another token by path, in braces: `{colors.primary}`, `{spacing.4}`,
`{typography.body}`. References resolve transitively (a reference may point at another reference). This
keeps the system DRY — components point at the palette/scale, they don't restate values.

## The prose sections (canonical order)

Each is a `##` heading. Order matters — agents look for sections by position.

1. **Overview** — the brand's visual atmosphere and aesthetic intent; the one-paragraph "feel" that
   makes choices coherent. (Sometimes titled *Brand & Style*.)
2. **Colors** — what each semantic role means and when to use it; the contrast/accessibility intent.
3. **Typography** — the families, the scale, the pairing rationale; when to use each style.
4. **Layout** — grid, breakpoints, base spacing rhythm, container widths.
5. **Elevation & Depth** — shadows, z-layers, how surfaces stack.
6. **Shapes** — corner-radius language, borders, shape motifs.
7. **Components** — patterns for the core components (button/card/form/nav) and their variants/states.
8. **Do's and Don'ts** — explicit allowed/forbidden rules — the guardrails that stop an agent drifting
   to a generic look. The highest-leverage section for keeping generated UI on-brand.

## Minimal example

```
---
version: alpha
name: Warm Editorial
description: Calm, text-forward reading product with a warm paper feel.
colors:
  background: "#FAF7F2"
  surface: "#FFFFFF"
  primary: "#1F6F5C"
  onPrimary: "#FFFFFF"
  text: "#22201C"
  muted: "#6B655C"
  accent: "#C2410C"
  error: "#B3261E"
typography:
  heading: { fontFamily: "Fraunces, serif", fontSize: "2rem", fontWeight: 600, lineHeight: 1.2, letterSpacing: "-0.01em" }
  body:    { fontFamily: "Inter, sans-serif", fontSize: "1rem", fontWeight: 400, lineHeight: 1.6, letterSpacing: "0" }
  caption: { fontFamily: "Inter, sans-serif", fontSize: "0.85rem", fontWeight: 400, lineHeight: 1.4, letterSpacing: "0.01em" }
rounded:
  none: "0"
  sm: "4px"
  md: "8px"
  lg: "16px"
spacing:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  6: "24px"
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.onPrimary}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "{spacing.3}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
    padding: "{spacing.6}"
---

## Overview
Warm Editorial is a reading-first product. The atmosphere is calm and paper-like…

## Colors
`primary` (deep green) is for primary actions and active states only…

## Typography
Fraunces (a soft serif) for headings pairs with Inter for body…

## Layout
Single readable column, max width ~70ch; an 8px spacing rhythm…

## Elevation & Depth
Mostly flat; cards lift with a single soft shadow, never stacked elevations…

## Shapes
Gently rounded (md/lg); no sharp corners, no pills except tags…

## Components
Buttons are solid `primary`; secondary actions are text buttons…

## Do's and Don'ts
- Do keep long-form text on `surface` over `background`.
- Don't introduce a second accent hue; `accent` is for one thing — inline emphasis.
- Don't use pure black (`#000`) — text is `{colors.text}`.
```

## Using it to render and to build

- **Rendering a mockup (Tier 2):** flatten the tokens to CSS custom properties on `:root` and write
  markup with `var(--…)` — see `../../_shared/build-pipeline/mockup-method.md` ("Token resolution").
- **Building a feature:** `implement-feature` reads the root `DESIGN.md` and applies the tokens + the
  Do's/Don'ts; the prose resolves the judgment calls the tokens alone can't.

## When importing an existing `DESIGN.md`

Validate before adopting: front matter parses as YAML; `name` present; the prose sections are present
and in order; every `{path}` reference resolves to a real token; color roles cover at least
background/surface/text/primary; text-on-surface contrast meets the project's WCAG target. Report any
gap rather than silently "fixing" the author's intent.
