---
name: jj
description: >-
  Use when the user or agent needs to operate in a Jujutsu (jj) version control
  repository — running jj commands, creating atomic changes, describing commits,
  inspecting diffs/status/logs, managing bookmarks, rebasing, resolving first-class
  conflicts, recovering with operation logs (jj undo / jj op restore), or pushing
  to Git remotes. Enforces agent-safe non-interactive operations (no pagers, no editor hangs)
  and prevents destructive Git habits.
---

# Jujutsu (`jj`) VCS Skill

Use `jj` for all version control operations in any repository with a `.jj/` directory. Direct `git` commands (both mutating and read-only) are blocked by the plugin's safeguard hook; use `jj` commands exclusively (`jj --no-pager status`, `jj --no-pager log`, `jj --no-pager diff`, `jj git fetch`, `jj git push`, `jj workspace root`).

---

## 1. Core Mental Model for Agents

1. **Working Copy is a Commit (`@`)**: Unlike Git where working files sit unstaged outside the DAG, in `jj` your working tree is an active commit (`@`). File edits are automatically snapshotted on the next `jj` command. There is no staging index and **never** a need for `git add`.
2. **Stable Change IDs vs. Commit IDs**:
   - **Commit ID**: Ephemeral hash that changes whenever a commit is amended, rebased, or squashed.
   - **Change ID**: Stable identifier (e.g. `kntqzsqt`) that remains constant across rewrites. **Always use Change IDs** in command arguments and scripts.
3. **Bookmarks Do Not Auto-Advance**: In `jj`, `@` is just a commit. Creating new commits or editing files does NOT automatically move bookmarks forward. Bookmarks are updated explicitly (`jj bookmark move <name> --to @-`).
4. **First-Class Conflicts**: Rebases and merges never abort or freeze into interactive states. Conflicts are safely recorded inside commits and resolved asynchronously.
5. **Operation Log Safety Net**: Every mutation is logged. Any command can be undone with `jj undo` or restored with `jj op restore <id>`.

---

## 2. Non-Negotiable Agent Safety Rules

- **Always pass `--no-pager`**: Output commands page through `less` by default and will hang non-interactive sessions. Use `jj --no-pager <cmd>` (or set `--config ui.paginate=never` for the command). Do *not* write `ui.paginate=never` to the user's global config.
- **Always pass explicit `-m "<msg>"`**: Never run bare `jj describe`, `jj commit`, `jj squash`, `jj split`, or `jj resolve` without arguments—they launch interactive editors/TUIs (Notepad, nano, vim) and hang the session.
- **Never run direct Git commands**: All direct `git` commands (both mutating and read-only) are blocked by the plugin's `PreToolUse` safeguard hook in `.jj/` repositories. Use `jj` commands exclusively (`jj --no-pager status`, `jj --no-pager log`, `jj --no-pager diff`, `jj git fetch`, `jj git push`, `jj workspace root`).
- **Verify worktree shadowing**: If running inside an external Git worktree or subfolder without its own `.jj/`, verify that `jj workspace root` matches the current working directory. If mismatched, do not run `jj` commands to prevent unintentionally modifying the parent repository.

*See [references/agent-safety.md](./references/agent-safety.md) for full safety guidelines.*

> [!TIP]
> **Built-in Documentation via `--help`**:
> Almost all `jj` commands and subcommands support `--help` (or `-h` for a summary). When in doubt about flags, syntax, or behavior across versions, run `jj <subcommand> --help` (e.g. `jj rebase --help`, `jj bookmark --help`, `jj git --help`).
> For an exhaustive, side-by-side translation of every Git command to its `jj` counterpart, see the [Complete Git vs. Jujutsu Command Reference Table](./references/git-command-table.md).

---

## 3. The Core Development Loop

Follow this standard rhythm for every task:

```bash
# 1. Inspect repository state
jj --no-pager status
jj --no-pager log --limit 10

# 2. Start a fresh change off the default branch or current work
jj new trunk() -m "feat(module): describe task unit"

# 3. Edit files (tools edit files normally)

# 4. Review changes (snapshotted automatically on command execution)
jj --no-pager diff --stat
jj --no-pager diff

# 5. Advance to next unit (prevents single "fat commit" absorption)
jj new -m "feat(module): next logical task"
```

> [!IMPORTANT]
> **Avoid Commit Absorption**: If you make multiple edits without running `jj new`, all modifications collapse into a single commit in `@`. Establish a strict rhythm: `jj describe -m "..."` then `jj new -m "..."`.

---

## 4. History Surgery (Non-Interactive)

