# Frozen design decisions (shared — build & release pipelines)

The product's **visual decisions are settled once, in the spec, and never re-opened by a skill or an
agent on its own initiative** — colours, contrast, type scale, spacing, radii, motion, the icon set,
the kit's component look. `define-design-decisions` chooses the direction, `setup-dev-environment`
writes it into the committed root `DESIGN.md`, and from then on the tokens are **frozen**.

## Why this rule exists

An agent can nearly always argue for changing a token — usually on accessibility, since contrast has a
published number. Audits and refactors have darkened hand-chosen palette tokens to clear a WCAG ratio
the owner already knew, and were reverted. A number in a standard is an input to the owner's decision,
not permission.

## The rule

**No skill and no agent changes a value under `## Frozen decisions` — or anything the design system
derives from it — unless the user asks for that change in this session.**

- **A finding is allowed. An edit is not.** Measure it, name it, say what it would cost and what the
  alternatives are — then leave the value alone. A contrast measurement is reported, never applied.
- **Not severity-dependent.** A WCAG-A failure on a frozen token is still reported, not fixed: filed for
  the owner, status `needs_human`, not `rework`. Ranking is not licence to edit.
- **Deriving is fine, re-deciding is not.** Building a new screen from the frozen tokens is normal work;
  introducing a token, a literal colour, or a "slightly adjusted" variant is not.
- **The owner's exception is per-session and explicit.** "Change the error colour" is an instruction;
  "make the product accessible" is not, and neither is silence.

## Who this binds

- **`implement-feature` / the implementer** — builds from the tokens, never edits them; a screen that
  seems to need a new token stops and asks.
- **`refactor`** — may replace a hardcoded literal *with the token that already matches it*; may not
  change what any token is worth.
- **`audit-product`** (and any audit that looks at the UI) — reports every accessibility failure with
  its measured number and files a frozen-token failure as an owner decision; never proposes the new
  value as a developer task.
- **`write-tests`** — never asserts a specific token *value*; test the rule ("the button uses the
  token"), not the hex.
- **`generate-mockups`** — explores arrangement within the system; never an alternative system.

## Where the freeze lives

The root `DESIGN.md` carries a `## Frozen decisions` section listing the frozen tokens, each with one
line on why it was chosen — including any accepted trade-off ("contrast 4.49 against a 4.5 target;
chosen by hand, accepted"), so no agent rediscovers it as a bug.

Changing the freeze is a spec change, started only by the user: `/define-design-decisions` (amend),
then `setup-dev-environment` rewrites `DESIGN.md`.
