from pathlib import Path


def is_jj_repo(start_dir: str | Path) -> bool:
    """Search up the directory tree looking for a .jj directory."""
    current = Path(start_dir).resolve()

    # Check the current directory and all its parent directories
    for directory in [current, *current.parents]:
        if (directory / ".jj").is_dir():
            return True

    return False
