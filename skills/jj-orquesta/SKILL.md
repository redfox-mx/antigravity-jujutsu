---
name: jj-orquesta
description: >-
  Use when orchestrating multiple autonomous AI agents working concurrently on
  a codebase using Jujutsu (jj) workspaces. Provides patterns for spawning isolated
  subagent workspaces, assigning parallel tasks on independent Change IDs, lock-free
  concurrency, cross-workspace progress monitoring, handling stale workspaces
  (jj workspace update-stale), reviewing and rebasing agent changes onto trunk,
  and safely cleaning up workspaces (jj workspace forget) without losing history.
---

# Jujutsu Multi-Agent Orchestration (`/jj-orquesta`)

This skill defines the multi-agent orchestration architecture utilizing **Jujutsu (`jj`) workspaces**. It empowers a lead agent (orchestrator) to spawn, supervise, coordinate, and integrate parallel worker subagents working simultaneously on the same repository without lock contention, branch collisions, or dirty working copy conflicts.

---

## 1. Why Jujutsu for Multi-Agent Systems?

Traditional VCSs like Git fail in multi-agent environments due to fundamental architectural limits:
- **Lock Contention**: Git uses coarse file locks (`.git/index.lock`, `refs/heads/*`). Multiple autonomous agents executing simultaneous commits trigger race conditions and lock crashes.
- **Single Working Tree**: Agents working in the same folder clobber each other's edits, or require painful branch hopping.
- **Jujutsu Solution**:
  1. **Native Workspaces (`jj workspace`)**: Each subagent gets a dedicated directory linked back to `.jj/repo`.
  2. **Isolated Working Copies (`<name>@`)**: Every workspace has its own independent working copy commit. Subagents edit their own Change IDs without interfering with other agents.
  3. **Lock-Free Concurrency**: Operations append atomically to content-addressed stores. Concurrent operations trigger automatic 3-way merges of repository views on the next command.
  4. **First-Class Conflicts**: If subagents edit overlapping code, conflicts are recorded safely inside commits rather than aborting runs or destroying files.
  5. **Clean Teardown**: `jj workspace forget` disconnects the workspace while preserving all commits and Change IDs permanently in the graph.

---

## 2. Agent Roles & Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Lead Agent (Orchestrator)                   │
│         Root Workspace (CWD) - Working Copy: default@       │
│  - Plans tasks & defines sub-goals                          │
│  - Spawns & monitors worker workspaces                      │
│  - Performs rebases, integration tests, & pushes PRs        │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌───────────────────────────────┐ ┌───────────────────────────┐
│       Worker Subagent 1       │ │     Worker Subagent 2     │
│   Path: .workspaces/agent-ui  │ │ Path: .workspaces/agent-api│
│  Working Copy: agent-ui@      │ │ Working Copy: agent-api@  │
│  - Implements Frontend Task   │ │ - Implements Backend Task │
│  - Edits dedicated Change ID  │ │ - Edits dedicated Change ID│
└───────────────────────────────┘ └───────────────────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
               ┌───────────────────────────────┐
               │ Shared Jujutsu Repo (.jj/repo)│
               │  - Central Object Store       │
               │  - Operation Log (Lock-Free)  │
               └───────────────────────────────┘
```

---

## 3. End-to-End Orchestration Lifecycle

### Step 1: Pre-Flight & Workspace Provisioning

From the repository root, the Lead Agent creates isolated workspaces for subagents:

```bash
# 1. Ensure the workspace container directory is ignored
if (-not (Select-String -Path .gitignore -Pattern "^\.workspaces/" -Quiet)) {
    Add-Content -Path .gitignore -Value "`n.workspaces/"
}

# 2. Provision worker workspace for Agent A off trunk
jj workspace add .workspaces/agent-frontend --name agent-frontend -r trunk() -m "feat(ui): implement user dashboard"

# 3. Provision worker workspace for Agent B off trunk
jj workspace add .workspaces/agent-backend --name agent-backend -r trunk() -m "feat(api): implement user metrics API"

# 4. Verify registered workspaces
jj --no-pager workspace list
```

### Step 2: Dispatch Subagents to Workspaces

The Lead invokes subagents (via `invoke_subagent`), directing each subagent to run within its allocated directory:

- **Agent Frontend**: Work inside `.workspaces/agent-frontend`
- **Agent Backend**: Work inside `.workspaces/agent-backend`

Inside its workspace, the subagent performs normal development:
```bash
# Subagent checks status (shows agent-frontend@)
jj --no-pager status

