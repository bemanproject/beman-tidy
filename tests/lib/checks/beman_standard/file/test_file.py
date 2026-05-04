#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.file import FileCopyrightCheck, FileLicenseIdCheck, FileNamesCheck, FileTestNamesCheck

# Workaround to test for both normal and block comments.
test_data_prefix = Path("tests/lib/checks/beman_standard/file/data")
license_id_prefix = test_data_prefix / "license_id"
valid_prefix = test_data_prefix / "valid"
invalid_prefix = test_data_prefix / "invalid"
valid_block_prefix = test_data_prefix / "valid_block"
invalid_block_prefix = test_data_prefix / "invalid_block"

# --- file.copyright tests ---

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
    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()
    for item in invalid_prefix.iterdir():
        if item.is_file():
            shutil.copy(item, invalid_dir / item.name)

    repo_info["top_level"] = invalid_dir
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is True
    assert check.check() is True

    for item in invalid_prefix.iterdir():
        if not item.is_file():
            continue

        fixed_file = invalid_dir / item.name
        content = fixed_file.read_text()
        lines = content.splitlines()

        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            if line.strip().startswith("//"):
                 assert "Copyright" not in line, f"Copyright still present in {fixed_file.name}: {line}"

    # Test with invalid_block_prefix
    invalid_block_dir = tmp_path / "invalid_block"
    invalid_block_dir.mkdir()
    for item in invalid_block_prefix.iterdir():
        if item.is_file():
            shutil.copy(item, invalid_block_dir / item.name)

    repo_info["top_level"] = invalid_block_dir
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is True
    assert check.check() is True

    for item in invalid_block_prefix.iterdir():
        if not item.is_file():
            continue

        fixed_file = invalid_block_dir / item.name
        content = fixed_file.read_text()
        lines = content.splitlines()

        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            # Check both single-line block comments and multi-line block comments
            stripped = line.strip()
            if stripped.startswith("/*") or stripped.startswith("*"):
                assert "Copyright" not in line, f"Copyright still present in {fixed_file.name}: {line}"

# --- file.license_id tests ---

def test__file_license_id__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = license_id_prefix / "valid"
    check = FileLicenseIdCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


def test__file_license_id__invalid(repo_info, beman_standard_check_config):
    # Missing SPDX entirely
    repo_info["top_level"] = license_id_prefix / "invalid_missing"
    check = FileLicenseIdCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

    # SPDX present but not at the first possible line
    repo_info["top_level"] = license_id_prefix / "invalid_wrong_line"
    check = FileLicenseIdCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


def test__file_license_id__fix_inplace(repo_info, beman_standard_check_config, tmp_path):
    # Fix: SPDX at wrong line → move to first line
    src = license_id_prefix / "invalid_wrong_line"
    dst = tmp_path / "invalid_wrong_line"
    shutil.copytree(src, dst)

    repo_info["top_level"] = dst
    check = FileLicenseIdCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is True
    assert check.check() is True

    for f in dst.iterdir():
        if not f.is_file():
            continue
        lines = f.read_text().splitlines()
        if lines and lines[0].startswith("#!"):
            assert "SPDX-License-Identifier:" in lines[1], f"SPDX not at line 2 in {f.name}"
        else:
            assert "SPDX-License-Identifier:" in lines[0], f"SPDX not at line 1 in {f.name}"

    # Fix: SPDX missing → cannot auto-fix
    src = license_id_prefix / "invalid_missing"
    dst = tmp_path / "invalid_missing"
    shutil.copytree(src, dst)

    repo_info["top_level"] = dst
    check = FileLicenseIdCheck(repo_info, beman_standard_check_config)

    assert check.check() is False
    assert check.fix() is False
  
# --- file.names tests ---

file_names_prefix = Path("tests/lib/checks/beman_standard/file/data/names")


def test__file_names__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = file_names_prefix / "valid"
    check = FileNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


def test__file_names__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = file_names_prefix / "invalid"
    check = FileNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


@pytest.mark.skip(reason="not implemented")
def test__file_names__fix_inplace(repo_info, beman_standard_check_config):
    pass

# --- file.test_names tests ---

test_names_prefix = Path("tests/lib/checks/beman_standard/file/data/test_names")


def test__file_test_names__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_names_prefix / "valid"
    check = FileTestNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


def test__file_test_names__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_names_prefix / "invalid"
    check = FileTestNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is False
    
@pytest.mark.skip(reason="not implemented")
def test__file_test_names__fix_inplace(repo_info, beman_standard_check_config):
    pass
