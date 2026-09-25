# Audit rubric — seven lenses, the severity scale, and the report template

Used by `audit-skills` in Stages 2–5. Read it before writing findings. The four extra lenses for a
pipelined skill set (invariants, artifacts, orchestration, placement) are in
`dev-skills-lenses.md` — read that one too whenever a target belongs to this set.

---

## What the evidence can and cannot prove

| Digest section | Proves | Does **not** prove |
|---|---|---|
| Skills loaded | which file to open and edit | that the skill was the right one to run |
| Skill invocations | what was invoked, with what args, and what the harness said back | whether the run was any good |
| What each skill run did | wall time, tool mix, errors, how many user turns it took | that the time was wasted — some work is just long |
| Subagents · cost by agent type | duration, tokens, tool count, model per agent and per role | whether a cheaper agent would have sufficed |
| Tool usage / slowest calls | where the wall clock went | that a faster path existed |
| Repetition signals | that identical work was done twice | that the second time was pointless (state may have changed) |
| Files written | what the session actually changed, and where | that the write was outside the skill's scope — check the scope first |
| Invariant tripwires | that a branch was created, a push happened, a commit message wasn't English | that the skill decided it — the user may have asked |
| Errors and denials | that a call failed or was refused | why — read the surrounding conversation |
| User turns | where the user corrected, interrupted, repeated themselves | what they meant — that's in the conversation |

The right-hand column is where bad findings come from. Every claim needs both a fact from the digest
**and** the reading of intent from the conversation.

---

## The seven lenses

Go through all seven for each target. Most sessions yield findings in two or three of them.

### 1. Correctness — it did the wrong thing

The skill produced a result its own file says it shouldn't have, or one that didn't match what was
asked.

**Signals:** a user turn correcting the output; a deliverable contradicting the template in the skill
file; a rule in the file ("always X") with no X in the transcript; a commit, write or call the skill
was told never to make.

**Proves it:** the rule quoted from the file + the transcript evidence that it wasn't honoured.

> *e.g.* `commit/SKILL.md` says "NEVER use `git add .`"; the digest's tripwire table shows
> `git add -A` at 14:22. The rule exists but sits under Step 6, 200 lines below where staging is
> decided → move it into Step 0 as a precondition.

### 2. Procedure drift — it skipped or reordered its own steps

The skill ran, but not the way its file describes: a gate passed silently, a step merged into
another, a mandatory read never happened.

**Signals:** a step that must produce a tool call (a `Read`, a `git log`, a question) with no such
call in the run window; a "show the result and wait" gate followed immediately by more tool calls;
the run finishing far faster than its own procedure allows; a stage in the copyable checklist that
was never checked off.

**Proves it:** the step quoted + the absence of its footprint in the window (name the timestamps the
window covers).

*A skipped step is usually a formatting problem, not a discipline problem.* Steps buried in prose,
steps stated once in an overview and never repeated in the procedure, and steps whose output isn't
checked anywhere are the ones that get skipped. Propose the structural fix — most often moving the
step into the skill's copyable checklist — not "be more careful".

### 3. Triggering — it fired when it shouldn't, or didn't when it should

**Signals:**
- `ERROR: … cannot be used with Skill tool due to disable-model-invocation` — the model tried to call
  a manual-only skill. Either the calling skill's own file tells it to (a broken hand-off), or the
  description invites it. Both are real defects in a file.
- The skill auto-fired on a message it had no business firing on → the `description` is too broad.
- The user had to type `/x` for something `x`'s description claims it fires on → too narrow, or
  worded as *what it is* instead of *when to use it*.
- Two skills in the session cover the same trigger → their descriptions overlap.

**Proves it:** the error line or the user turn, plus the `description:` as it currently reads.

### 4. Redundancy — it did the same work twice

**Signals:** the repetition table (same command, same `file_path`); files read 3+ times; a subagent
re-deriving context the caller already had in its prompt; re-reading a whole `references/` file when
a section was enough; the skill re-running a check its previous step already ran; an orchestrator
restating a sub-skill's procedure instead of invoking it.

**Proves it:** the repeat count and the call itself.

Before proposing: check whether state changed between the calls. `git status` before and after a
commit is not redundancy; `git status` twice in a row is. Reading a file, editing it, and reading it
back is usually redundancy — the edit tool already reports success.

> *e.g.* `make check` run 5× in one run window, all green, no edits in between → the skill's "verify
> after every step" rule is over-applied; scope it to steps that changed files.

### 5. Speed — it was slower than the work required

**Signals:**
- One call dominating the wall clock in the slowest-calls table.
- Subagents run one after another whose prompts don't reference each other → they could have been
  spawned in a single message and run concurrently. (Careful: in the build pipeline sequential is
  the deliberate invariant — only the read-only release audits fan out.)
- A polling loop (`until …; do sleep …; done`) where the harness would have notified anyway.
- A long foreground command that could have run in the background while other work continued.
- A heavyweight agent/model on a mechanical stage (a rename, a file move, a lookup).
- A full-repo `grep`/`find` where the skill already knew the path.
- A subagent spawned for something the caller could do in two tool calls — the agent costs a full
  context load before it does any work.
- A per-run cost multiplied by the role's run count in the cost-by-agent-type table.

**Proves it:** the duration from the digest **plus** the faster path spelled out. "This took 40
minutes" is not a finding; "this took 40 minutes and steps 2–4 have no data dependency, so one
message spawning three agents makes it ~15" is.

Never propose speed at the cost of a correctness gate the skill deliberately has. If the tradeoff is
real, say so in the proposal and let the user decide.

### 6. User friction — it cost the user turns it didn't need to

