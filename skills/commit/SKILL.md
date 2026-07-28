---
name: commit
disable-model-invocation: true
description: "Commit session changes with intelligent splitting for large changesets"
argument-hint: "[--dry-run] [--single] [--all] [--message <msg>]"
---

# Commit Changes Skill

Analyze uncommitted changes, group them intelligently by logic (not just paths), and create well-structured commits.

## Language

Respond and reason in whatever language the user addressed you in — write user-facing text (the
commit plan, the execution summary, questions, error messages) in that language and think in it
too.

**Critical exception — commit messages are ALWAYS in English**, regardless of the user's
language. The user's language affects only the report shown to the user, never the text written
into git. Likewise, never translate code, identifiers, file paths, or commands.

**Terms.** How the workflow vocabulary is rendered is governed by `../_shared/glossary.md`: translate it
(`findings` → замечания, `gate` → контрольная точка, `rework` → доработка, `spec` → спецификация),
keep `fork`, `commit`, `backlog`, `mockup`, `deploy`, `checklist`, `baseline`, `harness`,
`onboarding`, `sanity check` in Latin script and uninflected, never build hybrid verbs
(«закоммитить», «отскаффолдить»), and leave template section headings and task fields
(`## Forks / Decisions log`, `type: rework`) verbatim.

## Git safety

- **Never create a branch.** Commit onto the current branch. Only branch if the user has
  explicitly asked in this session.
- **Never push** unless the user explicitly asks.
- **Never use `--amend`** — always create a new commit.
- **Never add co-author or attribution trailers.** Do not append `Co-Authored-By:` lines,
  "Generated with Claude" / "🤖 Generated with..." footers, or any text crediting an AI model
  or tool. Commit messages contain only the change description.

## Backlog task reference

If the change relates to a build-backlog task (one of `.dev-skills/build-plan/tasks/T###-*.md`), include the
task id and what was done in the commit message — the id as a `[T###]` tag in the subject line. This
makes each commit traceable to the task it advances. `run-task` checkpoint commits always pass
the id of the task they finalize.

- **Relates to a task:** `<type>: <description> [T012]`. Put what was done in the body if the subject
  doesn't capture it.
- **Not backlog-related** (tooling, docs, a one-off fix that maps to no task): omit the id — never
  invent one.
- Determine the id from the `run-task` invocation that triggered the commit, or from the task
  whose files the change implements; if a change clearly maps to no task, treat it as not-backlog-related.

## Input

Arguments provided via `$ARGUMENTS`:
- **--dry-run**: Preview commits without executing
- **--single**: Force all changes into a single commit
- **--all**: Commit all uncommitted changes, not just session changes
- **--message <msg>**: Use specific commit message (for single commit)

Examples:
- `/commit` - Auto-analyze and commit (split if needed)
- `/commit --dry-run` - Preview what would be committed
- `/commit --single` - Force single commit
- `/commit --message "feat: Add user auth"` - Use specific message

## Procedure

### Step 0: Filter to Session-Only Changes

By default, ONLY commit files that were changed during this session. Do NOT commit pre-existing uncommitted changes.

**How to determine session changes:**
1. The conversation context includes a `gitStatus` snapshot taken at session start. Parse the list of dirty files from it.
2. Run `git status --porcelain` now to get the current dirty files.
3. **Session-changed files** = current dirty files MINUS files that were already dirty at session start.
4. If no session-changed files exist, report "No session changes to commit." and stop.

**Override:** If the user explicitly asks to commit all changes (e.g., `/commit --all`), skip this filter and commit everything.

### Step 1: Gather Change Information

```bash
# Get all changed files (then filter to session-only as per Step 0)
git status --porcelain

# Get recent commits for style reference
git log --oneline -10 --format='%s'

# Get diff ONLY for session-changed files (pass file paths explicitly)
git diff HEAD -- <session-changed-file1> <session-changed-file2> ...
```

### Step 2: Analyze Change Relationships

**Key insight**: Distinguish between core changes and ripple effects.

**Core changes** (commit separately):
- New component/hook/type definitions
- Interface/type signature changes
- New feature logic
- Bug fixes

**Ripple changes** (group together):
- Import statement updates after component rename
- Type annotation updates across files
- Props updates after interface change

**Detection patterns**:
- If one file modifies a component/hook/type definition AND many files have small changes referencing that symbol -> split into core + ripple
- Look for: same identifier appearing across many file diffs, import changes, type updates

### Step 3: Grouping Strategy (Priority Order)

**A. Detect ripple patterns first:**
```
Example: Button.tsx changes Button props interface
         + 20 files updating Button usage

Commit 1: "refactor: Add variant prop to Button component"
  - components/ui/Button.tsx (the definition)
  - types/components.ts (if types changed)

Commit 2: "refactor: Update Button usages for new variant prop"
  - All 20 files with usage updates
```

**B. Group by logical feature:**
- Related module files: `types/*.ts` + `components/*.tsx` + `hooks/*.ts`
- API + component: `app/api/*/route.ts` + `components/*`
- Hook + usage: `hooks/use*.ts` + components using it

**C. Path-based fallback:**
| Path Pattern | Category |
|--------------|----------|
| `components/**` | Components |
| `app/**` | Pages/Routes |
| `lib/**` | Utilities |
| `hooks/**` | Hooks |
| `types/**` | Types |
| `utils/**` | Utilities |
| `styles/**` | Styles |
| `public/**` | Assets |

### Step 4: Decide Split Strategy

**Single commit** when:
- <=3 files changed, OR
- All changes clearly related (same feature), OR
- `--single` flag provided, OR
- `--message` flag provided

