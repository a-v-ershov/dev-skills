# Frozen design decisions (shared — build & release pipelines)

The product's **visual decisions are settled once, in the spec, and are never re-opened by a skill or
an agent on its own initiative.** Colours, contrast, type scale, spacing, radii, motion, the icon set,
the kit's component look — all of it. `define-design-decisions` chooses the direction,
`setup-dev-environment` writes it into the committed root `DESIGN.md`, and from that moment the tokens
are **frozen**.

## Why this rule exists

An agent reading a design token can nearly always produce an argument for changing it — most often an
accessibility one, because contrast is the single visual property that has a published number attached.
Twice in the field, an audit and a refactor darkened a palette token to clear a WCAG ratio and shipped
it as a fix. Both were reverted by the owner with the same instruction: *put the design back, and record
that it is not to be touched.* The palette was chosen by hand, deliberately, with the ratio known.

A number in a standard is not permission. The design belongs to the owner; a computed ratio is an
input to their decision, not a substitute for it.

## The rule

**No skill and no agent changes a value under `## Frozen decisions` — or anything the design system
derives from it — unless the user asks for that change in this session.**

- **A finding is allowed. An edit is not.** Measure it, name it, say what it would cost and what the
  alternatives are — then leave the value alone. A contrast measurement is reported, never applied.
- **This is not severity-dependent.** A WCAG-A failure on a frozen token is still reported, not fixed:
  it is filed for the owner to decide, and its status is `needs_human`, not `rework`. The audits may
  rank it however the rubric says; ranking is not licence to edit.
- **Deriving is fine, re-deciding is not.** Building a new screen out of the frozen tokens is normal
  work. Introducing a token, a literal colour, or a "slightly adjusted" variant is not.
- **The owner's exception is per-session and explicit.** "Change the error colour" is an instruction;
  "make the product accessible" is not, and neither is silence.

## Who this binds

- **`implement-feature` / the implementer** — builds from the tokens, never edits them; a screen that
  seems to need a new token stops and asks.
- **`refactor`** — may replace a hardcoded literal *with the token that already matches it*; may not
  change what any token is worth.
- **`audit-product`** (and any audit that looks at the UI) — runs its accessibility pass, reports every
  failure with its measured number, and files a frozen-token failure as an owner decision. It never
  proposes the new value as a task for a developer to apply.
- **`write-tests`** — never asserts a specific token *value* as a requirement; test the rule ("the
  button uses the token"), not the hex.
- **`generate-mockups`** — explores arrangement within the system; never an alternative system.

## Where the freeze lives

The root `DESIGN.md` carries a `## Frozen decisions` section listing the frozen tokens and, for each,
one line on why it was chosen — including any known, accepted trade-off ("contrast 4.49 against a 4.5
target; chosen by hand, accepted"). An accepted trade-off written down once stops the next agent from
rediscovering it as a bug every release.

Changing the freeze is a spec change: `/define-design-decisions` (amend), then `setup-dev-environment`
rewrites `DESIGN.md`. That path exists, and it starts with the user asking for it.
