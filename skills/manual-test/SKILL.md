---
name: manual-test
description: "Prepare the briefing for a human's hands-on check: bring-up, seeded users and their data now, built journeys with steps and real texts, rare-state switches, and above all what needs a person — review: auto tasks, needs_human, risky surfaces. Read-only. Last release step, or standalone before a demo. Writes .dev-skills/release/manual-test-brief.md."
argument-hint: "[<feature / scenario in words> | empty = whole product]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Manual Test Skill (the briefing for a hands-on pass)

Even with the suite green, a person has to look. A task with nothing hand-checkable in its diff is
accepted with `review: auto`, so **no human has ever opened it** — and that is where money, access and
deletion live. You remove the blank moment (*what do I poke, and how do I log in?*) with a ready map,
plus an honest list of what only a person can judge.

## Inputs and outputs

- **Reads:** `.dev-skills/project-setup/verification.md` (bring-up, dummy-auth, seed, reset); the
  **flows** in `.dev-skills/project-spec/user-flows.research.md`; the **backlog** in
  `.dev-skills/build-plan/` (statuses, `review`, `spec_sync`, `origin`, acceptance criteria); the code
  (routes, screens, endpoints, mock switches); where cheap and safe, the **running product**.
- **Writes:** `.dev-skills/release/manual-test-brief.md` only (write-scope hook).

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands, paths or the product's own on-screen texts. Commit messages are
always English. **One branch — the current one** (normally `main`): never branch, switch or open a
worktree unless the user explicitly asked in this session — **`../_shared/git-workflow.md`**.

## Focused mode (called with words)

An argument is the **goal of the pass** ("check the payment", a feature name): aim every stage at it,
no product inventory — its criteria and error branches, the one bring-up command and screen/endpoint,
the fitting seeded user and state, steps with real texts, what is easy to break. Could mean two
features → ask one clarifying question. A neighbouring risk the human will miss gets one line.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Intake — mode (whole product / one feature); what this project is: stack, surfaces, where tasks and seed live
- [ ] Stage 1: Bring-up — the command, the address, the prerequisites; is it already running? (probe, don't assume)
- [ ] Stage 2: Users & data — the seeded accounts, and their state RIGHT NOW versus the seed
- [ ] Stage 3: What is built — journeys that are covered, with steps and the product's real texts
- [ ] Stage 4: Rare states — the project's own mock switches for errors, limits, declines
- [ ] Stage 5: What needs a person — needs_human · review: auto · ahead of the spec · risky surfaces
- [ ] Stage 6: The briefing — five sections, written to .dev-skills/release/manual-test-brief.md and shown
```

### Stage 0: Intake
Read `verification.md`, then the root `CLAUDE.md` and README. Determine stack and product type — it
decides how the result is *observed*: browser; `curl` + the OpenAPI document; running the CLI; a
simulator; launching the binary; a library's usage examples. State it in one line so the human can
correct you.

### Stage 1: Bring-up
Bring-up command, addresses, ports and prerequisites from `verification.md` (the contract
`setup-dev-environment` wrote), else the manifest and compose file. **Probe whether it is already up**
(port or health endpoint). Not up → the bring-up command first, the rest marked "product not queried".

### Stage 2: Users and data — the state right now
Seeded accounts **with credentials**, fixtures, the dummy-auth mechanism. Store cheaply and safely
queryable → the **current** state (balance, flags, row counts) against the seed, **both** values where
they differ ("now 7 · seed 10"), plus the reset path. No seed → say so; point at how this project
expects a test account to be created.

### Stage 3: What is built and how to click it
Status from the backlog (`done`, `in_progress`, `needs_human`), **verified against** the actual
routes, screens, endpoints, sub-commands and recent commits. Reduce to **journeys** with the flows
doc's steps and the product's **real texts** (no flow → derive it from the code): covered or not,
which user, the short path. Mark partial coverage honestly.

### Stage 4: Rare states
Rare states show only when staged. Find **this project's own mechanism** —
mock switches and error modes (`verification.md`, the external-service clients), fixture modes,
feature flags, dev-only pages, pre-seeded edge records (expired, empty, someone else's, maximum size)
— and give the exact command or toggle.

### Stage 5: What needs a person
- **`needs_human`** — what each escalated task requires (often access, money or an account).
- **Seen only by machines** — every **`review: auto`** task with a human-facing surface (screen, copy,
  money, deletion); the marking makes this list exact.
- **Ahead of the spec** — `origin: adhoc` and `spec_sync: pending`: behaviour no spec-derived test
  may cover.
- **Risky surfaces, always** — money · sign-in and access · ownership and privacy · deletion ·
  external side effects · layout, copy, mobile-only branches; plus `TODO`/`FIXME`, skipped tests, open
  findings.

Internal logic or config fully proven by tests is **not** listed.

### Stage 6: The briefing
Write `.dev-skills/release/manual-test-brief.md` and end the turn with it — five sections, each line
pointing at its source, real texts and addresses verbatim:

1. **How to bring it up and observe it** — command(s), addresses, mock mode (live vs stubs), liveness
   result, reset path, the Stage 4 switches.
2. **Test users and data — state right now** — table: who · credentials · what they hold (per seed) ·
   state now · which scenario they serve; differences from the seed on a visible line.
3. **What is ready and how to click it** — per journey: covered or not, which user, the short path
   with real texts, how to reach the error branches.
4. **Needs a person** — the Stage 5 groups, each with exactly what to click.
5. **Worth checking by hand as well** — boundaries and stress cases, mobile and responsive states,
   cross-cutting rules (security, idempotency, refunds), risky surfaces first.

Then offer in one line: walk one scenario together (browser, simulator or command), or file a finding
as a task through `/run-task`.

## Rules

1. **Read-only** — no code, tasks, spec or data; no live or paid calls; reset the environment only if
   the human asks.
2. **Nothing hardcoded to a stack**, nothing from memory — every fact comes from this project's files
   or its running product.
3. **Proof is observed** — a status is a row from the store, liveness the product's own answer; "the
   logs are clean" is not evidence. Say what you did not check.
4. **"Not found" is a valid answer** — missing seed, flows or health endpoint → degrade gracefully,
   name the gap, never fill it with something plausible.
5. **Check the anchors** — variable names, dev-only pages, commands and paths are verified against the
   current code before you recommend them.
6. **The document may lag** — code and running product are the truth; show a divergence, never
   reconcile it silently.
7. **`review: auto` always goes on the human's list** when the work has a human-facing surface.
8. **You prepare, you do not accept** — check nothing, fix nothing; the briefing is a map, not a
   verdict.
9. **End every report with «What you should do»** (**`../_shared/build-pipeline/report-format.md`**).
