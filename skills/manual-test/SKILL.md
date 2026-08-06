---
name: manual-test
description: "Prepare the briefing a human needs in order to check the product by hand. Use as the last step of the release phase (run by release-product, after the audits) or standalone before a demo or an acceptance pass. Read-only: it proves nothing and changes nothing — it answers 'what do I poke, and how do I log in?' in advance. It works out how to bring the product up, which seeded users and data exist right now, what has been built and which journeys that covers with exact steps and real texts, how to trigger rare states through the project's own mock switches, and above all what genuinely needs a person — needs_human tasks, risky surfaces, and every task accepted as review: auto."
argument-hint: "[<feature / scenario in words> | empty = whole product]"
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/scripts/guard-write-scope.sh '*/.dev-skills/*' '/tmp/*' '/private/tmp/*' '/var/folders/*'"
---

# Manual Test Skill (the briefing for a hands-on pass)

Even with the suite green, a person still has to look at the product. A test proves only what somebody
thought to encode; whether the copy reads well, whether the layout survives a phone, whether this is the
feeling that was wanted — no machine decides that. And in this workflow the gap is wider than it looks:
a task whose diff held nothing hand-checkable is accepted with `review: auto`, which means **no human
has ever opened it** — and that is exactly where money, access, and deletion live.

The reason hands-on testing gets skipped is never disagreement. It is the blank moment in front of the
screen: *everything is built… so what do I poke, and how do I log in?* You remove that moment. You work
out what this project is and hand over a ready map — the command to bring it up, the seeded user to sign
in as, the journey and its steps, the switch that triggers the error state — plus an honest list of what
only a person can judge.

**You check nothing and you fix nothing.** The human does the poking; you prepare the ground so it takes
a minute to start.

## Inputs and outputs

- **Reads:** `.dev-skills/project-setup/verification.md` (bring-up, how to drive each surface,
  dummy-auth, seed and reset), the **flows** in `.dev-skills/project-spec/user-flows.research.md`, the
  **backlog** in `.dev-skills/build-plan/` (statuses, `review`, `spec_sync`, `origin`, acceptance
  criteria), the code (routes, screens, endpoints, sub-commands, mock switches), and — where it is cheap
  and safe — the **running product** itself.
- **Writes:** `.dev-skills/release/manual-test-brief.md`, and nothing else (enforced by a write-scope
  hook). Never code, tasks, spec, or data.

## Language & git

Respond and write the briefing in whatever language the user addressed you in, and think in it too.
Never translate code, commands, identifiers, paths, or the product's own on-screen texts.

Workflow vocabulary follows **`../_shared/glossary.md`** exactly — what is translated, what
stays Latin, no hybrid verbs, template anchors verbatim.

**One branch — the current one, normally `main`.** Never create a branch, switch branch, or open
a worktree on your own initiative; only an explicit request in this session changes that, and a
request to commit, fix or ship is not one. Full rule: **`../_shared/git-workflow.md`**.

## Focused mode (called with words)

An argument is the **goal of the pass** ("check the payment", "password recovery", a feature name). Then
do not inventory the whole product — compress the briefing to that one thing: what we are checking and
by which criteria (including its error branches), the one command to bring it up and the one
screen/endpoint to reach, which seeded user fits and in what state, the steps with the real texts, and
what is easy to break here. The stages below still run, but aimed at that feature. If the request could
mean two different features, ask one clarifying question rather than guessing. A neighbouring risk the
human will obviously miss gets one line, not a section.

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
Read how the project describes itself (`verification.md` first, then the root `CLAUDE.md` and README)
and determine the stack and the product type — that is what decides how the result is *observed at all*:
a web app in a browser at the configured port; an HTTP API through `curl` and its OpenAPI document; a
CLI by running the command with different flags; mobile in a simulator; desktop by launching the
binary; a library by its usage examples, since there is no UI to look at. Say what you determined in one
line so the human can correct you.

### Stage 1: Bring-up
Take the one-command bring-up, the addresses and ports, and the prerequisites from `verification.md`
(the contract `setup-dev-environment` wrote), falling back to the manifest and compose file. Then
**probe whether it is already up** — hit the port or the health endpoint; do not assume. If it is not
up, do not invent statuses: give the bring-up command first and mark the rest of the briefing as
"product not queried".

