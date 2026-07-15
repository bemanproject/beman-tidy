#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".github" / "scripts"))

from create_library_beman_tidy_issue import (  # noqa: E402
    build_body,
    parse_codeowners,
)


def test__parse_codeowners__extracts_users(tmp_path: Path):
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "CODEOWNERS").write_text(
        "# comment\n* @alice @bemanproject/team @bob\n"
    )
    assert parse_codeowners(tmp_path) == ["alice", "bob"]


def test__parse_codeowners__missing_file(tmp_path: Path):
    assert parse_codeowners(tmp_path) == []


def test__build_body__mentions_assignees():
    body = build_body(
        repo="optional",
        mode="require-all",
        tidy_version="beman-tidy 0.5.2",
        run_url="https://example.com/run/1",
        tidy_log="check failed",
        assignees=["steve-downey", "neatudarius"],
    )
    assert "require-all" in body
    assert "@steve-downey" in body
    assert "@neatudarius" in body
    assert "previously passed beman-tidy checks" in body
