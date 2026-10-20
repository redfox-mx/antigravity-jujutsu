# Multi-Agent Orchestration Patterns & Recipes

Practical architectural patterns for orchestrating teams of autonomous agents using Jujutsu workspaces.

---

## Pattern 1: Fan-Out / Fan-In (Parallel Feature Teams)

### Use Case:
Multiple subagents implement independent modules simultaneously (e.g. Frontend UI, Backend API, Documentation).

### Sequence:
1. **Fan-Out (Lead Agent)**:
   ```bash
   jj workspace add .workspaces/agent-ui --name agent-ui -r trunk() -m "feat(ui): client components"
   jj workspace add .workspaces/agent-api --name agent-api -r trunk() -m "feat(api): graphql schema"
   jj workspace add .workspaces/agent-docs --name agent-docs -r trunk() -m "docs: API reference"
   ```
2. **Parallel Autonomous Execution**:
   - Subagent `agent-ui` edits in `.workspaces/agent-ui`
   - Subagent `agent-api` edits in `.workspaces/agent-api`
   - Subagent `agent-docs` edits in `.workspaces/agent-docs`
3. **Fan-In Integration (Lead Agent)**:
   Lead integrates the completed changes onto `trunk()` in order:
   ```bash
   # Rebase API first
   jj rebase -s roots(trunk()..agent-api@) -d trunk()
   # Run tests
   pytest tests/api/

   # Rebase UI second
   jj rebase -s roots(trunk()..agent-ui@) -d trunk()
   npm test

   # Rebase Docs third
   jj rebase -s roots(trunk()..agent-docs@) -d trunk()
   ```
4. **Teardown**:
   ```bash
   jj workspace forget agent-ui agent-api agent-docs
   Remove-Item -Recurse -Force .workspaces
   ```

---

## Pattern 2: Speculative Implementation & Competitor Agents

### Use Case:
Two subagents attempt different algorithmic solutions to the same problem. The lead inspects both, runs benchmarks, picks the winner, and discards the other.

### Sequence:
1. **Spawn Two Candidates**:
   ```bash
   jj workspace add .workspaces/solution-a --name sol-a -r trunk() -m "approach: recursive dynamic programming"
   jj workspace add .workspaces/solution-b --name sol-b -r trunk() -m "approach: iterative bitmask"
   ```
2. **Lead Compares Diffs**:
   ```bash
   jj --no-pager diff --from sol-a@ --to sol-b@
   ```
3. **Select Winner (e.g. Solution B)**:
   ```bash
   # Rebase Solution B onto trunk
   jj rebase -s sol-b@ -d trunk()

   # Clean up candidate workspaces
   jj workspace forget sol-a sol-b
   Remove-Item -Recurse -Force .workspaces/solution-a, .workspaces/solution-b

   # (Optional) Abandon candidate A commit if never needed:
   jj abandon <sol_a_change_id>
   ```

---

## Pattern 3: Automated Reviewer / Fixer Loop

### Use Case:
Worker agent writes code; reviewer agent runs in a second workspace to audit or run linters, squashing fixes back.

### Sequence:
1. Worker completes change in `.workspaces/dev-agent`.
2. Reviewer inspects diff from root workspace:
   ```bash
   jj --no-pager diff -r dev-agent@
   ```
3. Reviewer applies formatting or security fixes:
   ```bash
   jj absorb --into dev-agent@
   ```
4. Both workspaces stay in sync via `jj workspace update-stale`.
