#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
from pathlib import Path

from tests.utils.path_runners import (
    run_check_for_each_path,
)

# Actual tested checks.
from beman_tidy.lib.checks.beman_standard.cmake import (
    CMakeLibraryNameCheck
)

test_data_prefix = "tests/lib/checks/beman_standard/cmake/data"
valid_prefix = f"{test_data_prefix}/valid"
invalid_prefix = f"{test_data_prefix}/invalid"


def test__cmake_library_name__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.library_name check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/valid-CMakeLists-v1")
	]

    run_check_for_each_path(
        True,
        valid_cmake_paths,
        CMakeLibraryNameCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__cmake_library_name__invalid(repo_info, beman_standard_check_config):
    """
    Test that an invalid CMakeLists.txt file fails the cmake.library_name check.
    """
    invalid_cmake_paths = [
        # CMakeLists.txt missing library name
        Path(f"{invalid_prefix}/invalid-CMakeLists-v1"),
        # CMakeLists.txt with invalid library name
		Path(f"{invalid_prefix}/invalid-CMakeLists-v2")
    ]

    run_check_for_each_path(
        False,
        invalid_cmake_paths,
        CMakeLibraryNameCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="not implemented")
def test__cmake_library_name__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid CMakeLists.txt file.
    Note: Skipping this test as it is not implemented.
    """
    pass
