"""git.py: the one module that runs git. These tests run the real git in a throwaway repo."""

import subprocess
from pathlib import Path

import pytest

from ghplan import git
from ghplan.git import GitError, current_branch


def _repo(path: Path, branch: str) -> Path:
    def run(*args: str) -> None:
        subprocess.run(["git", *args], cwd=path, check=True, capture_output=True)

    run("init", "-q", "-b", branch)
    run("-c", "user.name=Example", "-c", "user.email=dev@example.com", "commit", "-q", "--allow-empty", "-m", "x")
    return path


def test_current_branch(tmp_path: Path):
    assert current_branch(_repo(tmp_path, "feat/pl-tunep-draw-a-word")) == "feat/pl-tunep-draw-a-word"


def test_a_detached_head_has_no_branch(tmp_path: Path):
    repo = _repo(tmp_path, "main")
    subprocess.run(["git", "checkout", "-q", "--detach"], cwd=repo, check=True)
    assert current_branch(repo) is None


def test_outside_a_repo_is_a_git_error(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    with pytest.raises(GitError, match="git branch --show-current"):
        current_branch(tmp_path)


def test_no_git_on_path_is_a_git_error(monkeypatch):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(GitError, match="not installed"):
        git.current_branch()
