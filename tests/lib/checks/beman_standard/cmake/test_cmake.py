#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
from pathlib import Path

from tests.utils.path_runners import (
    run_check_for_each_path,
)

# Actual tested checks.
from beman_tidy.lib.checks.beman_standard.cmake import (
    CMakeProjectNameCheck,
    CMakeLibraryNameCheck,
    CMakeLibraryAliasCheck,
    CMakeTargetNamesCheck,
    CMakeDefaultCheck,
)

test_data_prefix = "tests/lib/checks/beman_standard/cmake/data"
valid_prefix = f"{test_data_prefix}/valid"
invalid_prefix = f"{test_data_prefix}/invalid"


def test__cmake_project_name__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.project_name check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/CMakeLists-v1.txt"),
    ]

    run_check_for_each_path(
        True,
        valid_cmake_paths,
        CMakeProjectNameCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__cmake_project_name__invalid(repo_info, beman_standard_check_config):
    """
    Test that an invalid CMakeLists.txt file fails the cmake.project_name check.
    """
    invalid_cmake_paths = [
        # CMakeLists.txt missing project name
        Path(f"{invalid_prefix}/invalid-project_name-v1.txt"),
        # CMakeLists.txt with invalid project name
        Path(f"{invalid_prefix}/invalid-project_name-v2.txt"),
        # CMakeLists.txt with another invalid project name
        Path(f"{invalid_prefix}/invalid-project_name-v3.txt"),
    ]

    run_check_for_each_path(
        False,
        invalid_cmake_paths,
        CMakeProjectNameCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="not implemented")
def test__cmake_project_name__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid CMakeLists.txt file.
    Note: Skipping this test as it is not implemented.
    """
    pass


def test__cmake_library_name__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.library_name check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/CMakeLists-v1.txt"),
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
        # CMakeLists.txt missing library target name
        Path(f"{invalid_prefix}/invalid-library_name-v1.txt"),
        # CMakeLists.txt with invalid library target name
        Path(f"{invalid_prefix}/invalid-library_name-v2.txt"),
        # CMakeLists.txt with another invalid library target name
        Path(f"{invalid_prefix}/invalid-library_name-v3.txt"),
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


def test__cmake_library_alias__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.library_alias check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/CMakeLists-v1.txt"),
    ]

    run_check_for_each_path(
        True,
        valid_cmake_paths,
        CMakeLibraryAliasCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__cmake_library_alias__invalid(repo_info, beman_standard_check_config):
    """
    Test that an invalid CMakeLists.txt file fails the cmake.library_alias check.
    """
    invalid_cmake_paths = [
        # CMakeLists.txt missing library alias
        Path(f"{invalid_prefix}/invalid-library_alias-v1.txt"),
        # CMakeLists.txt with invalid library alias
        Path(f"{invalid_prefix}/invalid-library_alias-v2.txt"),
        # CMakeLists.txt with another invalid library alias
        Path(f"{invalid_prefix}/invalid-library_alias-v3.txt"),
    ]

    run_check_for_each_path(
        False,
        invalid_cmake_paths,
        CMakeLibraryAliasCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="not implemented")
def test__cmake_library_alias__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid CMakeLists.txt file.
    Note: Skipping this test as it is not implemented.
    """
    pass


def test__cmake_target_names__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.target_names check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/CMakeLists-v1.txt"),
    ]

    run_check_for_each_path(
        True,
        valid_cmake_paths,
        CMakeTargetNamesCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__cmake_target_names__invalid(repo_info, beman_standard_check_config):
    """
    Test that an invalid CMakeLists.txt file fails the cmake.target_names check.
    """
    invalid_cmake_paths = [
        # CMakeLists.txt with invalid 'add_library' target name
        Path(f"{invalid_prefix}/invalid-target_names-v1.txt"),
        # CMakeLists.txt with invalid 'add_executable' target name
        Path(f"{invalid_prefix}/invalid-target_names-v2.txt"),
        # CMakeLists.txt with multiple invalid target names
        Path(f"{invalid_prefix}/invalid-target_names-v3.txt"),
    ]

    run_check_for_each_path(
        False,
        invalid_cmake_paths,
        CMakeTargetNamesCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="not implemented")
def test__cmake_target_names__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid CMakeLists.txt file.
    Note: Skipping this test as it is not implemented.
    """
    pass


def test__cmake_default__valid(repo_info, beman_standard_check_config):
    """
    Test that a valid CMakeLists.txt file passes the cmake.default check.
    """
    valid_cmake_paths = [
        # CMakeLists.txt from beman.exemplar
        Path(f"{valid_prefix}/valid-default-v1.txt"),
    ]

    run_check_for_each_path(
        True,
        valid_cmake_paths,
        CMakeDefaultCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__cmake_default__invalid(repo_info, beman_standard_check_config):
    """
    Test that an invalid CMakeLists.txt file fails the cmake.default check.
    """
    invalid_cmake_paths = [
        # CMakeLists.txt with library behind OFF option
        Path(f"{invalid_prefix}/invalid-default-v1.txt"),
        # CMakeLists.txt with library only inside if()
        Path(f"{invalid_prefix}/invalid-default-v2.txt"),
    ]

    run_check_for_each_path(
        False,
        invalid_cmake_paths,
        CMakeDefaultCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="not implemented")
def test__cmake_default__fix_inplace(repo_info, beman_standard_check_config):
    """
    Test that the fix method corrects an invalid CMakeLists.txt file.
    Note: Skipping this test as it is not implemented.
    """
    pass
