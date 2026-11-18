#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.cpp import (
    CppNamespaceCheck,
    CppExtensionIdentifiersCheck,
    CppMinStdVersionCheck,
    CppNoFlagForkingCheck,
)

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


no_flag_forking_prefix = Path("tests/lib/checks/beman_standard/cpp/no_flag_forking")
no_flag_forking_valid_prefix = no_flag_forking_prefix / "valid"
no_flag_forking_invalid_prefix = no_flag_forking_prefix / "invalid"


def test__cpp_no_flag_forking__valid(repo_info, beman_standard_check_config):
    """
    Test that headers using config.hpp macros pass, that __cpp_* in comments, strings, tests/
    and in the library's own include/beman/<library>/config.hpp fallback is not flagged.
    """
    repo_info["top_level"] = no_flag_forking_valid_prefix

    check = CppNoFlagForkingCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


@pytest.mark.parametrize(
    "case",
    [
        "defined",  # #if defined(__cpp_...) / #elif defined(__cpp_...)
        "elif_bare",  # #elif __cpp_...
        "ifdef",  # #ifdef __cpp_...
        "ifndef",  # #ifndef __cpp_...
        "compound",  # #if __cplusplus >= ... && __cpp_... // comment
        "continuation",  # __cpp_... on a continuation line
        "indented",  # indented directive with space after '#'
        "detail_config",  # nested config.hpp is not exempt
        "example",  # examples/ are not exempt
    ],
)
def test__cpp_no_flag_forking__invalid(repo_info, beman_standard_check_config, case):
    """
    Test that each way of using a __cpp_* feature test macro in a preprocessor conditional fails.
    """
    repo_info["top_level"] = no_flag_forking_invalid_prefix / case

    check = CppNoFlagForkingCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


@pytest.mark.skip(reason="not implemented")
def test__cpp_no_flag_forking__fix_inplace(repo_info, beman_standard_check_config):
    pass


def test__cpp_extension_identifiers__is_always_skipped(repo_info, beman_standard_check_config):
    """
    Test that cpp.extension_identifiers is always skipped.
    """
    assert CppExtensionIdentifiersCheck(repo_info, beman_standard_check_config).should_skip()


min_std_version_prefix = Path("tests/lib/checks/beman_standard/cpp/min_std_version")
min_std_version_valid_prefix = min_std_version_prefix / "valid"
min_std_version_invalid_prefix = min_std_version_prefix / "invalid"


def test__cpp_min_std_version__valid(repo_info, beman_standard_check_config):
    for repo_path in (
        min_std_version_valid_prefix / "repo-v1",
        min_std_version_valid_prefix / "repo-cpp29",
    ):
        repo_info["top_level"] = repo_path
        check = CppMinStdVersionCheck(repo_info, beman_standard_check_config)
        assert check.check() is True


def test__cpp_min_std_version__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = min_std_version_invalid_prefix / "repo-v1"

    check = CppMinStdVersionCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


@pytest.mark.skip(reason="not implemented")
def test__cpp_min_std_version__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid README.md minimum C++ standard.
    Note: Skipping this test as it is not implemented.
    """
    pass
