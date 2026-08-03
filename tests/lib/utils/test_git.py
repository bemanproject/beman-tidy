#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

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
