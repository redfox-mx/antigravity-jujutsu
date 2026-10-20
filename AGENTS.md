# Antigravity Jujutsu (`jj`) Plugin

This repository contains a plugin for Google Antigravity designed to provide first-class support, workflows, and integrations for the **Jujutsu (`jj`)** version control system.

---

## What is Jujutsu (`jj`)?

[Jujutsu](https://github.com/jj-vcs/jj) is a modern, Git-compatible distributed version control system (DVCS) engineered to deliver a superior developer experience, increased flexibility, and safety when manipulating version history.

### Key Concepts of `jj`
- **Working copy as a commit:** Unlike Git, in `jj` the working copy is always an automatic commit (`@`). There is no staging area or index.
- **Stable Change IDs:** Every change maintains a stable identifier that survives history rewrites (rebases, amends, squashes).
- **Recoverable history (Operation Log):** Every command appends to an immutable operation log (`jj op log`), making accidental mistakes trivially reversible (`jj undo`, `jj op restore`).
- **First-class conflicts:** Conflicts do not halt or abort operations; they are safely stored inside commits and can be resolved asynchronously.
- **Powerful Revsets:** An expressive functional query language for selecting, inspecting, and manipulating revisions and graph slices.
- **Git Compatibility:** Can operate directly on local and remote Git repositories (`colocated` or backed by a Git storage engine). See the full [Git vs. Jujutsu Command Comparison Table](skills/jj/references/git-command-table.md).
- **Built-in CLI Documentation (`--help`):** Almost all `jj` commands and subcommands support the `--help` (or `-h`) flag. Whenever an agent or developer is unsure about command syntax, options, or flags across versions, running `jj <command> --help` or `jj <command> <subcommand> --help` provides immediate, authoritative documentation.

---

## Plugin Objectives

1. **Skills and Workflows:** Provide guided skills for Antigravity agents to interact idiomatically with `jj` repositories (change creation, revset navigation, conflict resolution, operation log management).
2. **Rules and Best Practices:** Enforce rules ensuring agents respect `jj` conventions (avoiding traditional Git habits such as `git add` when operating in `jj` repositories).
3. **Tools and Integrations:** Facilitate lifecycle hooks, safety safeguards, and MCP tooling for structured inspection of revisions and workspaces.

---

## Bundled Skills

The plugin exposes two specialized skills ready for use via slash commands or autonomous model decisions:

1. **`/jj` (`skills/jj/SKILL.md`)**:
   - Daily version control workflow for individual agents operating in Jujutsu (`.jj/`) repositories.
   - Non-negotiable agent safety rules (prevent pager hangs with `--no-pager`, avoid interactive TUI editors with explicit `-m`, prohibit direct mutating Git commands).
   - Non-interactive history manipulation (`jj squash`, `jj absorb`, hunk splitting by construction).
   - First-class conflict detection and resolution.
   - Git remote synchronization and PR creation workflows.
   - Time-travel recovery via the operation log (`jj undo`, `jj op restore`).

2. **`/jj-orquesta` (`skills/jj-orquesta/SKILL.md`)**:
   - Concurrent, lock-free multi-agent orchestration using `jj workspace`.
   - Total filesystem isolation across agents via dedicated working copies (`<workspace>@`).
   - Real-time cross-workspace monitoring from the root workspace without branch switching or directory hopping.
   - Resynchronization of out-of-sync working copies (`jj workspace update-stale`).
   - Reviewing, rebasing, and integrating subagent contributions onto the main trunk (`trunk()`).
   - Clean, safe workspace teardown (`jj workspace forget`) preserving all revision history in the DAG.

---

## Guidelines for Agents

- Maintain modular architecture adhering to Antigravity plugin conventions (`skills/`, `rules/`, `plugin.json`).
- Clearly document the purpose and expected commands for each skill.
- Prioritize operational safety by leveraging the operation log (`jj undo`) when handling unexpected failures or unintended changes.