# Subagent edits code...

# Subagent updates description or adds logical steps
jj describe -m "feat(ui): completed dashboard widgets"
jj new -m "feat(ui): added test suite"
```

### Step 3: Real-Time Supervision from Root Workspace

The Lead Agent monitors progress without changing directories or checking out branches!

```bash
# View all active workspaces and their current working commits
jj --no-pager log -r 'visible_heads() | @ | agent-frontend@ | agent-backend@'

# Inspect the exact diff of Agent Frontend
jj --no-pager diff -r agent-frontend@

# Compare work between the two agents
jj --no-pager diff --from agent-backend@ --to agent-frontend@
```

### Step 4: Synchronizing Stale Workspaces

If the Lead Agent rebases `trunk()` or amends parent revisions, worker workspaces become "stale".

```bash
# Update stale workspace from its own folder:
cd .workspaces/agent-frontend
jj workspace update-stale

# Or update stale workspace remotely from root:
jj -R .workspaces/agent-frontend workspace update-stale
```

> [!TIP]
> You can automate stale updates by running:
> `jj config set --repo snapshot.auto-update-stale true`

### Step 5: Integration & Merging into Trunk

When a worker completes its task:

```bash
# 1. Lead identifies the worker's changes
$FRONTEND_CHANGE = (jj log -r 'agent-frontend@-' --no-graph -T 'change_id')

# 2. Rebase the worker's completed changes onto the latest trunk
jj rebase -s $FRONTEND_CHANGE -d trunk()

# 3. Run validation tests in root workspace
npm test   # or pytest, cargo test, etc.
```

### Step 6: Handling Conflicts Between Parallel Agents

If Agent A and Agent B edited overlapping code, rebasing will flag `(conflict)`:

- **Option 1 (Lead Resolves Immediately)**:
  ```bash
  jj --no-pager resolve --list
  # Lead edits conflict markers out of files
  jj squash
  ```
- **Option 2 (Lead Delegates Resolution to Subagent)**:
  Lead rebases worker onto conflicted state, worker runs `jj workspace update-stale`, resolves markers, and runs `jj squash`.

### Step 7: Clean Workspace Teardown

Once changes are rebased and integrated, clean up the workspace:

```bash
# 1. (Optional) Create a named bookmark on the integrated change for PR handoff
jj bookmark create feat/user-dashboard -r $FRONTEND_CHANGE

# 2. Forget the workspace in Jujutsu (stops tracking in repository metadata)
jj workspace forget agent-frontend

# 3. Delete the physical workspace folder from disk safely
Remove-Item -Recurse -Force .workspaces/agent-frontend    # PowerShell
# or: rm -rf .workspaces/agent-frontend                  # Unix
```

> [!IMPORTANT]
> **Windows Teardown Rule**: On Windows, the subagent must exit or the Lead must execute `Remove-Item` from **outside** the `.workspaces/agent-*` directory to prevent file lock errors (`EPERM: resource busy or locked`).

---

## 4. Best Practices for Orchestration

1. **One Workspace Per Concurrent Agent**: Never point two active agents at the same working directory.
2. **Never `jj edit` Another Agent's `@`**: Modifying another workspace's active working copy commit creates divergent changes (`change_id??`).
3. **Keep Workspaces in `.workspaces/`**: Keeps the project root clean and ensures workspace directories are ignored by git.
4. **Communicate via Stable Change IDs**: Agents should report their results using Change IDs rather than ephemeral commit hashes.

> [!TIP]
> **Built-in Documentation via `--help`**:
> All workspace commands support `--help` (e.g. `jj workspace --help`, `jj workspace add --help`, `jj workspace update-stale --help`, `jj workspace list --help`, `jj workspace forget --help`), providing instant access to options and flags directly from the CLI.

*See detailed reference guides in `references/`:*
- [references/concurrency-architecture.md](./references/concurrency-architecture.md)
- [references/workspace-commands.md](./references/workspace-commands.md)
- [references/orchestration-patterns.md](./references/orchestration-patterns.md)
