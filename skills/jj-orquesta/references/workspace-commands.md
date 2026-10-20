# Jujutsu Workspace Command Reference

Comprehensive guide to the `jj workspace` subcommands used by orchestration agents.

---

## 1. `jj workspace add`

Spawns a new independent working directory attached to the central repository.

### Syntax:
```bash
jj workspace add [OPTIONS] <DESTINATION>
```

### Key Options:
- `--name <NAME>`: Custom name for the workspace (defaults to the directory basename). This name is used to prefix the workspace's working copy in revsets (`<NAME>@`).
- `-r, --revision <REVSET>`: The parent revision for the newly created working-copy commit. Defaults to the parent of the current workspace's `@`. To base off main trunk: `-r trunk()`.
- `-m, --message <MSG>`: Initial description/message for the newly spawned working copy commit.
- `--colocate` / `--no-colocate`: Controls whether an underlying Git worktree is created alongside (in colocated repositories).

### Examples:
```bash
# Create worker workspace off trunk with task description
jj workspace add .workspaces/agent-1 --name agent-1 -r trunk() -m "feat(auth): add OAuth2 provider"
```

---

## 2. `jj workspace list`

Lists all workspaces registered to the repository.

### Syntax:
```bash
jj workspace list [OPTIONS]
```

### Programmatic Templating (`-T`):
The Lead Agent can extract workspace paths and names cleanly:
```bash
# Output name and root path tab-separated:
jj workspace list -T 'name ++ "\t" ++ root() ++ "\n"'
```

---

## 3. `jj workspace root`

Displays the absolute path to the root of a workspace.

### Syntax:
```bash
jj workspace root [--name <NAME>]
```

---

## 4. `jj workspace update-stale`

Brings physical files in a stale workspace into alignment with the latest repository operation view.

### Syntax:
```bash
jj workspace update-stale
```

### When to use:
- Run whenever another workspace or the lead orchestrator rebased or modified the parent commit of this workspace.
- Can be run from the root workspace using `-R`:
  ```bash
  jj -R .workspaces/agent-1 workspace update-stale
  ```

---

## 5. `jj workspace rename`

Renames the active workspace in repository metadata.

### Syntax:
```bash
jj workspace rename <NEW_NAME>
```

---

## 6. `jj workspace forget` vs. `jj workspace remove`

Jujutsu provides two ways to disconnect and clean up workspaces:

| Command | Metadata Action | Disk Action | Windows Safety | Recommended for Agents? |
| :--- | :--- | :--- | :--- | :--- |
| **`jj workspace forget [NAME]`** | Unlinks workspace from repo tracking | **Leaves files untouched** on disk | 100% safe | **YES** (followed by clean directory deletion) |
| **`jj workspace remove [NAME]`** | Unlinks workspace from repo tracking | Deletes files from disk | May fail if files are open/locked | Use with caution |

### The Standard Safe Teardown Pattern:
```bash
# 1. Unlink from jj repository
jj workspace forget agent-1

# 2. Delete directory using OS shell
Remove-Item -Recurse -Force .workspaces/agent-1    # Windows PowerShell
# or: rm -rf .workspaces/agent-1                  # Linux / macOS
```
