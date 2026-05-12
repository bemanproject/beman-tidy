#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import cmake_parser

from ..system.registry import register_beman_standard_check
from ..base.file_base_check import FileBaseCheck

# [cmake.*] checks category.
# All checks in this file extend the CMakeBaseCheck class.
#
# Note: CMakeBaseCheck is not a registered check!


class CMakeBaseCheck(FileBaseCheck):
    """
    Represents a base class for checks related to CMake files.

    CMakeBaseCheck is designed to validate and analyze CMakeLists.txt
    files in the context of a repository. It provides functionality
    to parse CMake files and extract specific data.

    Methods:
    -------
    - parse_raw and parse_tree (Core functionality for parsing CMake code):
    parse_raw:
        - Returns a simplified AST containing Command and Comment nodes
        - (Command - Generic representation of a single CMake instruction; Comment - CMake comment)
        - Hierarchical structures such as if() or function() blocks are not resolved

    parse_tree:
        - Returns a fully constructed AST.
        - Resolves block structures such as function(), if(), include() and more.
        - The block structures return specialized AST nodes (e.g., Function, If, Include, etc.).

    See more here: https://roehling.github.io/cmake_parser/api/parser.html

    Attributes:
        repo_info: Contains information about the repository being checked.
        beman_standard_check_config: Configuration settings for the Beman standard checks.
    """
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "CMakeLists.txt")

    def get_cmake_parse_raw(self, skip_comments=True):
        return cmake_parser.parser.parse_raw(self.read(), skip_comments=skip_comments)

    def get_cmake_parse_tree(self, skip_comments=True):
        return cmake_parser.parser.parse_tree(self.read(), skip_comments=skip_comments)

    def get_cmake_library_name(self, ast):
        cmake_library_name = None

        for item in ast:
            if item.identifier == "add_library":
                if item.args:
                    cmake_library_name = item.args[0].value
                    break

        return cmake_library_name

    def get_cmake_project_name(self, ast):
        cmake_project_name = None

        for item in ast:
            if item.identifier == "project":
                if item.args:
                    cmake_project_name = item.args[0].value
                    break

        return cmake_project_name


# TODO cmake.default


# TODO cmake.use_find_package


@register_beman_standard_check("cmake.project_name")
class CMakeProjectNameCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        ast = self.get_cmake_parse_raw()
        cmake_project_name = self.get_cmake_project_name(ast)

        if cmake_project_name is None:
            self.log("CMake project name not found. "
                     f"Expected project name: '{self.library_name}'"
                     "Please update the CMakeLists.txt file according to the Beman Standard. "
                     "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakeproject_name for more information.")
            return False

        if cmake_project_name != self.library_name:
            self.log(f"Invalid CMake project name - got: '{cmake_project_name}', expected: '{self.library_name}'. "
                     "Please update the CMakeLists.txt file according to the Beman Standard. "
                     "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakeproject_name for more information.")
            return False

        return True

    def fix(self):
        self.log(
            "Please update the CMakeLists.txt file so that the CMake project name is identical to the Beman project name. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakeproject_name for more information."
        )
        return False


# TODO cmake.passive_projects


@register_beman_standard_check("cmake.library_name")
class CMakeLibraryNameCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        ast = self.get_cmake_parse_raw()
        cmake_library_name = self.get_cmake_library_name(ast)
        cmake_library_name2 = self.get_cmake_library_name(ast)

        self.log(f"{cmake_library_name} -> {cmake_library_name2}")

        if cmake_library_name is None:
            self.log("CMake library target name not found. "
                     f"Expected library target name: '{self.library_name}'"
                     "Please update the CMakeLists.txt file according to the Beman Standard. "
                     "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_name for more information.")
            return False

        if cmake_library_name != self.library_name:
            self.log(f"Invalid CMake library target name - got: '{cmake_library_name}', expected: '{self.library_name}'. "
                     "Please update the CMakeLists.txt file according to the Beman Standard. "
                     "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_name for more information.")
            return False

        return True

    def fix(self):
        self.log(
            "Please update the CMakeLists.txt file so that the CMake library target's name is identical to the Beman library name. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_name for more information."
        )
        return False


# TODO cmake.library_alias


# TODO cmake.target_names


# TODO cmake.passive_targets


# TODO cmake.skip_tests


# TODO cmake.skip_examples


# TODO cmake.avoid_passthroughs
