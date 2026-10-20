# Git Interoperability & PR Workflow Guide

Jujutsu is fully compatible with Git remotes and repositories. This guide details how to work with Git repositories, open Pull Requests, and maintain clean synchronizations.

---

## 1. Repository Modes

Jujutsu interacts with Git in one of three modes:
1. **Colocated Workspace** (`.jj/` and `.git/` in the same directory):
   - Default when running `jj git init` in an existing git repo or `jj git clone`.
   - `jj` automatically updates Git's refs and index on every command.
   - **Rule**: All direct `git` commands (both mutating and read-only) are blocked by the safeguard hook in `.jj/` repositories. Use `jj` commands exclusively (`jj --no-pager status`, `jj --no-pager diff`, `jj git fetch`, `jj git push`).
2. **Dedicated Jujutsu Repository with Git Backing Store**:
   - `.jj/` is at the root; the underlying Git store is hidden inside `.jj/repo/store/git`.
   - Requires `jj git push` / `jj git fetch` for all remote interactions.
3. **Pure Native JJ Repository**:
   - Native storage backend, no Git dependencies.

---

## 2. Pull Request Handoff Workflow

When you are ready to submit work as a Git branch or GitHub Pull Request:

### Step 1: Sync with Remote
```bash
jj git fetch
jj rebase -d trunk()
```

### Step 2: Ensure Commits are Described
`jj git push` strictly rejects any push if **any commit** in the pushed range lacks a description!
```bash
# Check descriptions in current stack
jj --no-pager log -r 'trunk()..@-'
# Set message if needed:
jj describe <change_id> -m "feat(scope): concise description"
```

### Step 3: Create and Push Bookmark
```bash
# Option A: Standard Named Bookmark
jj bookmark create feat/auth-flow -r @-
jj git push --bookmark feat/auth-flow

# Option B: Auto-Generated Push Bookmark
jj git push -c @-    # Pushes as "push-<change_id>"
```

### Step 4: Open PR using GitHub CLI (`gh`)
```bash
gh pr create --title "feat(scope): summary" --body "Details..." --head feat/auth-flow
```

---

## 3. Post-Review Updates (Addressing Comments)

When review feedback arrives, update the commit cleanly:

```bash
# 1. Edit directly or squash fixes
jj new feat/auth-flow
# (edit files)
jj squash -m "feat(scope): updated with review feedback"

# 2. Advance bookmark to the revised commit
jj bookmark move feat/auth-flow --to @-

# 3. Push update (Jujutsu safely rewrites the remote branch)
jj git push --bookmark feat/auth-flow
```

---

## 4. Avoiding "Squash-Merge Zombies"

When merging PRs on GitHub:
- **Prefer Rebase-Merge** (`gh pr merge --rebase`):
  - Preserves commit hashes and Change IDs.
  - Jujutsu automatically recognizes that the change has landed on `trunk()`.
- **If Squash-Merge Was Used**:
  - GitHub creates a brand new synthetic commit hash, leaving your local commit orphaned as a "zombie" in `trunk()..visible_heads()`.
  - To clean up:
    ```bash
    jj git fetch
    jj abandon <orphaned_local_change_id>
    ```
