# Designing meaningfully-different mockup variants (reference)

A good variant set is a **real choice**, not three pages that differ only by hue. All variants share
the **same design system** (the `DESIGN.md` tokens — colors, type, spacing, components are fixed); what
varies is **arrangement**. If you find the only difference is the accent color, you've made one mockup
three times.

## Vary along real axes (pick 2–3 per set)

- **Layout / structure** — single column vs sidebar+content vs grid; where the primary action sits;
  top-nav vs side-nav; modal vs inline.
- **Information hierarchy** — what's biggest and first; progressive disclosure vs everything-visible;
  summary-first vs detail-first.
- **Density / whitespace** — airy and focused (one thing per view) vs dense and efficient (a power-user
  table). A real tradeoff for the product's audience.
- **Navigation / flow shape** — wizard/steps vs single long form; tabs vs scroll; list→detail vs
  master-detail split.
- **Emphasis** — which content the screen optimizes for (e.g. a media-first card wall vs a text-first
  list for the same items).

Name the axis each variant explores, so the comparison is legible: "A — airy, action-first, single
column · B — dense table for scanning many · C — split master-detail for fast triage."

## Rules for the stubs

- **Hard-coded, realistic sample content.** Real-looking names/text/numbers (not "Lorem ipsum",
  not "Item 1 / Item 2") — believable content makes the layout judgeable. No data layer, no fetch.
- **No logic, no state machine.** Buttons don't submit; forms don't validate; nav links can be inert or
  jump between the static variant pages. Just enough to *see* the screen.
- **Cover the screen's real job.** Pull what the screen must show from the task's acceptance criteria /
  the `user-flows` success outcome — including an important empty or error state if it's central (shown
  statically, not wired).
- **Apply the system faithfully.** Use the resolved tokens for every color/type/spacing/radius; follow
  the `DESIGN.md` **Do's and Don'ts**. The mockup's whole purpose is to show *this system on this screen*.
- **Responsive intent if it matters.** If `design-decisions` says the screen has distinct small/large
  behavior, show the primary viewport (and optionally a second), per that intent.

## How many

Default **3** — enough for a genuine spread, few enough to compare at a glance. Two is fine for a small
screen; more than four dilutes the choice. When comparing the same screen across contexts, render the **same** 1–2
representative screens across the candidates so the systems (not the screens) are what's compared.

## After the pick

The chosen variant is a **reference for the implementer**, not the implementation. Record (feature mode)
what to carry forward — the layout, the hierarchy, the component usage — as the design-note on the task;
`implement-feature` builds the real, wired version against the same `DESIGN.md`. Don't promote a stub to
production as-is: it has no logic, no error handling, no tests.
