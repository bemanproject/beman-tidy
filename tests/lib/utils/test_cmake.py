#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import cmake_parser

from beman_tidy.lib.utils.cmake import (
    cmake_build_skip_subdir_option_pattern,
    cmake_has_unguarded_subdirectory,
    cmake_is_subdirectory,
)


def _parse_tree(cmake_source):
    return list(cmake_parser.parser.parse_tree(cmake_source, skip_comments=True))


def _command(identifier, arg):
    tree = _parse_tree(f"{identifier}({arg})")
    return tree[0]


def test__cmake_is_subdirectory__matches_exact_and_nested():
    assert cmake_is_subdirectory(_command("add_subdirectory", "tests"), "tests")
    assert cmake_is_subdirectory(_command("add_subdirectory", "tests/beman/foo"), "tests")
    assert cmake_is_subdirectory(_command("add_subdirectory", '"examples"'), "examples")


def test__cmake_is_subdirectory__rejects_other_commands_and_paths():
    assert not cmake_is_subdirectory(_command("add_subdirectory", "examples"), "tests")
    assert not cmake_is_subdirectory(_command("include", "tests"), "tests")
    assert not cmake_is_subdirectory(_command("add_subdirectory", ""), "tests")


def test__cmake_has_unguarded_subdirectory__detects_unguarded_add_subdirectory():
    tree = _parse_tree(
        """
        if(BEMAN_EXEMPLAR_BUILD_TESTS)
            add_subdirectory(tests/beman/exemplar)
        endif()
        add_subdirectory(tests/beman/exemplar)
        """
    )
    assert cmake_has_unguarded_subdirectory(tree, "tests", "BEMAN_EXEMPLAR_BUILD_TESTS")


def test__cmake_has_unguarded_subdirectory__accepts_fully_guarded_subdirectory():
    tree = _parse_tree(
        """
        if(BEMAN_EXEMPLAR_BUILD_TESTS)
            add_subdirectory(tests/beman/exemplar)
        endif()
        """
    )
    assert not cmake_has_unguarded_subdirectory(tree, "tests", "BEMAN_EXEMPLAR_BUILD_TESTS")


def test__cmake_has_unguarded_subdirectory__detects_missing_guard():
    tree = _parse_tree("add_subdirectory(examples)")
    assert cmake_has_unguarded_subdirectory(tree, "examples", "BEMAN_EXEMPLAR_BUILD_EXAMPLES")


def test__cmake_build_skip_subdir_option_pattern__matches_project_is_top_level_default():
    pattern = cmake_build_skip_subdir_option_pattern("BEMAN_EXEMPLAR_BUILD_TESTS")
    cmake = """
    option(
        BEMAN_EXEMPLAR_BUILD_TESTS
        "Enable building tests and test infrastructure. Default: ${PROJECT_IS_TOP_LEVEL}. Values: { ON, OFF }."
        ${PROJECT_IS_TOP_LEVEL}
    )
    """
    assert pattern.search(cmake)


def test__cmake_build_skip_subdir_option_pattern__rejects_wrong_default():
    pattern = cmake_build_skip_subdir_option_pattern("BEMAN_EXEMPLAR_BUILD_TESTS")
    cmake = """
    option(
        BEMAN_EXEMPLAR_BUILD_TESTS
        "Enable building tests and test infrastructure. Default: ON. Values: { ON, OFF }."
        ON
    )
    """
    assert not pattern.search(cmake)