**Signals:** interrupts; rejected tool calls ("The user doesn't want to proceed"); the user repeating
an instruction they already gave; a question the skill could have answered by reading a file or the
spec; the user asking "what did you do?" after the skill reported; more than 3 clarifying questions
in one run; a gate that asked for approval of something the config had already settled.

**Proves it:** the user turn, quoted, with its timestamp.

An interrupt is the strongest signal in the whole digest — the user watched it going wrong and
stopped it. Always chase one down to what the file let it do.

### 7. Simplicity — its output was harder to use than the work it delivered

The simplification KPI applied to the tooling itself: **the skill's result should be easier to
understand, and the skill easier to use, than the run before it.** The skill did its job, but the
human had to work to consume it — or the skill carries machinery no run has ever needed.

**Signals:** the user asking "so what do I do?" / "what did you actually change?" after a report
that formally has its «What you should do» block; a report longer than the work it describes, or
that opens with method instead of the outcome; a procedure stage whose output nothing downstream
reads; an argument or config option no session has ever passed; two sections of the artifact
carrying the same content in different words.

**Proves it:** the user turn or the artifact section quoted, **plus the shorter form** that would
have carried the same decision — a simplicity finding you cannot state as "replace this with this
smaller thing" is taste, not a finding.

Proposals from this lens **remove or merge; they do not add**. A simplicity fix that grows the file
has failed its own test — prefer deleting the unused option, collapsing the duplicate section,
tightening the report template.

---

## Severity

Same three levels the release pipeline uses (`../../_shared/release-pipeline/severity-rubric.md`),
read against the skill's own contract — its `SKILL.md`, the `_shared/` method it inherits, and the
invariants of the set — never against an ideal skill you have in mind.

| Level | Meaning for a skill |
|---|---|
| 🔴 **Blocker** | It produced a wrong result, lost work, or broke a rule it states about itself or an invariant of the set (branched on its own, wrote outside its scope, answered in the wrong language). Would happen again on the next run. |
| 🟡 **Major** | It cost real time, tokens or user turns, or made the output materially worse — but the result was recoverable. A missing template section, a repeated expensive read, a gate that asked for nothing. |
| ⚪ **Minor** | Wording, ordering, or a rough edge. Fixing it is cheap; not fixing it costs little. |

Rank by severity, then by cheapness of fix. Cap the report at 8 proposals and state how many you
dropped. The `severity-rubric.md` guard applies here in full: **no finding without proof**, flag
against the contract rather than against an ideal, and remember that a wall of 🟡/⚪ noise buries the
one 🔴 that mattered.

---

## Report template

The report is the final text message of the turn. Numbering runs in one sequence across all targets.
Write the labels in the user's language (Russian: **Факт** / **Причина** / **Правка** / **Эффект**;
sections «Не предлагаю» and «Без правки файла»); keep file paths, section headings and quoted
wording verbatim.

```markdown
# Session audit — <n> proposals across <m> targets

<one or two lines: what ran this session and the overall verdict>

## <skill or agent name> — <k> proposals
*<what it was asked to do, and how it went — one line>*

**1. 🔴 <the defect in one line>**
- **Fact:** <timestamp, quote, count or duration from the digest>
- **Cause:** `<file>` → `## <section>`: "<the wording that allowed it>"
- **Fix:** <the concrete edit — what the wording becomes>
- **Effect:** <what changes on the next run> · <cost, if this adds lines>

**2. 🟡 …**

## <next target> — <k> proposals
…

## Not proposed
- <considered and rejected, one line each with the reason>

## No file change — note only
- <a real constraint of the harness or the model, with the workaround>

---
Reply with the numbers to apply (`1, 4`), `all`, or say what to change.
```

### Worked example of one proposal

```markdown
**2. 🟡 Верификатор перечитывает весь спек на каждой задаче**
- **Факт:** `dev-skills:verifier` ×4 запуска, 28–48 мин каждый, 210–275k токенов;
  `Read` одного и того же `project-spec/summary.md` в каждом (повторы: ×4).
- **Причина:** `_shared/build-pipeline/verification-method.md` → `## Stage 0: Intake`:
  «Прочитай спецификацию целиком».
- **Правка:** заменить на «Прочитай только разделы из `traces_to` задачи; целиком — только если
  `traces_to` пуст».
- **Эффект:** −1 полное чтение спецификации на задачу (~15–20k токенов, ~2 мин), критерии приёмки
  не затрагиваются. Правка заменяет строку, не добавляет; правило общее — правим в `_shared/`,
  а не в `verify-feature/SKILL.md`.
```

---

## Anti-patterns — findings that look right and aren't

| Anti-pattern | Why it's wrong |
|---|---|
| "Add a rule about X" after one incident | One misstep can be noise. Say it's a single occurrence, or show it repeating. |
| A proposal that only adds lines | Every line is re-read on every future run. Prefer replacing or tightening; if it must be an addition, say what it costs — or move detail into `references/`. |
| "Be more careful / more thorough / more explicit" | Not an edit. If you can't quote the before and after, it isn't a proposal. |
| Patching the copy instead of the source | The rule lives in `_shared/`; editing one skill's copy makes the pipeline disagree with itself. |
| Rewriting the skill's purpose | Out of scope. Audit how it did its job, not whether it should have that job. |
| Findings about a skill that didn't run | You have no evidence. Leave it alone. |
| Treating a tripwire as a verdict | The user may have asked for the branch, the push, the rebase. Check the conversation. |
| Attributing a harness failure to the skill | An API error, a permission denial or a tool timeout isn't the skill's wording. Put it under **no file change — note only**. |
| Grading the user's prompts | The audit is about the skills, not the person driving them. |
| Proposing a fix the file already contains | Read the file first, every time — the rule is often there and merely buried. |
