# Jujutsu Concurrency Architecture & Multi-Agent Safety

This document explains the internal mechanisms that make Jujutsu (`jj`) fundamentally superior to Git for concurrent multi-agent systems.

---

## 1. The Git Multi-Agent Bottleneck

Git was designed for a human developer working in a single terminal session. When multiple autonomous AI agents attempt to operate concurrently on a Git repository:
1. **Coarse File Locks**: Git uses `.git/index.lock` and `.git/refs/heads/<branch>.lock`. Any parallel `git add`, `git commit`, `git checkout`, or `git rebase` fails immediately if another process holds the lock.
2. **Global HEAD**: Git has a single active `HEAD` pointer per worktree. Two agents cannot commit to different branches in the same folder.
3. **Mid-Operation Halts**: A conflict halts git commands midway (`rebase in progress`). Agents must manage complex interactive abort/continue flows.

---

## 2. Jujutsu's Lock-Free Concurrency Model

Jujutsu eliminates repository lock files entirely:

### 2.1 Content-Addressed Operations
- Every command that modifies repository state writes a new **Operation Object** into `.jj/repo/op_store/`.
- Each operation object points to:
  1. Parent operation ID(s).
  2. A **View Object**: Snapshot of all visible heads, bookmarks, tags, and the current working copy commit (`@`) for every registered workspace.
  3. Metadata: timestamp, user, hostname, command line arguments.

### 2.2 Atomic Operation Head Updates
- To commit an operation, Jujutsu writes an empty file whose filename is the new Operation ID into `.jj/repo/op_heads/`, and deletes the file for the parent operation.
- This file write is an atomic filesystem operation.
- No locks are held during the execution of commands.

### 2.3 Automatic 3-Way Operation Merging
- If Agent A and Agent B execute mutating commands simultaneously, both will successfully write new operation heads into `.jj/repo/op_heads/`.
- On the next command run by any agent or human, Jujutsu detects multiple operation heads.
- **Jujutsu automatically executes a 3-way merge of the view objects!**
- Because Agent A was modifying `agent-a@` and Agent B was modifying `agent-b@`, their workspace views are disjoint. The operation log merges automatically and cleanly with zero user or agent intervention.

---

## 3. First-Class Conflicts

If two agents modify conflicting lines of code and their changes are rebased together:
- Git: Aborts rebase, corrupts index, leaves conflicted files on disk with conflict markers.
- Jujutsu: **The rebase succeeds completely**. The conflict is stored as a first-class object in the commit tree. Both agents can continue running commands safely.

---

## 4. Stale Working Copy Semantics

Every Jujutsu command executes three phases:
1. Snapshot working copy files $\to$ record operation.
2. Calculate graph mutations $\to$ commit new operation.
3. Update filesystem working copy to match the operation's `@` commit.

If Phase 3 does not occur for Workspace A (because Workspace B rewrote the commit that Workspace A was based on), Workspace A becomes **stale**:
- Jujutsu protects against file corruption by requiring a synchronization before mutating files in a stale workspace.
- Resolution: `jj workspace update-stale` brings the filesystem files into alignment with the current operation view.
- Automation: Setting `snapshot.auto-update-stale = true` in config allows Jujutsu to update stale workspaces automatically.
