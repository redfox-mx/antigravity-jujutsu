# Jujutsu (`jj`) Command Cheatsheet & Git Mapping

Quick translation table between standard Git commands and their Jujutsu equivalents, optimized for AI agent execution.

> [!TIP]
> **Built-in Documentation via `--help`**:
> Almost all `jj` commands and subcommands support `--help` (or `-h` for quick summary). For instance:
> `jj --help`, `jj workspace --help`, `jj rebase --help`, `jj bookmark --help`, `jj git --help`.
> When in doubt about flags, syntax, or arguments across `jj` versions, run `jj <subcommand> --help` to inspect built-in documentation directly from the CLI.
>
> For the complete, exhaustive translation table covering all edge cases, see the [Full Git vs Jujutsu Comparison Table](./git-command-table.md).

---

## 1. Daily Version Control Translation Table

| Intent | Git Command | Safe `jj` Equivalent | Notes |
| :--- | :--- | :--- | :--- |
| **Status** | `git status` | `jj --no-pager status` | Working copy is `@` |
| **Log (Graph)** | `git log --graph --oneline` | `jj --no-pager log --limit 10` | Shows Change IDs and Commit IDs |
| **Inspect Commit** | `git show <commit>` | `jj --no-pager show <change_id>` | Shows description and diff |
| **Diff Working Copy** | `git diff` | `jj --no-pager diff` | Diffs `@` against `@-` |
| **Diff Unified (Git-style)** | `git diff` | `jj --no-pager diff --git` | Standard unified diff format |
| **Diff Specific File** | `git diff <file>` | `jj --no-pager diff <file>` | Scoped to path |
| **Diff Between Commits** | `git diff A B` | `jj --no-pager diff --from A --to B` | Supports any two revsets |
| **Stage & Commit** | `git add -p && git commit -m "..."` | `jj describe -m "..."` then `jj new` | No staging area exists |
| **Amend Working Commit** | `git commit --amend -m "..."` | `jj describe -m "..."` | Files auto-amend into `@` |
| **Start New Branch/Change**| `git checkout -b <name>` | `jj new trunk() -m "..."` | Bookmarks created only at handoff |
| **Switch Working Target** | `git switch <branch>` | `jj edit <change_id>` | Moves `@` to target commit |
| **Stash Changes** | `git stash` | `jj new` | Not needed; work is already committed |
| **Fetch from Remote** | `git fetch` | `jj git fetch` | Imports remote bookmarks |
| **Pull & Rebase** | `git pull --rebase` | `jj git fetch && jj rebase -d trunk()` | Two clean, explicit steps |
| **Push Branch** | `git push -u origin <branch>` | `jj git push --bookmark <branch>` | Pushes bookmark to remote |
| **Auto-Named Push** | N/A | `jj git push -c @-` | Pushes as `push-<change_id>` |
| **Undo Last Command** | `git reset --hard HEAD@{1}` | `jj undo` | Safe, reliable operation log rollback |
| **Redo Undone Command** | N/A | `jj redo` | Restores last undone operation |
| **Discard Changes** | `git reset --hard` | `jj restore` | Restores files from `@-` |
| **Delete/Abandon Commit** | `git reset --hard <parent>` | `jj abandon <change_id>` | Hides commit from graph |
| **Rebase Branch** | `git rebase <target>` | `jj rebase -d <target>` | Rebases descendants automatically |
| **Distribute Fixes** | N/A | `jj absorb` | Splits changes into matching ancestors |

---

## 2. Advanced Stack Manipulation

### Move Backwards & Forwards in Stack:
```bash
jj prev -e    # Edit immediate parent commit (@-)
jj next -e    # Edit child commit on current branch
```

### Squash Changes Up the Stack:
```bash
# Squash working copy into immediate parent
jj squash

# Squash specific file into immediate parent
jj squash --into @- src/auth.py

# Squash changes from one commit into another arbitrary commit
jj squash --from <source_id> --into <target_id>
```

### Rebase Specific Branch or Revision:
```bash
# Rebase an entire stack onto main
jj rebase -s <stack_root_id> -o trunk()

# Rebase current commit onto a specific feature
jj rebase -d <feature_change_id>
```

---

## 3. Bookmark Operations

```bash
# Create bookmark on the completed commit
jj bookmark create feat/login-form -r @-

# Move existing bookmark forward
jj bookmark move feat/login-form --to @-

# Move bookmark backwards or sideways
jj bookmark move feat/login-form --to @- --allow-backwards

# Delete local bookmark
jj bookmark delete feat/login-form

# List all bookmarks
jj bookmark list --tracked
```
