# Four more lenses — for a skill set with shared methodology and pipelines

Read this alongside `rubric.md` whenever a target belongs to a set like **dev-skills**: skills that
share `_shared/*.md` methods, hand work to named agents, run under an orchestrator, and produce
documents from templates. The six general lenses ask *how the run went*; these four ask *whether the
set still holds together*.

---

## Lens A — Invariants of the set

These are stated once, in the set's own documentation, and every skill repeats a compact copy. A
skill that breaks one is a 🔴 even when the output looked fine: the same wording will break it again.

| Invariant | Where it is stated | What betrays a breach |
|---|---|---|
| **One branch — the current one** | `_shared/git-workflow.md` + every skill's `## Git workflow` | the digest's tripwire `branch / worktree created`, with no user turn asking for it |
| **Respond in the user's language** | `skills/CLAUDE.md`, each `## Language`, `_shared/glossary.md` | an English report answering a Russian prompt; a subagent replying in the wrong language (the skill didn't pass the rule down); transliterated verbs («закоммитить», «зафайлить») or a translated structural anchor (`## Источники` instead of `## Sources`) |
| **Commit messages in English** | `commit/SKILL.md`, `skills/CLAUDE.md` | the tripwire `non-English commit message` |
| **No attribution trailers** | `CLAUDE.md`, the `commit-msg` hook | the tripwire `AI attribution trailer` |
| **An audit never fixes or installs** | `_shared/release-pipeline/audit-method.md` | an `audit-*` run window containing an `npm install`, or a write to product code in the files-written table |
| **Write scope per role** | each skill's `hooks:` guard | a blocked-write error in the errors table (the guard worked, but the skill tried) — or a write outside the scope that the guard's globs failed to catch |
| **The version is the user's to bump** | `CLAUDE.md` → *Versioning* | a `⚠︎ version-carrying manifest` row in the files-written table with no user turn asking for a bump |
| **Sequential build, parallel only for read-only audits** | `skills/CLAUDE.md`, `build-tasks`, `release-product` | two implementers in flight at once; three read-only audits run one after another |

**Careful:** a tripwire is a signal, not a verdict. Find the user turn that authorized it before
writing the finding; if the user asked, there is no finding — at most a note that the skill should
have said which branch the work landed on.

---

## Lens B — Artifact fidelity: what it produced vs the template it was written from

Almost every skill in this set writes a document. The template is the contract, so the artifact is
evidence about the skill's wording — and unlike the transcript, it survives a compaction.

Open the artifact and its template side by side:

| Artifact | Template / format | Look for |
|---|---|---|
| `.dev-skills/project-spec/*.research.md` | `_shared/spec-pipeline/output-format.md` | a missing or empty `## Sources`; an unfilled `## Forks / Decisions log`; a brownfield run with no `## Divergences (code vs intended)` |
| `.dev-skills/project-spec/*.summary.md` | `output-format.md` + `summary-template.md` | the human report missing `## Decide — what I need from you` or `## Risks`; a summary as long as the research doc |
| `.dev-skills/build-plan/tasks/*.md` | `_shared/build-pipeline/backlog-format.md` | tasks with empty `acceptance`; an orphan `traces_to`; a `status` the run never moved off `in_progress`; a missing `timings` block on a task that left the board; an empty `## Log` on a task that was verified |
| `.dev-skills/release/*.md` | `_shared/release-pipeline/report-template.md` | findings with no evidence link; no verdict; a 🔴 with no filed task id |
| `DESIGN.md`, `.dev-skills/project-setup/*.md` | `setup-dev-environment/references/*` | tokens decided in the spec but absent here; a `verification.md` with no bring-up command |

**Rule for turning this into a finding:** a section the template requires and the output lacks is a
defect *in the skill's wording*, not in the run — and the fix is nearly always structural. The usual
cause is that the section is described in the skill's prose but never named in its copyable
checklist, so nothing forces it. Quote both: the template's requirement and the checklist that
doesn't mention it.

