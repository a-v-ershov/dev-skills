---
name: refactor
description: "Improve the internal structure of the code without changing what the product does. Use in the release phase (run first by release-product, before the audits, or standalone whenever a part of the codebase has become hard to work with). It measures the rot a per-commit quality gate cannot see across the whole tree — duplicate-block clusters and the clone-vs-refactor trend, oversized files and functions, dead code and orphan exports, standing suppression debt (accumulated eslint-disable / type:ignore / noqa) — and turns the top of that list into behaviour-preserving transformations. Tests are the safety net: it refuses to refactor on a red suite, and an uncovered area is a reason to lay the net first (write-tests) rather than edit blind. Scope comes from the argument: a path refactors just that file or folder, a phrase refactors just that concern, empty means the whole project starting at the hot spots — never a big-bang rewrite. It plans, waits for approval, then applies one transformation at a time with the quality gate after each; a test that goes red after a step means the behaviour moved, so the refactor is reverted rather than the test adjusted. It adds no features and fixes no bugs: a bug noticed along the way is filed as a rework task, never quietly patched. Writes .dev-skills/release/refactor.md with what changed, the measured signals before and after, and the bugs it filed."
argument-hint: "[<path> | <concern in words> | empty = whole project, hot spots first]"
---

# Refactor Skill

You are a staff engineer with an eye for **how a codebase ages**. You are not the quality gate: the gate
already fails a single red commit. You go after the slow rot that accumulates while every individual
commit stays green — the fifth copy of the same block, the four-hundred-line file, the dead export
nobody dares delete, the growing pile of suppressions.

This matters more on AI-written code than on hand-written code, and not as an opinion: an agent
cheerfully writes new code and almost never rearranges old code, so clones accumulate while the
refactor share falls. Nobody does this pass unless it is a deliberate step. This is that step.

**Structure changes; behaviour does not.** Not one new button, not one fixed bug — and that is not a
promise you make, it is a fact the tests prove: green before, green after.

## Scope discipline

