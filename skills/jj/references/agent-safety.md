# Agent Safety Guidelines for Jujutsu (`jj`)

Autonomous coding agents execute without interactive terminals. Misconfigurations or running interactive commands will cause the agent to freeze indefinitely waiting for input that will never arrive. Follow these non-negotiable rules.

---

## 1. Pagers Will Freeze the Agent

By default, `jj` commands that display output (`status`, `log`, `diff`, `op log`, `show`) route through a terminal pager (typically `less`).

### The Rule:
Always pass `--no-pager` on every command that produces output:
```bash
jj --no-pager status
jj --no-pager log --limit 10
jj --no-pager diff
```

### Important Warning:
**Do NOT** run `jj config set --user ui.paginate never`. That writes to the user's persistent global configuration file and changes how `jj` behaves for the human developer interactively. Use `--no-pager` per invocation or specify `--config ui.paginate=never` in the command line flags.

---

## 2. Editor Hangs on Bare Commands

In Git, commands like `git commit` open `$EDITOR` if no message is provided. In Jujutsu, many more commands open an interactive text editor or TUI by default.

### Strictly Prohibited Bare Invocations:
| Forbidden Command | Why It Fails | Safe Non-Interactive Replacement |
| :--- | :--- | :--- |
| `jj describe` | Opens editor to prompt for commit message | `jj describe -m "feat: message"` |
| `jj commit` | Opens editor to prompt for message | `jj commit -m "feat: message"` |
| `jj new` without `-m` | Creates commit with no message | `jj new -m "feat: next task"` |
| `jj split` (bare) | Launches interactive diff-editing TUI | `jj split <paths> -m "msg"` or construction method |
| `jj squash -i` | Launches 3-pane interactive diff tool | `jj squash --into @- <path>` or `jj absorb` |
| `jj resolve` (bare) | Launches external 3-way merge tool | Edit conflict markers directly in file editor |
| `jj diffedit` | Launches interactive editor | Edit files directly in workspace |

---

## 3. The Working Copy is a Mutable Commit

- In Git, file edits sit in your working tree uncommitted until you explicitly run `git add` and `git commit`.
- In Jujutsu, **the working copy is always an active commit (`@`)**.
- As soon as any `jj` command runs, changes in the filesystem are snapshotted into `@`.

### Prevention of "Commit Absorption":
If you perform multiple development steps without running `jj new`, all edits flow into the same single commit (`@`).
**Required Rhythm:**
1. Work on first logical unit.
2. `jj describe -m "feat: first unit"`
3. `jj new -m "feat: second unit"`
4. Work on second unit.

---

## 4. Colocated Repository Rules

In a repository managed by Jujutsu (where `.jj/` exists in the repository or an ancestor directory):
1. **Never run direct Git commands**: The plugin's `PreToolUse` safeguard hook blocks all direct `git` commands (both mutating commands like `git add`/`git commit` and read-only commands like `git status`/`git log`/`git diff`) to protect repository integrity and prevent state desynchronization.
2. **Use Jujutsu commands exclusively**:
   - Instead of `git status` $\to$ `jj --no-pager status`
   - Instead of `git log` $\to$ `jj --no-pager log`
   - Instead of `git diff` $\to$ `jj --no-pager diff`
   - Instead of `git fetch` $\to$ `jj git fetch`
   - Instead of `git push` $\to$ `jj git push`
   - Instead of `git rev-parse --show-toplevel` $\to$ `jj workspace root`
3. If an external desynchronization occurs: run `jj git import` to bring Git's index state into Jujutsu, or `jj git export` to update Git refs.

---

## 5. Worktree Shadowing Trap

When an agent runner puts the agent into an isolated Git worktree or nested subfolder:
- If that directory lacks its own `.jj/` directory but resides on a path under a parent repository that *has* a `.jj/` directory:
- Running `jj` will traverse up the filesystem and operate on the **parent repository's files**, not the intended directory!
- Direct `git` commands will also be blocked by the safeguard hook because `.jj/` is detected in an ancestor directory.
- **Check before running**:
  ```bash
  jj_root=$(jj workspace root)
  current_dir=$(pwd)
  ```
  If `$jj_root` does not match `$current_dir` (and the current directory has no `.jj/` directory), you are shadowed. Do not run `jj` commands to prevent unintentionally modifying the parent repository.