The `timings` block is also a cross-check on the speed lens: compare the recorded per-stage seconds
with the run window in the digest. A `verify` stage costing more than `build`, repeatedly, is a
finding about `verification-method.md`, not about one task.

---

## Lens C — Orchestration and hand-off

The set's structure is *orchestrator → sub-skill → agent*. Most expensive defects live in the seams.

**Signals:**

- **The orchestrator duplicated the sub-skill.** The run window shows the orchestrator doing the work
  itself (reading the spec, writing the doc) instead of invoking the sub-skill via the Skill tool.
  The convention is "conduct, don't duplicate" — the finding is the orchestrator's wording that
  re-states a procedure it should delegate.
- **A gate passed silently.** A hard gate (spec phase), the human acceptance step (`run-task`), the
  confirmation before `cut-release` — each must show a user turn between the skill's report and the
  next tool call. None in the window → the gate is stated in prose, not in the checklist.
- **The mode was ignored.** `mode: interactive` should stop at each gate; `mode: autopilot` should
  log each decision instead. A run that neither stopped nor logged means the config key is read once
  at intake and never referenced again in the procedure.
- **The hand-off lost context.** A subagent re-derives what the caller already knew (re-reads the
  whole spec, re-runs `git status`, re-discovers the stack) because the spawn prompt passed a task id
  instead of the facts. The fix belongs in the *caller's* spawn instructions, not in the agent.
- **The hand-off passed too much.** A 400-line prompt where the agent then reads the same files
  anyway.
- **Loop discipline broke.** More than one fix round; more than 8 tasks in a `build-tasks` run; an
  audit re-run more than once; a task looping instead of going to `needs_human`. These are stated
  limits — quote the limit and the count.
- **The env lease was skipped.** Two skills driving the running stack at once
  (`_shared/build-pipeline/env-access.md`).

**Proves it:** the invocation table (which skill called which), the run windows, the subagent prompts
in the transcript, and the count against the stated limit.

---

## Lens D — Placement: which file the fix belongs in

A correct finding pointed at the wrong file makes the set inconsistent. Decide the owner before
writing the proposal:

| The behaviour is… | The fix goes in |
|---|---|
| shared by several skills (research budget, review format, severity, backlog fields, quality gate, env access, propagation) | `_shared/<pipeline>/<method>.md` |
| that one skill's own procedure or checklist | `skills/<name>/SKILL.md` |
| a long template, rubric or recipe the skill reads on demand | `skills/<name>/references/*.md` |
| how an agent is briefed or what it may touch | `agents/<name>.md` (thin wrapper) — but if the *procedure* is wrong, its preloaded skill owns it |
| an invariant of the whole set (language, glossary, branch, versioning, layout) | `_shared/glossary.md` · `_shared/git-workflow.md` · `skills/CLAUDE.md` · root `CLAUDE.md` |
| a scope that prose alone can't enforce | the skill's `hooks:` guard (`scripts/guard-write-scope.sh` patterns) |
| when a skill is allowed to fire at all | the frontmatter `description` / `disable-model-invocation` |

Also check the authoring conventions while you are in the file — each is a legitimate ⚪/🟡 finding
when the session gave you evidence for it:

- **Body budget.** A `SKILL.md` grown past ~2,000 words is re-read in full on every run. If your
  proposal adds lines to a body already at budget, propose moving a block into `references/` in the
  same breath.
- **Description = discoverability.** Third person, WHAT + WHEN. If the session shows the skill firing
  wrongly or not firing, the description is the file to edit.
- **`disable-model-invocation`.** Side-effecting or outward-facing entry points carry it; doc-only
  and read-only skills deliberately don't. An auto-fire that shouldn't have happened is evidence.
- **Duplicated invariant sections.** `## Language` and `## Git workflow` are compact copies by design.
  When `_shared/` changes, the copies must change with it — a copy that drifted is a real finding,
  and fixing it means touching every drifted copy, not one.
