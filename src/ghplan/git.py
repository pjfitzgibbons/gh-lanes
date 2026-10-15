"""Every subprocess call to git, in one place (design 0001 *Layout*, architecture invariant 6)."""

import subprocess
from pathlib import Path


class GitError(Exception):
    """git failed. The message carries what git wrote to stderr."""


def _git(*args: str, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
        )
    except FileNotFoundError as e:
        raise GitError("git is not installed or not on PATH") from e
    except subprocess.CalledProcessError as e:
        raise GitError(f"git {' '.join(args)}: {e.stderr.strip()}") from e
    return result.stdout


def current_branch(cwd: Path | None = None) -> str | None:
    """The checked-out branch's name, or None on a detached HEAD."""
    return _git("branch", "--show-current", cwd=cwd).strip() or None
