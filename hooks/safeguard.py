import json
import os
import re
import shlex
import sys
from pathlib import Path

try:
    from hooks.utils import is_jj_repo
except ImportError:
    from utils import is_jj_repo

OPERATORS = {"&&", "||", ";", "|", "&", "(", ")"}
WRAPPERS = {"sudo", "env", "time", "nohup", "nice", "xargs", "command"}
SHELLS = {
    "cmd", "cmd.exe", "powershell", "powershell.exe",
    "pwsh", "pwsh.exe", "sh", "bash", "zsh", "dash", "ksh"
}
SHELL_FLAGS = {"-c", "-command", "/c", "/k", "/command"}

# Search content inside $(...) or `...`
SUBSTITUTION_RE = re.compile(r"\$\(([^)]+)\)|`([^`]+)`")


def extract_substitutions(text: str) -> list[str]:
    """Extract commands inside $(...) or `...`."""
    return [m.group(1) or m.group(2) for m in SUBSTITUTION_RE.finditer(text)]


def split_into_subcommands(tokens: list[str]) -> list[list[str]]:
    subcommands, current = [], []
    for token in tokens:
        if token in OPERATORS:
            if current:
                subcommands.append(current)
                current = []
        # Ignore $ left over when shlex separates $(cmd)
        elif token == "$" and not current:
            continue
        else:
            current.append(token)
    if current:
        subcommands.append(current)
    return subcommands


def is_env_assignment(token: str) -> bool:
    return "=" in token and not token.startswith("-")


def contains_forbidden_git(cmd_line: str) -> bool:
    # 1. Check substitutions $(...) or `...` (even inside quoted strings)
    for sub in extract_substitutions(cmd_line):
        if contains_forbidden_git(sub):
            return True

    # 2. Tokenize separating also parentheses and operators
    normalized_cmd = cmd_line.replace("\\", "/")
    try:
        lexer = shlex.shlex(normalized_cmd, posix=True, punctuation_chars="();<>|&")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = normalized_cmd.split()

    # 3. Analyze each subcommand
    for subcmd in split_into_subcommands(tokens):
        idx = 0
        while idx < len(subcmd) and (
            is_env_assignment(subcmd[idx])
            or os.path.basename(subcmd[idx]).lower() in WRAPPERS
        ):
            idx += 1

        if idx >= len(subcmd):
            continue

        executable = os.path.basename(subcmd[idx]).lower()

        if executable in {"jj", "jj.exe"}:
            continue

        if executable in {"git", "git.exe"}:
            return True

        if executable in SHELLS:
            for j in range(idx + 1, len(subcmd) - 1):
                flag = subcmd[j].lower()
                if flag in SHELL_FLAGS:
                    if contains_forbidden_git(subcmd[j + 1]):
                        return True

    return False

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow", "reason": "Invalid JSON input"}))
        sys.exit(0)

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    if tool_name != "run_command":
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    args = tool_call.get("args", {})
    cmd_line = args.get("CommandLine", "")
    workspace_paths = payload.get("workspacePaths", [])
    cwd = args.get("Cwd") or (workspace_paths[0] if workspace_paths else os.getcwd())

    if is_jj_repo(cwd) and contains_forbidden_git(cmd_line):
        response = {
            "decision": "deny",
            "reason": (
                "Direct git commands are not permitted in Jujutsu "
                "repositories. A Jujutsu repository was detected at "
                f"{Path(cwd).resolve()}. In Jujutsu (jj), the working "
                "copy is always an automatic commit and history is tracked "
                "through stable Change IDs. Modifying Git directly in a "
                "Jujutsu-managed repository (especially colocated "
                "repositories) can desynchronize or corrupt Jujutsu's state. "
                "Please use Jujutsu commands instead."
            )
        }
        print(json.dumps(response))
        sys.exit(0)

    # Si todo está bien, salimos con 0 sin bloquear
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