**Multi-commit** when:
- Ripple pattern detected (definition + many usages)
- Multiple unrelated features mixed
- Large refactoring spanning many modules

### Step 5: Generate Commit Messages

Commit messages are **always written in English** (see Language).

Do NOT include any co-author or attribution trailers (no `Co-Authored-By:`, no "Generated with
Claude" footer, no AI/model credit). The message holds only `<type>: <description>` and an
optional body.

**Format:**
```
<type>: <Short description (imperative, <70 chars)> [<task-id> if backlog-related]

<Optional body explaining why / what was done>

```

**Types:**
- `feat:` - New functionality
- `fix:` - Bug fixes
- `refactor:` - Code restructuring
- `chore:` - Maintenance, tooling
- `docs:` - Documentation
- `test:` - Test changes
- `style:` - Styling changes (CSS, formatting)

### Step 6: Execute Commits

For each commit group:

1. Stage specific files (NEVER use `git add .` or `git add -A`):
```bash
git add path/to/file1.tsx path/to/file2.ts
```

2. Create commit with HEREDOC:
```bash
git commit -m "$(cat <<'EOF'
feat: Add authentication service

Implement OAuth2 flow with refresh token support.

EOF
)"
```

3. Verify success:
```bash
git log -1 --oneline
```

## Output Format

All user-facing text below is rendered in the user's language. The commit messages embedded in it
stay in English.

### Dry Run

```markdown
## Commit Plan (Dry Run)

**Files changed**: 25
**Proposed commits**: 2

### Commit 1: Core Change
**Type**: refactor
**Files** (2):
- components/ui/Button.tsx
- types/components.ts

**Message**:
> refactor: Add size prop to Button component

---

### Commit 2: Usage Updates
**Type**: refactor
**Files** (23):
- components/header/NavButton.tsx
- components/forms/SubmitButton.tsx
- ... (21 more files)

**Message**:
> refactor: Update Button usages with size prop

---

Run `/commit` to execute.
```

### Execution

```markdown
## Commits Created

### Commit 1/2
$ git add components/ui/Button.tsx types/components.ts
$ git commit -m "refactor: Add size prop..."
[main abc1234] refactor: Add size prop to Button component
 2 files changed, 25 insertions(+), 8 deletions(-)

### Commit 2/2
$ git add components/header/NavButton.tsx ...
$ git commit -m "refactor: Update Button usages..."
[main def5678] refactor: Update Button usages with size prop
 23 files changed, 46 insertions(+), 46 deletions(-)

---

**Summary**: Created 2 commits
def5678 refactor: Update Button usages with size prop
abc1234 refactor: Add size prop to Button component
```

## Error Handling

| Scenario | Action |
|----------|--------|
| No changes | Report "No changes to commit" and exit |
| Pre-commit hook fails | Show error, offer to fix, create NEW commit (never amend) |
| Merge conflicts | Report files with conflicts, ask user to resolve |

### Hook Failure Recovery

If commit fails due to pre-commit hooks:
1. Show the hook output
2. Identify what needs fixing
3. Ask: "Pre-commit hook failed. Fix and retry?"
4. If yes, fix issues and create NEW commit (never use --amend)

## Edge Cases

- **No changes**: "No uncommitted changes found."
- **Only untracked files**: Treat as new additions, stage normally
- **Single file**: Skip splitting, create one commit
- **Very large changeset (50+ files)**: Summarize first, ask to proceed
- **Mixed staged/unstaged**: Analyze ALL changes together
- **node_modules or .next changes**: Skip these directories, warn if staged

## Full Example Session

### Example 1: Ripple Pattern Detection

```
User: /commit

Claude: Analyzing uncommitted changes...

$ git status --porcelain
M  components/ui/Card.tsx
M  types/ui.ts
M  components/dashboard/StatsCard.tsx
M  components/dashboard/UserCard.tsx
M  components/products/ProductCard.tsx
M  app/page.tsx
... (15 more files)

Analyzing diffs...

Detected ripple pattern:
- Card.tsx: Changed Card component props (added `elevated` prop)
- types/ui.ts: Added CardProps type update
- 15 other files: Updating Card usage

Splitting into 2 commits:

### Commit 1/2: Core Change
$ git add components/ui/Card.tsx types/ui.ts
$ git commit -m "$(cat <<'EOF'
feat: Add elevated prop to Card component

Add visual elevation option with shadow effects.

EOF
)"
[main a1b2c3d] feat: Add elevated prop to Card component
 2 files changed, 18 insertions(+), 4 deletions(-)

### Commit 2/2: Usage Updates
$ git add components/dashboard/StatsCard.tsx components/dashboard/UserCard.tsx ...
$ git commit -m "$(cat <<'EOF'
refactor: Update Card usages with elevated prop

EOF
)"
[main d4e5f6g] refactor: Update Card usages with elevated prop
 15 files changed, 30 insertions(+), 15 deletions(-)

---

**Summary**: Created 2 commits
d4e5f6g refactor: Update Card usages with elevated prop
a1b2c3d feat: Add elevated prop to Card component
```

### Example 2: Single Commit (Small Change)

```
User: /commit

Claude: Analyzing uncommitted changes...

$ git status --porcelain
M  components/forms/LoginForm.tsx

Found 1 changed file. Creating single commit...

$ git add components/forms/LoginForm.tsx
$ git commit -m "$(cat <<'EOF'
fix: Handle empty email validation gracefully

Add check for empty string before email format validation.

EOF
)"
[main x1y2z3a] fix: Handle empty email validation gracefully
 1 file changed, 5 insertions(+), 2 deletions(-)

---

**Summary**: Created 1 commit
x1y2z3a fix: Handle empty email validation gracefully
```
