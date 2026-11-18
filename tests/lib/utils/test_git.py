#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shutil
from pathlib import Path

import pytest

from git import Actor, Repo

from beman_tidy.lib.utils.git import get_repo_info


def create_repository(path: Path) -> Repo:
    repo = Repo.init(path, initial_branch="main")
    (path / "README.md").write_text("# Test repository\n")
    repo.index.add(["README.md"])

    actor = Actor("Test Author", "test@example.com")
    repo.index.commit("Initial commit", author=actor, committer=actor)
    return repo


def test_get_repo_info_reports_current_branch(tmp_path):
    create_repository(tmp_path)

    assert get_repo_info(tmp_path)["current_branch"] == "main"


def test_get_repo_info_accepts_detached_head(tmp_path):
    repo = create_repository(tmp_path)
    repo.git.checkout("--detach", "HEAD")

    assert get_repo_info(tmp_path)["current_branch"] is None


def create_bare_clone_with_worktrees(tmp_path: Path, worktree_names: list[str]) -> Path:
    """
    Recreate the layout from issue #186: a bare clone without
    refs/remotes/origin/HEAD and worktrees added next to it.
    """
    source = create_repository(tmp_path / "source")
    for name in worktree_names[1:]:
        source.git.branch(name)

    bare_path = tmp_path / "exemplar.git"
    bare = Repo.clone_from(source.working_dir, bare_path, bare=True)
    for name in worktree_names:
        bare.git.worktree("add", str(tmp_path / name), name)
    return bare_path


def test_get_repo_info_accepts_worktree_of_bare_clone(tmp_path):
    create_bare_clone_with_worktrees(tmp_path, ["main"])

    repo_info = get_repo_info(tmp_path / "main")

    assert repo_info["top_level"].resolve() == (tmp_path / "main").resolve()
    assert repo_info["current_branch"] == "main"
    assert repo_info["default_branch"] == "main"


def test_get_repo_info_resolves_bare_repository_to_its_only_worktree(tmp_path):
    bare_path = create_bare_clone_with_worktrees(tmp_path, ["main"])

    repo_info = get_repo_info(bare_path)

    assert repo_info["top_level"].resolve() == (tmp_path / "main").resolve()
    assert repo_info["current_branch"] == "main"


def test_get_repo_info_resolves_bare_repository_with_non_ascii_worktree_path(tmp_path):
    bare_path = create_bare_clone_with_worktrees(tmp_path, ["main", "café"])
    bare = Repo(bare_path)
    bare.git.worktree("remove", str(tmp_path / "main"))

    repo_info = get_repo_info(bare_path)

    assert repo_info["top_level"].resolve() == (tmp_path / "café").resolve()


def test_get_repo_info_ignores_missing_locked_worktree(tmp_path):
    bare_path = create_bare_clone_with_worktrees(tmp_path, ["main", "feature"])
    bare = Repo(bare_path)
    missing_worktree = tmp_path / "feature"
    bare.git.worktree("lock", str(missing_worktree))
    shutil.rmtree(missing_worktree)

    repo_info = get_repo_info(bare_path)

    assert repo_info["top_level"].resolve() == (tmp_path / "main").resolve()


@pytest.mark.parametrize("worktree_names", [[], ["main", "feature"]])
def test_get_repo_info_rejects_ambiguous_bare_repository(
    tmp_path, caplog, worktree_names
):
    bare_path = create_bare_clone_with_worktrees(tmp_path, worktree_names)

    with pytest.raises(SystemExit) as exit_info:
        get_repo_info(bare_path)

    assert exit_info.value.code == 1
    assert "is a bare repository" in caplog.text
    for name in worktree_names:
        assert str((tmp_path / name).resolve()) in caplog.text
