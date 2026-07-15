#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".github" / "scripts"))

from detect_beman_tidy_mode import detect_mode, has_beman_tidy_hook, uses_require_all


def test__no_precommit__default_mode(tmp_path: Path):
    assert detect_mode(tmp_path) == "default"


def test__precommit_without_beman_tidy__default_mode(tmp_path: Path):
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n      - id: trailing-whitespace\n"
    )
    assert detect_mode(tmp_path) == "default"


def test__beman_tidy_without_require_all__default_mode(tmp_path: Path):
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/bemanproject/beman-tidy\n"
        "    hooks:\n"
        "      - id: beman-tidy\n"
        "        args: [\".\", \"--verbose\"]\n"
    )
    assert detect_mode(tmp_path) == "default"


def test__beman_tidy_with_require_all__require_all_mode(tmp_path: Path):
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/bemanproject/beman-tidy\n"
        "    hooks:\n"
        "      - id: beman-tidy\n"
        "        args: [\".\", \"--verbose\", \"--require-all\"]\n"
    )
    assert detect_mode(tmp_path) == "require-all"


def test__helpers():
    cfg = "hooks:\n  - id: beman-tidy\n    args: [\"--require-all\"]\n"
    assert has_beman_tidy_hook(cfg) is True
    assert uses_require_all(cfg) is True
    assert uses_require_all("hooks:\n  - id: other\n") is False
