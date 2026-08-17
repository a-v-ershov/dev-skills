# The plan's four sections, and what the smoke-test must prove

Stage 2 and Stage 5 of `setup-dev-environment` in full. Read each when you reach it.

---

## Stage 2 — the plan's four sections
Compose `.dev-skills/project-setup/setup-plan.md` (template: `setup-templates.md` §1) as a
checklist in four sections, each item carrying **action · provenance (component/ADR) · reversibility ·
idempotency note · already-present?**:

- **(A) Global installs** — toolchains, Docker, CLIs the stack needs that aren't on PATH. The plan
  shows the exact command. *Gated — never auto-run.*
- **(B) Repo scaffolding** — everything under "Repo files", "The quality gate" and "Environment
  access…" in the Outputs above. When the spec has `.dev-skills/project-spec/code-style.md`, its
  `## Enforcement` section is part of the gate config: wire each tool + rule row into the
  linter/formatter/type-checker configs behind `make check-fast` (one plan item per tool, provenance
  = the guide), so the style guide's enforceable subset is enforced by the harness, not by prose.
  *Auto-applicable (repo-local).*
- **(C) AI tooling** — `.claude/settings.json` (the **permissions** block the loop needs plus a
  `permissions.deny` list excluding generated/build/vendor trees, and **no gate-running Stop /
  PostToolUse hook**), the **code-intelligence LSP plugin(s)**, the stack plugins / MCP servers the
  dev-architecture named. *Config files auto; plugin / MCP / LSP installs gated.* Recipes:
  `setup-templates.md` §5.
- **(D) Manual-only** — real secrets/API keys, cloud accounts, licenses. *Listed for the human.*

---

## Stage 5 — what the smoke-test must prove
Run the one-command bring-up and prove it is actually **green**: the stack starts, the app is reachable
at the documented URL/port, seed data is present, and an agent can drive one basic flow and observe a
real outcome (a page renders / a health endpoint returns 200 / a seeded row is queryable). "No error in
the logs" is not proof.

Then prove the gate has teeth, in two ways:
- **Static gate blocks.** `make check` is green on the clean tree, and a deliberately-introduced **type
  or lint** error makes `make check-fast` fail and the pre-commit hook block the commit (then revert
  it). Use a static error, not a failing test — the hook does not run tests.
- **The scoped run really selects.** `make test-scoped SCOPE=<one existing test path/pattern>` runs
  those tests and visibly *fewer* than the full run. A "scoped" target that quietly runs everything is
  the failure mode to catch here — it is the command the whole build loop leans on.

If any of this fails, report what failed and offer to fix it; the environment is not "done" until it
is green.

---

## Stage 5b — the design system, in full
Read `.dev-skills/project-spec/design-decisions.research.md`. A no-UI project, or **Design system /
Needed? = no** → **skip** this stage, note it in the setup log, go to Stage 6. A root `DESIGN.md` that
already exists → leave it alone and note that (idempotent).

Otherwise write it **directly from the spec** — the tokens come from the installed kit's real theme
values or from the recorded brand intent, the format and the full procedure are in
**`design-md-format.md`** ("Writing DESIGN.md during setup"), the per-kit token mapping in
`adoption-recipes.md`. Prove it renders on one real screen, screenshot it into the setup
log, and write the short `.dev-skills/project-setup/design-system.md` record. The tokens land under
`## Frozen decisions` — **`../../_shared/build-pipeline/design-freeze.md`**.

Deviating from the spec's design decisions here is out of scope: if the kit is genuinely wrong, stop
and say so — that is a spec change, not a setup call.