### Stage 2: Users and data — the state right now
Find the seeded accounts **with their credentials** and the fixtures, and the dummy-auth mechanism from
`verification.md`. Then, if the store can be queried cheaply and safely, show the **current** state
(balance, flags, row counts), compare it with the seed, and where they differ show **both** values
("now 7 · seed 10") plus the project's reset path. No seeded data at all → say so and point at how this
project expects a test account to be created.

### Stage 3: What is built and how to click it
Take status from the backlog (`done`, `in_progress`, `needs_human`) but **verify against reality** — the
code and the running product are the truth, a document can lag: actual routes, screens, endpoints,
sub-commands, and recent commits. Reduce it to **journeys**, using the flows doc for the steps and the
product's **real texts**; where there is no flow, derive the journey from the code. For each: is it
covered, which user to use, and the short path in steps. Mark partial coverage honestly.

### Stage 4: Rare states
The happy path shows itself; "error", "limit", "payment declined", "retry" do not until they are staged.
Find **this project's own mechanism** — the mock switches and error modes `verification.md` and the
external-service clients document, fixture modes, feature flags, dev-only pages, pre-seeded edge records
(expired, empty, someone else's, maximum size) — and give the exact command or toggle, **verified against
the code** rather than recalled. Never a live paid call.

### Stage 5: What needs a person
Separate out what no automated test closes:

- **`needs_human`** — tasks the loop escalated. What it is and what is actually required (often access,
  money, or an account rather than a click).
- **Seen only by machines** — every task accepted with **`review: auto`** that nevertheless has a
  human-facing surface (a screen, copy, money, deletion). This project marks them explicitly, so this
  list is exact rather than guessed: it is the work no person has ever opened.
- **Ahead of the spec** — `origin: adhoc` and `spec_sync: pending`: shipped behaviour the spec does not
  describe, so a spec-derived test may not exist for it.
- **Risky surfaces, always, whatever the tasks say** — money and payments · sign-in and access ·
  ownership and privacy (someone else's data) · deletion · external side effects · layout, copy, and
  mobile-only branches. Plus the code's own signals: `TODO`/`FIXME`, skipped tests, open findings.

Work whose whole diff is internal logic or config, fully proven by tests, does **not** go on this list.

### Stage 6: The briefing
Write `.dev-skills/release/manual-test-brief.md` and end the turn with it — five sections, each line
pointing at its source, real texts and addresses quoted verbatim:

1. **How to bring it up and observe it** — the command(s), addresses, mock mode (live calls vs stubs),
   the liveness check result, the reset path, the rare-state switches from Stage 4.
2. **Test users and data — state right now** — a table: who · credentials · what they hold (per the
   seed) · state now · which scenario they serve. Differences from the seed on a visible line.
3. **What is ready and how to click it** — by journey: covered or not, which user, the short path in
   steps with the real texts, how to reach the error branches.
4. **Needs a person** — the groups from Stage 5, each with what exactly to click.
5. **Worth checking by hand as well** — boundaries and stress cases, mobile and responsive states,
   cross-cutting rules (security, idempotency, refunds), with the risky surfaces first.

Then offer, in one line: walk one scenario together (browser, simulator, or command), or file anything
the human finds as a task through `/run-task`.

## Rules

1. **Read-only.** No code, no tasks, no spec, no data; no live or paid calls. Resetting the environment
   happens only if the human asks.
2. **Nothing hardcoded to a stack** and nothing from memory: every specific fact comes from this
   project's files or its running product.
3. **Proof is observed** — a status is a row from the store, liveness is the product's own answer. "The
   logs are clean" is not evidence. What you did not check, say you did not check.
4. **"Not found" is a valid answer.** Missing seed, flows, or health endpoint → degrade gracefully with
   what exists and name the gap; never fill it with something plausible.
5. **Check the anchors** — variable names, dev-only pages, commands, and paths are verified against the
   current code before being recommended; they move.
6. **The document may lag.** The truth about what exists is the code and the running product; show a
   divergence, never reconcile it silently.
7. **`review: auto` always goes on the human's list** when the work has a human-facing surface — that
   marking is the whole reason this skill exists.
8. **You prepare, you do not accept.** The briefing is a map, not a verdict, and not a substitute for
   the human's judgement.
9. **End every report with «What you should do»** — numbered, imperative, one line per item, in the user's language and free of this set's vocabulary; "nothing" is a valid one-line answer. Timings, where reported, must reconcile with their total. **`../_shared/build-pipeline/report-format.md`**.
