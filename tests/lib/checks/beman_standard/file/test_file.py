#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.file import FileCopyrightCheck

# workaround to test for both normal and block comments
test_data_prefix = Path("tests/lib/checks/beman_standard/file/data")
valid_prefix = test_data_prefix / "valid"
invalid_prefix = test_data_prefix / "invalid"
valid_block_prefix = test_data_prefix / "valid_block"
invalid_block_prefix = test_data_prefix / "invalid_block"

def test__file_copyright__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = valid_prefix
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is True

    repo_info["top_level"] = valid_block_prefix
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is True

def test__file_copyright__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = invalid_prefix
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

    repo_info["top_level"] = invalid_block_prefix
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

def test__file_copyright__fix_inplace(repo_info, beman_standard_check_config, tmp_path):
    # Test with invalid_prefix
    dir1 = tmp_path / "invalid"
    dir1.mkdir()
    for item in invalid_prefix.iterdir():
        if item.is_file():
            shutil.copy(item, dir1 / item.name)

    repo_info["top_level"] = dir1
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is True
    assert check.check() is True

    for item in invalid_prefix.iterdir():
        if not item.is_file():
            continue

        fixed_file = dir1 / item.name
        content = fixed_file.read_text()
        lines = content.splitlines()

        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            if line.strip().startswith("//"):
                 assert "Copyright" not in line, f"Copyright still present in {fixed_file.name}: {line}"

    # Test with invalid_block_prefix
    dir2 = tmp_path / "invalid_block"
    dir2.mkdir()
    for item in invalid_block_prefix.iterdir():
        if item.is_file():
            shutil.copy(item, dir2 / item.name)

    repo_info["top_level"] = dir2
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is True
    assert check.check() is True

    for item in invalid_block_prefix.iterdir():
        if not item.is_file():
            continue

        fixed_file = dir2 / item.name
        content = fixed_file.read_text()
        lines = content.splitlines()

        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            # Check both single-line block comments and multi-line block comments
            stripped = line.strip()
            if stripped.startswith("/*") or stripped.startswith("*"):
                assert "Copyright" not in line, f"Copyright still present in {fixed_file.name}: {line}"
