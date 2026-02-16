#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.cpp import CppNamespaceCheck

test_data_prefix = Path("tests/lib/checks/beman_standard/cpp/namespace")
valid_prefix = test_data_prefix / "valid"
invalid_prefix = test_data_prefix / "invalid"

def test__cpp_namespace__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = valid_prefix
    
    check = CppNamespaceCheck(repo_info, beman_standard_check_config)
    assert check.check() is True

def test__cpp_namespace__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = invalid_prefix
    
    check = CppNamespaceCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

def test__cpp_namespace__fix_inplace(repo_info, beman_standard_check_config, tmp_path):
    shutil.copytree(invalid_prefix, tmp_path, dirs_exist_on_copy=True)

    repo_info["top_level"] = tmp_path
    check = CppNamespaceCheck(repo_info, beman_standard_check_config)
    
    assert check.check() is False
    
    assert check.fix() is True
    
    assert check.check() is True
