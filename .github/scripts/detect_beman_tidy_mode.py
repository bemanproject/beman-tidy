#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Detect how beman-tidy should run for a Beman library repository."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_BEMAN_TIDY_HOOK_RE = re.compile(r"id:\s*beman-tidy\b")
_REQUIRE_ALL_RE = re.compile(r"--require-all\b")


def has_beman_tidy_hook(content: str) -> bool:
    return _BEMAN_TIDY_HOOK_RE.search(content) is not None


def uses_require_all(content: str) -> bool:
    return has_beman_tidy_hook(content) and _REQUIRE_ALL_RE.search(content) is not None


def detect_mode(repo_path: Path) -> str:
    """
    Return the beman-tidy invocation mode for a library repo.

    - ``require-all``: pre-commit configures the beman-tidy hook with ``--require-all``.
    - ``default``: no beman-tidy hook, or hook without ``--require-all``.
    """
    precommit = repo_path / ".pre-commit-config.yaml"
    if not precommit.is_file():
        return "default"

    content = precommit.read_text(encoding="utf-8", errors="ignore")
    if not has_beman_tidy_hook(content):
        return "default"
    if uses_require_all(content):
        return "require-all"
    return "default"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", type=Path, help="Path to cloned library repository")
    args = parser.parse_args()
    print(detect_mode(args.repo_path))


if __name__ == "__main__":
    main()