- **Amend Current Change**: Simply edit files on disk; the next `jj` command automatically amends `@`. To update the description: `jj describe -m "new message"`.
- **Squash into Parent (`@-`)**:
  ```bash
  jj squash -m "feat: consolidated description"
  ```
- **Move Specific Files into Parent (File-Level Split)**:
  ```bash
  jj squash --into @- src/utils.py
  ```
- **Non-Interactive Hunk Splitting (Construction Method)**:
  ```bash
  # 1. Capture original change ID
  $ORIG = (jj log -r @ --no-graph -T 'change_id')
  # 2. Create sibling off parent
  jj new @- -m "fix(core): first part"
  # 3. Write partial file content, then advance
  jj new -m "feat(core): second part"
  # 4. Restore remainder from original change
  jj restore --from $ORIG src/core.py
  # 5. Abandon the original fat commit
  jj abandon $ORIG
  ```
- **Auto-Distribute Hunks Up the Stack (`jj absorb`)**:
  ```bash
  jj absorb
  ```
  Automatically distributes modified hunks in `@` into the appropriate ancestor commits that originally introduced those lines.

*See [references/command-cheatsheet.md](./references/command-cheatsheet.md) for Git-to-jj command mappings.*

---

## 5. Bookmarks & Git Remote Collaboration

```bash
# 1. Fetch latest changes from remote
jj git fetch

# 2. Rebase stack onto updated remote trunk
jj rebase -d trunk()

# 3. Create bookmark on the completed commit (@-)
jj bookmark create feat/my-feature -r @-

# 4. Push to remote (new bookmarks push directly in jj 0.42+)
jj git push --bookmark feat/my-feature

# Alternatively: auto-generated push bookmark
jj git push -c @-    # pushes as "push-<change_id>"

# 5. Update existing bookmark after further edits
jj bookmark move feat/my-feature --to @-
jj git push --bookmark feat/my-feature
```

> [!NOTE]
> Every commit in the pushed range MUST have a description (`jj describe -m "..."`). Jujutsu rejects pushes if any ancestor commit has an empty description.

*See [references/git-interop.md](./references/git-interop.md) for details on remotes, PR stacks, and avoiding squash-merge zombies.*

---

## 6. Resolving First-Class Conflicts

When a rebase or merge introduces conflicts, Jujutsu never halts. Conflicted commits display `(conflict)` in `jj status`:

1. **List Conflicted Files**:
   ```bash
   jj --no-pager resolve --list
   ```
2. **Inspect Conflict Markers**:
   Markers show the diff from base to side A to be applied to side B:
   ```text
   <<<<<<< conflict 1 of 1
   %%%%%%% diff from: <base>
   \\\\\\\        to: <side A>
   -line in base
   +line in A
   +++++++ <side B>
   line in B
   >>>>>>> conflict 1 of 1 ends
   ```
3. **Resolve Non-Interactively**:
   Edit the file directly using file-editing tools, remove all `<<<<<<<`, `%%%%%%%`, `+++++++`, `>>>>>>>` markers, and save clean intended code.
4. **Verify and Squash**:
   ```bash
   jj --no-pager status    # verify "(conflict)" disappeared
   jj squash               # squash resolution into the conflicted commit
   ```

*See [references/recovery-playbook.md](./references/recovery-playbook.md) for divergence resolution (`jj converge`, `change_id??`) and operation log time-travel.*

---

## 7. Recovery & Time Travel (Operation Log)

If an operation produced an unexpected result or deleted needed code:

```bash
# 1. View recent operations (newest first)
jj --no-pager op log --limit 10

# 2. Undo the very last operation
jj undo

# 3. Redo what you just undid
jj redo

# 4. Restore the ENTIRE repository to an exact historical operation snapshot
jj op restore <operation_id>

# 5. Recover an abandoned commit
jj new <abandoned_change_id>
```

---

## 8. Essential Revset Queries

Use `jj --no-pager log -r '<revset>'` to query the commit graph:

| Revset Expression | Description |
| :--- | :--- |
| `@` | Current working copy commit |
| `@-` | Immediate parent of working copy |
| `trunk()` | Main remote tracking branch (e.g. `main@origin`) |
| `trunk()..@` | All commits on current stack since trunk |
| `conflicts()` | All commits currently having unresolved conflicts |
| `divergent()` | Commits with duplicate Change IDs (`id??`) |
| `mine()` | Commits authored by the current user |
| `::@` | All ancestors of the working copy |
| `roots(trunk()..@)` | Root commit of current feature stack |

*See [references/revsets.md](./references/revsets.md) for the full revset functional language guide.*
