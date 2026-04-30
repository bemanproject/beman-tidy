#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.cpp import CppNamespaceCheck, CppExtensionIdentifiersCheck

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
    for path in invalid_prefix.rglob('*'):
        if path.is_file():
            dest_path = tmp_path / path.relative_to(invalid_prefix)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(path, dest_path)

    repo_info["top_level"] = tmp_path
    check = CppNamespaceCheck(repo_info, beman_standard_check_config)
    
    assert check.check() is False
    
    assert check.fix() is True
    
    assert check.check() is True


def test__cpp_extension_identifiers__is_always_skipped(repo_info, beman_standard_check_config):
    """
    Test that cpp.extension_identifiers is always skipped.
    """
    assert CppExtensionIdentifiersCheck(repo_info, beman_standard_check_config).should_skip()
