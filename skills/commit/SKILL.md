---
name: commit
description: "Commit the session's uncommitted changes: group files by logic, write English conventional-commit messages with the [T###] task id where one applies, commit on the current branch — never branch, push, merge, amend or add AI-attribution trailers. Invoked by run-task and cut-release; otherwise only on the user's explicit request — finishing a task or review is not one."
argument-hint: "[--dry-run] [--single] [--all] [--message <msg>]"
---

# Commit Changes Skill

Analyze uncommitted changes, group them by logic (not just path), and create well-structured commits.

## Language & git

Respond and reason in the user's language; vocabulary per **`../_shared/glossary.md`**. Never
translate code, identifiers, commands or paths. **Commit messages are ALWAYS English** — the user's
language shapes only the report, never the text written into git. **One branch — the current one**
(normally `main`): never branch, switch or open a worktree unless the user explicitly asked in this
session — **`../_shared/git-workflow.md`**.

Safety:
- Asked for a branch explicitly → use the name given (or propose and confirm one), create it from
  the current branch, say where the commits landed. Being asked to commit is not being asked to
  branch, and neither is a large or risky change — the answer to "this could break things" is a
  clean commit.
- Already on a non-default branch → stay there; never switch to `main`, never offer to merge or rebase.
- **Never push** unless explicitly asked. **Never merge, rebase or reset** — a commit is the only
  history-changing operation. **Never `--amend`** — always a new commit.
- **Never add attribution trailers** — no `Co-Authored-By:`, no "Generated with Claude" / "🤖
  Generated with..." footer, no AI credit. The message holds only `<type>: <description>` and an
  optional body.

## Backlog task reference

A change that advances a backlog task (`.dev-skills/build-plan/tasks/T###-*.md`) carries the id as a
`[T###]` tag in the subject — `<type>: <description> [T012]` — with what was done in the body if the
subject doesn't capture it. `run-task` checkpoint commits always pass the id. Otherwise take it from
the task whose files the change implements; a change that maps to no task (tooling, docs, a one-off
fix) gets no id — never invent one.

## Input

`$ARGUMENTS`: **--dry-run** preview without executing · **--single** force one commit · **--all**
commit all uncommitted changes, not just the session's · **--message <msg>** use this message (single
commit). E.g. `/commit`, `/commit --dry-run`, `/commit --single`,
`/commit --message "feat: Add user auth"`.

## Procedure

### Step 0: Filter to Session-Only Changes
By default commit **only files changed in this session**, never pre-existing uncommitted changes:
dirty files in the `gitStatus` snapshot taken at session start vs `git status --porcelain` now —
session-changed = current dirty MINUS dirty at start. None → report "No session changes to commit."
and stop. `/commit --all` (or an explicit request to commit everything) skips the filter.

### Step 1: Gather Change Information
```bash
git status --porcelain                                   # then filter per Step 0
git log --oneline -10 --format='%s'                      # style reference
git diff HEAD -- <session-changed-file1> <session-changed-file2> ...   # ONLY session files
```

### Step 2: Analyze Change Relationships
Separate **core changes** (new component/hook/type definitions, interface or signature changes, new
feature logic, bug fixes — commit separately) from **ripple changes** (import updates after a rename,
type-annotation and props updates across files — group together). Signal: one file changes a
definition AND many files have small changes referencing that symbol → split into core + ripple.

### Step 3: Grouping Strategy (Priority Order)
**A. Ripple patterns first** — e.g. `Button.tsx` changes its props interface + 20 files update the
usage → commit 1 "refactor: Add variant prop to Button component" (the definition + changed types),
commit 2 "refactor: Update Button usages for new variant prop" (the 20 files).

**B. Logical feature** — `types/*.ts` + `components/*.tsx` + `hooks/*.ts`; `app/api/*/route.ts` +
`components/*`; `hooks/use*.ts` + the components using it.

**C. Path-based fallback:**

| Path Pattern | Category |
|---|---|
| `components/**` | Components |
| `app/**` | Pages/Routes |
| `lib/**`, `utils/**` | Utilities |
| `hooks/**` | Hooks |
| `types/**` | Types |
| `styles/**` | Styles |
| `public/**` | Assets |

### Step 4: Decide Split Strategy
**Single commit** when ≤3 files, or all changes clearly one feature, or `--single` / `--message`
given. **Multi-commit** when a ripple pattern is detected, unrelated features are mixed, or a
refactoring spans many modules.

### Step 5: Generate Commit Messages
Always English, no attribution trailers (see above):
```
<type>: <Short description (imperative, <70 chars)> [<task-id> if backlog-related]

<Optional body explaining why / what was done>
```
Types: `feat:` new functionality · `fix:` bug fix · `refactor:` restructuring · `chore:` maintenance,
tooling · `docs:` documentation · `test:` tests · `style:` styling (CSS, formatting).

### Step 6: Execute Commits
Per group: stage specific files (**never** `git add .` / `git add -A`), commit with a HEREDOC, verify
with `git log -1 --oneline`:
```bash
git add path/to/file1.tsx path/to/file2.ts
git commit -m "$(cat <<'EOF'
feat: Add authentication service

Implement OAuth2 flow with refresh token support.
EOF
)"
```

## Output Format

User-facing text in the user's language; the embedded commit messages stay English.

- **Dry run** — `## Commit Plan (Dry Run)`: files changed · proposed commits; per commit its type,
  file list (long lists truncated: "... (21 more files)") and the message quoted; close with
  "Run `/commit` to execute."
- **Execution** — `## Commits Created`: per commit the `git add` / `git commit` lines and git's own
  `[main abc1234] …` / "N files changed" output; then **Summary**: "Created N commits" + one
  `hash subject` line each, newest first.

## Error Handling

| Scenario | Action |
|---|---|
| No changes | "No uncommitted changes found." and exit |
| Pre-commit hook fails | Show the hook output, identify the fix, ask "Pre-commit hook failed. Fix and retry?"; on yes fix and create a NEW commit (never amend) |
| Merge conflicts | Report the conflicted files, ask the user to resolve |

Edge cases: only untracked files → stage as new additions · single file → one commit, no splitting ·
50+ files → summarize first, ask to proceed · mixed staged/unstaged → analyze all together ·
`node_modules` / `.next` changes → skip, warn if staged.