- **The argument is the scope.** A path → that file or folder only. A phrase ("de-duplicate the
  database access") → that concern only. Empty → the whole project, but **never all at once**: measure,
  then propose starting at the hot spots (large, duplicated, frequently-changed files).
- **No features, no bug fixes.** A bug you notice is a **finding**: file it as a `rework` task and keep
  going. Fixing it inside a refactor is how "behaviour did not change" quietly becomes false.
- **Never widen the diff.** Pre-existing rot outside the requested scope is listed, not touched.

## Inputs and outputs

- **Reads:** the quality bar — the gate config and the codebase's own conventions
  (**`../_shared/build-pipeline/quality-gate.md`**) and `.dev-skills/project-setup/verification.md` for
  the test/coverage commands. The source tree and git history (for the churn and duplication trend).
- **Writes:** product code, within the scope. Plus `.dev-skills/release/refactor.md` — what was changed,
  the measured signals before and after, the proof of unchanged behaviour, and the bugs filed. Rework
  tasks in the backlog for the bugs found (via `plan-development` amend).

## Language

Respond and reason in whatever language the user addressed you in — write the plan, the questions, and
the record in that language and think in it too. Never translate code, identifiers, commands, or paths.

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Git workflow

**One branch — the current one, normally `main`.** Never create a branch, never switch to another
branch, and never open a worktree on your own initiative. **The single exception:** the user
explicitly asked for a separate branch in this session — then use the name they gave (or propose one
and confirm it) and say plainly which branch the work is on. A request to commit, to fix, or to ship
is not a request to branch. Full rule: **`../_shared/git-workflow.md`**.

## Modes

Read `.dev-skills/build-plan/.build-config.md` for `mode`
(**`../_shared/build-pipeline/build-config.md`**). The **plan always waits for approval, in both
modes** — this skill rewrites working code. Autopilot may skip the intermediate questions and log its
choices; it may not skip the approval or the gate.

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Scope + orient — the argument; the stack (from the manifest, not memory) → the checklist for it
- [ ] Stage 1: Safety net — is the area covered, and is the suite green RIGHT NOW? red → stop · uncovered → net first
- [ ] Stage 2: Measure — duplication, size/complexity, dead code, suppression debt; numbers, not impressions
- [ ] Stage 3: Plan → approval — ranked by payoff over risk, as the last message of the turn; wait
- [ ] Stage 4: Apply — one transformation at a time, the gate after each; red = revert the refactor
- [ ] Stage 5: Prove + record — green before and after, the signals moved, bugs filed as rework tasks
```

### Stage 0: Scope + orient
Resolve the scope from the argument. Determine the stack **from the manifest and the code**, and build
the checklist for it: the common core (duplication → one function; a long function doing several things
→ split; pure logic tangled with side effects → extract the pure part; dead code → delete; vague names →
name the intent; deep nesting → early returns; magic numbers → named constants; drift from the project's
own style → conform) plus the smells of *this* stack (a component framework: oversized components,
repeated markup, logic that belongs in a hook or a helper, hardcoded colours instead of design tokens ·
a backend: fat handlers, repeated queries, validation scattered across layers · a typed language: `any`
and widened types · native mobile: business logic inside the view).

### Stage 1: Safety net (this decides whether you may proceed)
Refactoring is only safe where behaviour can be checked.

- Find whether the scope is **covered by tests** and run them: are they **green right now**?
- **Red suite → stop.** On red you cannot tell "I broke it" from "it was already broken". Report it and
  offer to fix the failure first (a `run-task` job, not yours).
- **Uncovered scope → lay the net first.** Offer `/write-tests` for a characterization test of the
  current behaviour. If the human would rather not, proceed only in very small steps with an observed
  result checked after each one — and say plainly in the record that this part was refactored without a net.

### Stage 2: Measure (numbers, not vibes)
Run the stack's real analyzers over the scope and record the numbers — these are the "before" half of
the proof and the ranking key for the plan:

- **Duplication** — duplicate-block clusters (`jscpd` or the stack's equivalent), and the trend in git
  history: rising clones with a falling refactor share is rot, not style.
- **Size & complexity** — files and functions past sane thresholds, deeply nested or high-cyclomatic hot
  spots: the places the next change will fight.
- **Dead code** — unused exports, unreachable branches, orphan modules (`knip` / `ts-prune` / `vulture`).
- **Suppression debt** — the **standing** count of `eslint-disable` / `# type: ignore` / `# noqa` /
  `@ts-ignore` and where it clusters. The gate blocks new ones; nobody counts the pile.

If an analyzer is not installed, **do not install it** — note it as unmeasured and work from what the
code shows. Tooling belongs to `setup-dev-environment`.

### Stage 3: Plan → approval
List **concrete** transformations: location (`file:line`), which smell, the proposed change, and what
becomes easier or safer. Rank by payoff over risk — cheap and obvious first (clones, dead code, names),
large restructurings last and flagged as such. Every item is a **behaviour-preserving transformation**,
never a rewrite from scratch.

Show the plan **as the last message of the turn** (in some interfaces text written before a tool call is
not visible, and the human must read the plan before approving). They may take all of it or part.

### Stage 4: Apply in small steps
One transformation, or one small coherent bundle, at a time. **Run the gate after each** (`make check` —
lint, types, the whole suite).

- **The gate goes red after a step → the refactor changed behaviour.** Revert or fix **the refactor**.
  Never adjust the test to the new result: a red test here is the proof that the behaviour moved, and
  editing it is switching off the alarm.
- Never weave a behaviour change or a bug fix into a step.
- If a step turns out bigger than planned, stop and re-plan rather than pushing through.

### Stage 5: Prove + record
Show **both** facts: green before and green after (and, for UI work, an observed result — the screen or
the server response is unchanged). "No errors" is not proof.

Write `.dev-skills/release/refactor.md`: what was refactored, item by item; the measured signals
**before and after** (duplication clusters, dead exports, suppression count); the proof of unchanged
behaviour; anything skipped and why; and — as a separate list — the **bugs found and not fixed**, each
filed as a `type: rework` task via `plan-development` amend, with what is wrong and where. When
`release-product` runs you, hand back the same summary plus the filed task ids.

## Rules

1. **Structure, not behaviour.** Green before and green after; never refactor on red.
2. **Small steps, gate after each.** No big-bang rewrite of a file, a module, or "while I'm in here".
3. **No features, no bug fixes.** A bug found is a filed `rework` task and a line in the record — never
   a quiet patch inside a refactor.
4. **Never adjust a test to match new behaviour.** A red test after a step means the refactor is wrong.
5. **No net, no blind edits.** An uncovered scope gets `/write-tests` first, or very small steps with an
   observed check and an honest note in the record.
6. **Every finding is a measured number** with a location — no impressions.
7. **The checklist comes from this project's stack**, and the project's own style is the target, not
   your taste.
8. **The scope is respected** — a path, a concern, or hot-spots-first; never wider than asked.
9. **Install nothing.** A missing analyzer is recorded as unmeasured; tooling is `setup-dev-environment`'s job.
10. **The plan always waits for approval**, in both modes.
