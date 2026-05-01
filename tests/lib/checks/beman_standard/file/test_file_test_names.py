#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
from pathlib import Path
from beman_tidy.lib.checks.beman_standard.file import FileTestNamesCheck

test_data_prefix = Path("tests/lib/checks/beman_standard/file/data/test_names")
valid_prefix = test_data_prefix / "valid"
invalid_prefix = test_data_prefix / "invalid"

def test__file_test_names__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = valid_prefix
    check = FileTestNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is True

def test__file_test_names__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = invalid_prefix
    check = FileTestNamesCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

@pytest.mark.skip(reason="not implemented")
def test__file_test_names__fix_inplace(repo_info, beman_standard_check_config):
    pass
