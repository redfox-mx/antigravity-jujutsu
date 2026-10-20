# Antigravity Jujutsu (`jj`) Plugin — Evaluation & Improvements Plan

## 1. Skill & Component Evaluations (1–10)

### Skill 1: `jj` ([skills/jj/SKILL.md](./skills/jj/SKILL.md)) — **9.0 / 10**

**Strengths:**
- **Exemplary Progressive Disclosure:** The main `SKILL.md` stays focused (~200 lines) while delegating deep dives into 6 well-organized reference files (`agent-safety.md`, `command-cheatsheet.md`, `git-command-table.md`, `git-interop.md`, `recovery-playbook.md`, `revsets.md`).
- **High-Signal Agent Mental Model:** Clearly addresses the exact failure modes AI agents hit with Jujutsu: pager hangs (`--no-pager`), TUI editor hangs (`-m` required, bare `jj split`/`jj squash -i` forbidden), commit absorption (`jj describe` + `jj new` rhythm), and worktree shadowing.
- **Non-Interactive Hunk Splitting:** Providing the "Construction Method" and `jj absorb` gives agents a deterministic way to split commits without interactive TUIs.

**Gaps to Address:**
- Contradicts the plugin's own `hooks/safeguard.py` hook regarding read-only `git` commands (see Improvement #1 below).
- Mixes PowerShell and Bash syntax inside `bash` code fences (e.g., `$ORIG = (jj log ...)` in `SKILL.md` and `2>$null` in `references/agent-safety.md`).
- Uses legacy `jj rebase -d` syntax in several places (`-d` was superseded by `-o` / `--onto` in newer `jj` versions, which is already used in `references/command-cheatsheet.md` but not in `SKILL.md`).

---

### Skill 2: `jj-orquesta` ([skills/jj-orquesta/SKILL.md](./skills/jj-orquesta/SKILL.md)) — **8.5 / 10**

**Strengths:**
- **Clear Multi-Agent Architecture:** The ASCII architecture diagram and step-by-step lifecycle (Provisioning $\to$ Dispatch $\to$ Supervision $\to$ Stale Sync $\to$ Integration $\to$ Teardown) are easy for an orchestrator agent to follow.
- **Strong Domain Coverage:** Covers lock-free operation log merging (`references/concurrency-architecture.md`), 3 practical orchestration patterns (`references/orchestration-patterns.md`), and the critical Windows directory-lock teardown caveat (`jj workspace forget` before `Remove-Item`).

**Gaps to Address:**
- **CLI Flag Verification (`jj workspace add -m`):** In `SKILL.md`, `references/workspace-commands.md`, and `references/orchestration-patterns.md`, the skill instructs agents to run `jj workspace add <path> --name <name> -r trunk() -m "feat: ..."`. Verify whether the target `jj` version supports `-m/--message` on `jj workspace add` or if a separate `jj -R <path> describe -m "..."` step is required.
- **Missing Integration with Antigravity's Subagent & Command Model:** In Antigravity, `run_command` executes in the workspace root by default and does not persist `cd` across calls. The skill should explicitly instruct subagents how to scope commands (e.g., `jj -R .workspaces/<agent>` or `cd .workspaces/<agent>; ...`) and use full paths in `read_file`/`edit_file`/`write_file`.
- **No Executable Helper Scripts (`scripts/`):** Provisioning and tearing down workspaces are multi-step operations ideal for helper scripts under `skills/jj-orquesta/scripts/`.

---

### Lifecycle Hooks & Plugin Packaging ([hooks/](./hooks/), [plugin.json](./plugin.json), [AGENTS.md](./AGENTS.md)) — **7.5 / 10**

**Strengths:**
- Clean `SessionStart` (`hooks/announce.py`) and `PreToolUse` (`hooks/safeguard.py`) hook contracts matching Antigravity's protojson specification.
- Thoughtful shell tokenization in `contains_forbidden_git` handling `$(...)`, backticks, wrapper commands (`sudo`, `env`), and nested shells (`powershell -Command`, `bash -c`).

---

## 2. Prioritized Improvements Checklist

### Priority 1: Align `safeguard.py` and `jj` Skill on Read-Only Git Commands (Critical)
- [x] **Problem:** `skills/jj/SKILL.md` and `skills/jj/references/agent-safety.md` instruct agents to run read-only Git commands (`git status`, `git log`, `git diff`, `git rev-parse --show-toplevel`), whereas `hooks/safeguard.py` unconditionally blocks **all** `git` commands (`if executable in ["git", "git.exe"]: return True`).
- [x] **Action:** Aligned `skills/jj/SKILL.md`, `skills/jj/references/agent-safety.md`, and `skills/jj/references/git-interop.md` with `hooks/safeguard.py` and `hooks/announce.py` to state that all direct `git` commands are blocked by the hook and provide pure-`jj` alternatives (`jj --no-pager status`, `jj --no-pager log`, `jj --no-pager diff`, `jj workspace root`).

### Priority 2: Fix Hook Crash & Portability Issues in `hooks/` (High)
- [x] **Fix `IndexError` in `hooks/safeguard.py`:** Replaced `cwd = args.get("Cwd") or payload.get("workspacePaths", [])[0] or os.getcwd()` with safe list access when `workspacePaths` is empty or omitted.
- [x] **Fix Windows Case-Sensitivity & Path Parsing in `hooks/safeguard.py`:** Normalized backslashes prior to `shlex(posix=True)` and normalized `executable` and `flag` with `.lower()` so `Git.exe`, `GIT`, `PowerShell.exe`, or `-Command` are properly matched.
- [x] **Relax Python Version Constraint in `pyproject.toml`:** Changed `requires-python = "==3.12.15"` to `requires-python = ">=3.10"` and updated `uv.lock`.

### Priority 3: Restructure Plugin Rules into `rules/AGENTS.md` (High)
- [ ] **Move Repository Documentation to `README.md`:** Rename the root `AGENTS.md` (which reads like plugin documentation) to `README.md`.
- [ ] **Create `rules/AGENTS.md`:** Following the Antigravity Plugin Specification (`plugins/<plugin_name>/rules/AGENTS.md`), add a concise operational rule file under `rules/AGENTS.md` so rules are properly ingested when the plugin is active across any workspace.

### Priority 4: Enhance `PreToolUse` Safeguard for Interactive `jj` Commands (Medium)
- [ ] **Prevent Interactive `jj` Hangs in `hooks/safeguard.py`:** Block bare interactive `jj` invocations (`jj split` without paths, `jj squash -i`, `jj diffedit`, bare `jj describe` / `jj commit` without `-m`) or auto-inject `--no-pager` via `PreToolUse` `"overwrite"`.
- [ ] **Add Unit Tests (`tests/test_safeguard.py`):** Add automated tests covering `contains_forbidden_git` and `jj` command safeguards across Windows and POSIX shell syntax.

### Priority 5: Subagent Dispatch & Helper Scripts in `jj-orquesta` (Medium)
- [ ] **Add Subagent Prompt Template:** Update `skills/jj-orquesta/SKILL.md` ("Step 2: Dispatch Subagents to Workspaces") with a concrete `invoke_subagent` prompt template reminding subagents that `run_command` does not persist working directory changes across calls and that file tools must target `<repo_root>/.workspaces/<agent-name>/...`.
- [ ] **Verify `jj workspace add` Flags:** Confirm `-m` support on `jj workspace add` vs `jj -R <path> describe -m "..."` and update examples accordingly.
