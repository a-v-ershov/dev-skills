# Git workflow — one branch, the current one

Shared by every skill and agent in this set. This is an **invariant, not a default**: no skill here
creates, switches, or merges branches on its own initiative. Each skill carries a compact copy of the
rule in its `## Git workflow` section and points back here for the full text.

## The rule

**Work on the current branch — normally `main`.** Whatever branch the session starts on is the branch
every skill reads, writes, and commits to, from the first spec doc to the checkpoint commits of the
build loop to the release cut.

Never, on your own initiative:

- `git checkout -b` / `git switch -c` — no `feature/*`, no `release/*`, no `fix/*`, not "just to be
  safe", not "so the work is isolated", not one branch per task;
- `git checkout <other>` / `git switch <other>` — don't move the session onto another branch;
- `git worktree add` — the build pipeline is deliberately **single working tree** (`run-task`,
  `build-tasks`), and the release phase's parallel agents are read-only;
- `git merge`, `git rebase`, `git reset --hard`, `git push --force` — nothing that rewrites or moves
  shared history;
- `git push` — only when the user asks (see the `commit` skill).

Branching is the user's decision about how their repository is organized. It is never a side effect
of running a skill.

## The one exception

**The user explicitly asked for a separate branch, in this session.** "Do this on a branch",
«сделай в отдельной ветке», or a branch name handed to you directly — that is the yes. Then:

1. Use the name the user gave. If they didn't give one, propose a name and get it confirmed.
2. Create it from the current branch, and say plainly which branch the work is now on.
3. Stay on it for the rest of the run. One yes licenses **one** branch, not a branching habit.

A request to *commit*, to *ship a release*, to *fix a bug*, or to *open a PR* is **not** a request to
branch. Neither is a large or risky change: the answer to "this could break things" is a checkpoint
commit and a clean tree, not a branch nobody asked for.

## Already on a non-default branch

If the session starts on something other than `main`, that is the user's choice — **stay there**.
Don't switch to `main`, don't branch off it, don't offer to merge or rebase. The rule is "the current
branch", and the current branch is whatever it already is.

## When a step genuinely cannot proceed without a branch

One real case exists: a **pull request cannot be opened from the base branch** (`cut-release`,
Stage 4). If a step truly needs a branch to complete, **stop and ask** — name why, propose the branch
name, and act only on an explicit yes. Otherwise commit and tag on the current branch and hand the PR
back to the user as a remaining step (`--no-pr` behaviour). Never resolve the situation by branching
silently.

## Subagents

A skill that spawns agents passes this rule down together with the language rule — the implementer,
the verifier, and the prototyper inherit the same invariant, and the read-only release agents don't
touch git at all. An agent that believes the work needs a branch **says so and lets the orchestrator
ask the user**; it never creates one itself.
