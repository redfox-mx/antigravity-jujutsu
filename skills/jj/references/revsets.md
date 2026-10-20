# Jujutsu (`jj`) Revsets Language Reference

Revsets is a powerful functional query language used in Jujutsu to select sets of commits, revisions, and graph slices.

---

## 1. Core Symbols

| Symbol | Meaning | Example |
| :--- | :--- | :--- |
| `@` | The current working copy commit | `jj log -r @` |
| `@-` | Immediate parent of current working copy | `jj diff -r @-` |
| `@--` | Grandparent of current working copy | `jj log -r @--` |
| `@+` | Immediate children of current working copy | `jj log -r @+` |
| `<name>@` | Working copy commit of a named workspace | `jj diff -r agent-1@` |
| `root()` | Virtual root commit (`00000000`) | `jj log -r 'root()..@'` |
| `<name>@<remote>` | Remote tracking bookmark | `jj log -r main@origin` |
| `<change_id>` | Single commit identified by Change ID | `jj show kntqzsqt` |
| `<commit_id>` | Single commit identified by SHA hash | `jj show 7fd1a60b` |

---

## 2. Graph Traversal Operators

| Operator | Syntax | Description |
| :--- | :--- | :--- |
| **Parents** | `x-` | Immediate parents of `x` |
| **Children** | `x+` | Immediate children of `x` |
| **Ancestors** | `::x` | All ancestors of `x` including `x` (equivalent to `root()::x`) |
| **Descendants** | `x::` | All descendants of `x` including `x` |
| **Ancestry Path** | `x::y` | Commits that are descendants of `x` and ancestors of `y` |
| **Reachable / Range**| `x..y` | Ancestors of `y` that are NOT ancestors of `x` (`::y ~ ::x`) |
| **All Commits** | `all()` or `::` | All visible commits in the repository |
| **Not** | `~x` | All revisions except `x` |
| **Intersection** | `x & y` | Revisions in both `x` and `y` |
| **Union** | `x \| y` | Revisions in either `x` or `y` |
| **Difference** | `x ~ y` | Revisions in `x` but not in `y` |

---

## 3. Built-in Functions & Aliases

| Function / Alias | Description | Example |
| :--- | :--- | :--- |
| `trunk()` | Default remote tracking branch (`main@origin`) | `jj rebase -d trunk()` |
| `mine()` | Commits authored by the current user | `jj log -r 'mine()'` |
| `conflicts()` | Revisions containing unresolved conflicts | `jj log -r 'conflicts()'` |
| `divergent()` | Revisions with divergent Change IDs | `jj log -r 'divergent()'` |
| `heads(x)` | Head commits of revset `x` | `jj log -r 'heads(mine())'` |
| `roots(x)` | Root commits of revset `x` | `jj log -r 'roots(trunk()..@)'` |
| `latest(x, n)` | Latest `n` commits in `x` by committer timestamp | `jj log -r 'latest(all(), 5)'` |
| `description("pattern")` | Commits matching description string/regex | `jj log -r 'description(substring:"fix")'` |
| `author("pattern")` | Commits matching author | `jj log -r 'author("bot")'` |
| `bookmarks()` | All commits pointed to by local bookmarks | `jj log -r 'bookmarks()'` |
| `remote_bookmarks()` | Commits pointed to by remote bookmarks | `jj log -r 'remote_bookmarks()'` |

---

## 4. Practical Recipes for Agents

### View Entire Feature Stack Since Trunk:
```bash
jj --no-pager log -r 'trunk()..@'
```

### View Unpushed Local Work:
```bash
jj --no-pager log -r 'remote_bookmarks()..@'
```

### Check If Any Conflicts Exist:
```bash
jj --no-pager log -r 'conflicts()'
```

### Find Root of Current Feature Branch:
```bash
jj --no-pager log -r 'roots(trunk()..@)'
```
