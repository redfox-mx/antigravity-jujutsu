import json
import os
import sys

try:
    from hooks.utils import is_jj_repo
except ImportError:
    from utils import is_jj_repo


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({}))
        sys.exit(0)

    workspace_paths = payload.get("workspacePaths", [])
    candidate_paths = workspace_paths if workspace_paths else [os.getcwd()]

    jj_workspaces = [path for path in candidate_paths if is_jj_repo(path)]
    if not jj_workspaces:
        print(json.dumps({}))
        sys.exit(0)

    messages = []
    for path in jj_workspaces:
        messages.append({
            "systemMessage": {
                "systemMessage": (
                    f"Notice: Workspace '{path}' is a Jujutsu (jj) repository. "
                    "Do not use git commands in this path. Use `jj` commands instead."
                ),
                "metadata": {
                    "source": "antigravity-jujutsu",
                    "workspace": path,
                },
            }
        })

    print(json.dumps({"injectSteps": messages}))
    sys.exit(0)


if __name__ == "__main__":
    main()
