# Jujutsu (`jj`) Recovery Playbook: Operation Log & Conflict Resolution

The Jujutsu **Operation Log (`op log`)** is an absolute safety net. Unlike Git's fragile `reflog` and detached HEAD states, Jujutsu records an immutable snapshot of the entire repository state on every single mutating command.

---

## 1. Initial Assessment: "Something Looks Wrong"

Run these commands to inspect repository health without modifying state:

```bash
# 1. View recent operations (what commands just ran)
jj --no-pager op log --limit 10

# 2. Check working copy and conflict status
jj --no-pager status

# 3. View the recent revision graph
jj --no-pager log --limit 15
```

---

## 2. Operation Log Time Travel

### Undo Last Command:
```bash
jj undo
```
Reverts the last operation, restoring bookmarks, commits, and working tree files to their prior state.

### Redo Undone Command:
```bash
jj redo
```

### Restore to Specific Operation:
```bash
jj op restore <operation_id>
```
Resets the entire repository to the exact state after `<operation_id>`. Use `jj --no-pager op log` to find the target operation hash.

### Inspect Historical Operation State (Read-Only):
```bash
jj --at-op=<operation_id> log
jj --at-op=<operation_id> diff
```

---

## 3. Resolving First-Class Conflicts

Conflicts occur when divergent changes modify the same file regions. Jujutsu stores conflicts as first-class objects within commits.

### Identify:
```bash
jj --no-pager resolve --list
```

### Resolve Without TUIs:
1. Open the conflicted file.
2. Search for markers: `<<<<<<<`, `%%%%%%%`, `+++++++`, `>>>>>>>`.
3. Edit the file to contain the final desired code without any marker lines.
4. Save the file.
5. Check status:
   ```bash
   jj --no-pager status
   ```
6. Squash the resolution into the conflicted commit:
   ```bash
   jj squash
   ```

---

## 4. Resolving Divergent Changes (`change_id??`)

A divergent change occurs when multiple visible commits share the same Change ID (shown in `jj log` as `mzvwutvl/0` and `mzvwutvl/1`).

### Resolution Strategies:

1. **Automatic Convergence**:
   ```bash
   jj converge
   ```
2. **Abandon Obsolete Copy**:
   If one version is superseded:
   ```bash
   jj abandon <unwanted_commit_id>
   ```
   *(Must reference by commit ID or offset `id/1`, not bare Change ID)*.
3. **Assign New Change ID**:
   If both versions should be kept as separate changes:
   ```bash
   jj metaedit --update-change-id <commit_id>
   ```
4. **Squash Copies Together**:
   ```bash
   jj squash --from <source_commit_id> --into <target_commit_id>
   ```

---

## 5. Recovering "Lost" or Abandoned Commits

Jujutsu never destroys commits immediately:
```bash
# 1. Show hidden/abandoned commits
jj --no-pager log --hidden -r 'all()' --limit 20

# 2. Resurrect by creating a new change on top of it
jj new <abandoned_change_id>
```
