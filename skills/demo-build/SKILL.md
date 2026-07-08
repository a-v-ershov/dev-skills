---
name: demo-build
disable-model-invocation: true
description: "Webinar DEMO variant of the build loop — builds ONE feature with the real implementer/verifier two-agent mechanism, for a live before/after demo. Use only for the vibe-coding course demo, NOT for real builds (that's build-product). It skips the kanban planning entirely: it writes a single throwaway task file for the feature you name, spawns the real implementer agent to build it, then spawns the SEPARATE, fresh verifier agent to independently find bugs and hand them back — the whole point being to SHOW the second agent catching real bugs in the first agent's work, versus a naive 'it works, ship it'. HARD-CAPPED at 2 implement↔verify iterations (usually 1 is enough) so it fits a webinar slot. Reuses the genuine agents/mechanism — only the surrounding kanban is stripped."
argument-hint: "[feature description]"
---

# Demo Build Skill (webinar variant — ONE feature, real two-agent loop)

You are running the **demo** version of the build phase for a live webinar. The payoff of this act is
watching the **independent verifier find real bugs** in the implementer's work — the honest mechanism,
not a slide. The "before" (a co-host prompting *"add feature X"* and accepting "it works") is done live
by the co-host; your job is the "after".

This is **not** `build-product`. You skip the kanban backlog and its planning. You build **one**
feature: create a single throwaway task file, run the real agents on it, cap the loop tight, done.

## Language

Respond and reason in whatever language the user addressed you in. Never translate code, identifiers,
commands, or file paths. (Commit messages are always English — but this demo does not commit unless
the user asks.)

## What stays REAL (do not fake this)

- The **`implementer`** agent (`subagent_type: implementer`, fresh) actually builds the feature.
- The **`verifier`** agent (`subagent_type: verifier`, a **separate** fresh agent) actually authors
  adversarial tests, drives the stack, and reports pass/fail. Its independence is the whole demo — never
  let the implementer self-approve.
- On a FAIL, findings go back to the **same** implementer agent (it keeps its context) for one more round.

## Hard bounds (timed demo)

- **max 2 implement↔verify iterations.** Usually 1 is enough: build, then one verify pass that surfaces
  bugs. At the cap with a criterion still failing → mark it `needs_human` and stop; narrate that the real
  loop goes to 4 and escalates to a human. **Never** run a long loop live.
- **One feature only.** No planning, no second task, no dependency graph.
- **No commit** unless the user explicitly asks.

## Prerequisites (check fast, fix minimally)

- **A verification contract** — `.buildloop/project-setup/verification.md` (how to bring the stack up +
  drive/prove a surface). The verifier **cannot run without it**. If it's missing: either the user has
  already run `setup-dev-environment` on the demo project, or you write a **minimal** one inline from
  what you can detect (the dev-server command, how to hit the UI/API, how to run tests) — just enough
  for the verifier to drive the stack. Don't build a full setup; this is a demo.
- **A slim spec** — `.buildloop/project-spec/product-requirements.research.md` (from `demo-spec`), so the
  task can trace to a real feature + acceptance criteria. If absent, derive one acceptance criterion
  inline from the feature description.
- **`.buildloop/build-plan/.build-config.md`** — write it if absent: `mode: interactive`,
  `max_verify_iterations: 2`.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Prereqs — ensure verification.md + config (max_verify_iterations: 2); read the slim spec if present
- [ ] Stage 1: One task — write a single task file with a clear Description + 2–3 acceptance criteria (incl. an error path)
- [ ] Stage 2: Implement — spawn the implementer agent (fresh) on that task; it builds + self-checks the happy path
- [ ] Stage 3: Verify — spawn the SEPARATE verifier agent; it authors adversarial tests, drives the stack, finds bugs
- [ ] Stage 4: One re-round (if FAIL) — hand findings back to the SAME implementer, verify again; cap at 2
- [ ] Stage 5: Close — report the verdict + surface the bugs the verifier caught; say the real loop goes to 4 + human
```

### Stage 0: Prereqs
Ensure the verification contract and config exist per **Prerequisites** above. Read the slim
`product-requirements.research.md` if `demo-spec` produced it. Get the time for the task's `created`
(`date -u +%Y-%m-%dT%H:%M:%SZ`).

### Stage 1: One throwaway task
Create `.buildloop/build-plan/tasks/` if absent and write **one** task file `T001-<slug>.md` following
the schema in `../_shared/build-pipeline/backlog-format.md` (`type: feature`, `status: todo`,
`blocked_by: []`, `verify_attempts: 0`). Give it:
- a concrete `## Description` (what to build, where it fits, the relevant spec section),
- **2–3 acceptance criteria** — and make at least one a **negative/error path** (empty input, wrong
  input, unauthorized), because that's where the verifier tends to catch the implementer's happy-path
  bias, which is exactly the moment worth showing.
Pick the feature so the difference is visible — not so trivial both approaches nail it. A form with
validation, an auth-gated resource, or anything with an obvious error case works well.

### Stage 2: Implement
Set the task `in_progress`, then **spawn the `implementer` agent** (`subagent_type: implementer`, fresh,
clean context — it preloads `implement-feature`). It builds the feature on the current branch, self-checks
the happy path, gets `make check` green, and logs what it did. It does **not** commit or self-verify
adversarially — that's the next agent.

### Stage 3: Verify (the money shot)
**Spawn the `verifier` agent** (`subagent_type: verifier`, a **separate** fresh agent — it preloads
`verify-feature`). It starts from the acceptance criteria, authors adversarial tests (especially the
error path), drives the real stack, and proves each criterion with an observable outcome. Let its
findings show on screen — this is the act's payoff. It bumps `verify_attempts`.

### Stage 4: One bounded re-round
- **PASS** → report it; the feature is demo-done. (Do not commit unless asked.)
- **FAIL** → hand the specific findings back to the **same** `implementer` agent (keep its context) for
  one fix round, then run the verifier once more. `verify_attempts` is now at the cap (2).
- **Still failing at the cap** → set the task `needs_human`, and narrate: the real `build-product` caps
  at 4 and escalates to a human rather than looping forever. Stop.

### Stage 5: Close
Report the verdict and, plainly, **the bugs the verifier caught that a naive "it works" would have
shipped** — that contrast is the whole point. Note that in a real build this runs across a full kanban
backlog, task after task, each independently verified, with a checkpoint commit per task.

## Rules

1. One feature, one throwaway task — no kanban planning, no second task.
2. Real agents: implementer builds, the **separate** verifier finds bugs; never let the implementer self-approve.
3. Hard cap at 2 iterations; at the cap → `needs_human`, stop. Never loop live.
4. The verifier needs `verification.md` — ensure a minimal one exists before Stage 3.
5. Include a negative/error acceptance criterion — that's where the demo bug usually surfaces.
6. Don't commit unless the user asks; close by surfacing the caught bugs.
