# Git Command Table

Converted directly from the official Jujutsu documentation: `https://docs.jj-vcs.dev/latest/git-command-table/`

> [!TIP]
> **Built-in CLI Documentation (`--help` / `-h`)**:
> Almost all `jj` commands and subcommands support the `--help` (or `-h`) flag. Whenever you are unsure about command syntax, options, or flags across versions, running `jj <command> --help` or `jj <command> <subcommand> --help` provides immediate, authoritative documentation.

---

Note that all `jj` commands can be run on any commit (not just the working-copy commit), but that's left out of the table to keep it simple. For example, `jj squash -r <revision>` will move the diff from that revision into its parent.

| Use case | Git command | Jujutsu command | Notes |
| :--- | :--- | :--- | :--- |
| Create a new repo | `git init` | `jj git init [--no-colocate]` | Colocated by default in recent versions |
| Clone an existing repo | `git clone <source> <destination> [--origin <remote name>]` | `jj git clone <source> <destination> [--remote <remote name>]` | There is no support for cloning non-Git repos yet. |
| Update the local repo with all bookmarks/branches from a remote | `git fetch [<remote>]` | `jj git fetch [--remote <remote>]` | There is no support for fetching into non-Git repos yet. |
| Update a remote repo with all bookmarks/branches from the local repo | `git push --all [<remote>]` | `jj git push --all [--remote <remote>]` | There is no support for pushing from non-Git repos yet. |
| Update a remote repo with a single bookmark from the local repo | `git push <remote> <bookmark name>` | `jj git push --bookmark <bookmark name> [--remote <remote>]` | There is no support for pushing from non-Git repos yet. |
| Add a remote target to the repo | `git remote add <remote> <url>` | `jj git remote add <remote> <url>` |  |
| Show summary of current work and repo status | `git status` | `jj st` (or `jj --no-pager status`) | Working copy is an automatic commit (`@`) |
| Show diff of the current change | `git diff HEAD` | `jj diff` (or `jj --no-pager diff`) |  |
| Show diff of another change | `git diff <revision>^ <revision>` | `jj diff -r <revision>` |  |
| Show diff from another change to the current change | `git diff <revision>` | `jj diff --from <revision>` |  |
| Show diff from change A to change B | `git diff A B` | `jj diff --from A --to B` |  |
| Show all the changes in A..B | `git diff A...B` | `jj diff -r A..B` |  |
| Show description and diff of a change | `git show <revision>` | `jj show <revision>` |  |
| Add a file to the current change | `touch filename; git add filename` | `touch filename` | Added files are automatically tracked |
| Remove a file from the current change | `git rm filename` | `rm filename` | Deletions are automatically tracked |
| Remove a previously tracked file from the current change, but keep it in the working copy | `git rm --cached filename` | `jj file untrack filename` | File name must match an ignore pattern to remain untracked. See [working copy documentation](../working-copy/#introduction) for more. |
| Modify a file in the current change | `echo stuff >> filename` | `echo stuff >> filename` | Changes auto-amend into `@` |
| Finish work on the current change and start a new change | `git commit -a` | `jj commit` (or `jj new -m "..."`) | `jj commit` creates a new empty working-copy commit on top |
| See compact log graph of ancestors of the current commit | `git log --oneline --graph` | `jj log -r ::@` |  |
| See compact log graph of all reachable commits | `git log --oneline --graph --all` | `jj log -r 'all()'` or `jj log -r ::` | In a Git-backed Jujutsu repository the Git command will also show all commits preserved by Jujutsu, including hidden commits. To exclude all commits only preserved by Jujutsu, replace `--all` by `--exclude refs/jj/* --all`. This will also exclude the Jujutsu-reachable commits though, if they are not Git-reachable. |
| Show compact log graph of commits not on the main branch | `git log --oneline --graph --branches --not upstream/main` | `jj log` |  |
| Show log of commits that have the string "stuff" in the changed lines, also known as the "pickaxe" in Git | `git log -G stuff` | `jj log -r 'diff_lines(regex:stuff)'` |  |
| List versioned files in the working copy | `git ls-files --cached` | `jj file list` |  |
| Search among files versioned in the repository | `git grep foo` | `jj file search --pattern=foo` or `rg --no-require-git foo` |  |
| Abandon the current change and start a new change | `git reset --hard` (cannot be undone) | `jj abandon` | Reversible via `jj undo` |
| Make the current change empty | `git reset --hard` (same as abandoning a change since Git has no concept of a "change") | `jj restore` |  |
| Abandon the parent of the working copy, but keep its diff in the working copy | `git reset --soft HEAD~` | `jj squash --from @-` |  |
| Discard working copy changes in some files | `git restore <paths>...` or `git checkout HEAD -- <paths>...` | `jj restore <paths>...` |  |
| Edit description (commit message) of the current change | Not supported | `jj describe` (use `jj describe -m "..."` for agents) |  |
| Edit description (commit message) of the previous change | `git commit --amend --only` | `jj describe @- -m "..."` |  |
| Edit description (commit message) of any change | `git commit --fixup=reword:X; git rebase --autosquash X^` | `jj describe X -m "..."` |  |
| Temporarily put away the current change | `git stash` | `jj new @-` | The old working-copy commit remains as a sibling commit. The old working-copy commit X can be restored with `jj edit X`. |
| Start working on a new change based on the bookmark/branch | `git switch -c topic main` or `git checkout -b topic main` (may need to stash or commit first) | `jj new main` |  |
| Merge branch A into the current change | `git merge A` | `jj new @ A` |  |
| Check out a named revision (or branch) to examine source | `git checkout v1.0.1` | `jj new v1.0.1` | Creates new empty change on top (see `jj new main`) |
| Move bookmark/branch A onto bookmark/branch B | `git rebase B A` (may need to rebase other descendant branches separately) | `jj rebase -b A -o B` |  |
| Move change A and its descendants onto change B | `git rebase --onto B A^ <some descendant bookmark>` (may need to rebase other descendant bookmarks separately) | `jj rebase -s A -o B` |  |
| Reorder changes from A-B-C-D to A-C-B-D | `git rebase -i A` | `jj rebase -r C --before B` |  |
| Reorder multiple commits at once | `git rebase -i` | `jj arrange` |  |
| Move the diff in the current change into the parent change | `git commit --amend -a` | `jj squash` |  |
| Interactively move part of the diff in the current change into the parent change | `git add -p; git commit --amend` | `jj squash -i` | For agents: use `jj squash --into @- <path>` or `jj absorb` |
| Move the diff in the working copy into an ancestor | `git commit --fixup=X; git rebase --autosquash X^` | `jj squash --into X` |  |
| Interactively move part of the diff in an arbitrary change to another arbitrary change | Not supported | `jj squash -i --from X --into Y` |  |
| Interactively split the changes in the working copy in two | `git commit -p` | `jj split` | For agents: use `jj split <paths> -m "..."` or construction method |
| Interactively split an arbitrary change in two | Not supported (can be emulated with the "edit" action in `git rebase -i`) | `jj split -r <revision>` |  |
| Interactively edit the diff in a given change | Not supported (can be emulated with the "edit" action in `git rebase -i`) | `jj diffedit -r <revision>` |  |
| Resolve conflicts and continue interrupted operation | `echo resolved > filename; git add filename; git rebase/merge/cherry-pick --continue` | `echo resolved > filename; jj squash` | Operations don't get interrupted, so no need to continue. |
| Create a copy of a commit on top of another commit | `git co <destination>; git cherry-pick <source>` | `jj duplicate <source> -o <destination>` |  |
| Find the root of the working copy (or check if in a repo) | `git rev-parse --show-toplevel` | `jj workspace root` |  |
| List bookmarks/branches | `git branch` | `jj bookmark list` or `jj b l` for short |  |
| Create a bookmark/branch | `git branch <name> <revision>` | `jj bookmark create <name> -r <revision>` |  |
| Move a bookmark/branch forward | `git branch -f <name> <revision>` | `jj bookmark move <name> --to <revision>` or `jj b m <name> -t <revision>` for short |  |
| Move a bookmark/branch backward or sideways | `git branch -f <name> <revision>` | `jj bookmark move <name> --to <revision> --allow-backwards` |  |
| Delete a bookmark/branch | `git branch --delete <name>` | `jj bookmark delete <name>` |  |
| List tags | `git tag -l` | `jj tag list` |  |
| Create a tag | `git tag <name> <revision>` | `jj tag set <name> -r <revision>` |  |
| Delete a tag | `git tag -d <name>` | `jj tag delete <name>` |  |
| List tags that contain a revision (targets are descendants of the revision) | `git tag --contains <revision>` | `jj tag list -r '<revision>::'` | Uses jj's revset language. The `::` postfix operator selects all descendants of the given revision. |
| List tags merged into a revision (targets are ancestors of the revision) | `git tag --merged <revision>` | `jj tag list -r '::<revision>'` | Uses jj's revset language. The `::` prefix operator selects all ancestors of the given revision. |
| See log of operations performed on the repo | Not supported | `jj op log` |  |
| Undo the last operation | Not supported | `jj undo` | There is also a matching `jj redo` command to redo the most recently undone operation. |
| Revert an earlier operation | Not supported | `jj op revert` |  |
| Create a commit that cancels out a previous commit | `git revert <revision>` | `jj revert -r <revision> -B @` |  |
| Show what revision and author last modified each line of a file | `git blame <file>` | `jj file annotate <path>` |  |
