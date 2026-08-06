# Elicitation topics (define-design-decisions)

The full Stage 1 topic catalogue. Read it when you reach the stage; the `SKILL.md` carries the
shape and the order.

---

## Stage 1 in full
**Interview technique — `../../_shared/spec-pipeline/elicitation-method.md`** (read it): one thread at
a time, a recommended answer on every question, push past the first answer, mirror back to confirm.
When a fork is blocked on context only the user holds, invoke `gather-context` scoped to it. Work
the design decisions across five dimensions:
1. **Design system** — does the product need one? If yes, the *intent* (type scale, color approach,
   spacing system, motion stance) and the **component strategy**: adopt an existing library vs
   bespoke vs hybrid, and why. Decisions and direction, NOT concrete tokens or values. If the
   brief records a **design-taste preference**, treat it as a **soft prior** here — bias toward it,
   but let the product's needs and the category conventions decide; log it as a fork with
   `Source = preference`.
   **When the strategy is "adopt", name the kit here** — this is the decision, not a build-time
   detail, because it fixes a dependency and constrains what the screens can be. Pick it on three
   criteria, in this order:
   - **Coverage** — walk the key-screen inventory (dimension 2) for the components the product
     actually needs (data table with sorting, rich-text editor, date picker, command palette, toast,
     skeleton…). A kit missing a component the product leans on means hand-building it, which
     defeats the consistency the kit was for. Say so out loud rather than discovering it in build.
   - **Platform fit** — the kit must target the platforms from dimension 3.
   - **Ubiquity** — the more widely used the kit, the more reliably an AI agent writes against it.
     Prefer boring and common over novel.
   Also settle two decisions that travel with it: the **icon set** — one for the whole product,
   mixing two shows immediately — and the **theming approach** (start from a ready-made theme of
   that kit vs author tokens from the brand intent). Present the kit and the icon set as **closed
   forks with a recommendation first** (`AskUserQuestion`), each option one line of consequence.
   A kit already present in the repo's dependencies is the default — replacing it is a
   rewrite of every screen and needs the user's explicit decision (log it as drift).
   This dimension is the input `setup-dev-environment` builds `DESIGN.md` from; it does not re-open it.
2. **Key-screen inventory** — the set of screens/surfaces the product has, drawn from the flows.
   Per screen: name, the flow(s) it serves, its job. Structure and purpose, not layout.
3. **Viewport & platform behavior** — target platforms (web/responsive, iOS, Android, desktop) and
   the per-viewport intent for the key screens (what's primary on small vs large); platform
   conventions to honor.
4. **Media & connectivity** — media-heaviness (images/video/audio, at what scale), offline /
   low-connectivity expectations, real-time / live-update needs. Each is flagged as an
   architecture input.
5. **Accessibility** — the WCAG target (A / AA / AAA) and any specific requirements.

- **interactive:** ask, one dimension at a time; do not slide into pixel design.
- **autopilot:** choose each from the product spec + flows + (stage 2) conventions + best judgment;
  record each material choice in the Forks / Decisions log with rationale, confidence, source. Mark
  uncertain ones `Needs human confirm? = yes`.

---

## What the reviewer probes
Delegate to the `spec-reviewer` agent (offline — it reads the draft and the prior docs, not the web)
to find inconsistencies + gaps. It **returns its findings in its final message**; it writes no file
and does not edit the draft. Method + return format:
**`../../_shared/spec-pipeline/review-method.md`** and `review-format.md`. For this phase the reviewer
especially probes: a design decision that silently forces a costly architecture but isn't flagged as
an architecture input; a key screen with no flow (or a flow with no screen); a missing accessibility
target; media/offline/realtime implications left unsurfaced; a design system absent where the
category demands one (or bespoke where adopting a library would do); **an adopted UI kit that
doesn't cover a component the key screens lean on, a kit that doesn't target one of the stated
platforms, more than one icon set, or a "we'll adopt a library" with no kit actually named**; and
pixel/mockup/copy detail that leaked in (out of scope — that's implementation).
