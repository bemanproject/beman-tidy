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

    Attributes:
        repo_info: Contains information about the repository being checked.
        beman_standard_check_config: Configuration settings for the
            Beman standard checks.
    """
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "CMakeLists.txt")

    """
    parse_raw and parse_tree:
    Core functionality for parsing CMake code.
    
    parsed_raw: 
    - Returns a simplified AST containing Command and Comment nodes.
    - (Command - Generic representation of a single CMake instruction; Comment - CMake comment).
    - Hierarchical structures such as if() or function() blocks are not resolved.
    
    parsed_tree: 
    - Returns a fully constructed AST.
    - Resolves block structures such as function(), if(), include () and more.
    - The block structures return specialized AST nodes (e.g., Function, If, Include, etc.).
    
    See more here: https://roehling.github.io/cmake_parser/api/parser.html
    """
    def _get_cmake_parse_raw(self):
        return cmake_parser.parser.parse_raw(self.read(), skip_comments=True)

    def _get_cmake_parse_tree(self):
        return cmake_parser.parser.parse_tree(self.read(), skip_comments=True)

    def _get_cmake_library_name(self, ast):
        cmake_library_name = None

        for item in ast:
            if item.identifier == "add_library":
                cmake_library_name = item.args[0].value
                break

        return cmake_library_name


# TODO cmake.default


# TODO cmake.use_find_package


# TODO cmake.project_name


# TODO cmake.passive_projects


# TODO cmake.library_name
@register_beman_standard_check("cmake.library_name")
class CMakeLibraryNameCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        ast = self._get_cmake_parse_raw()

        cmake_library_name = self._get_cmake_library_name(ast)

        if cmake_library_name is None:
            log_message = "CMake library target name is not found. "
        elif cmake_library_name != self.library_name:
            log_message = f"CMake library target name: {cmake_library_name} does not match library name: {self.library_name}. "

        if cmake_library_name != self.library_name or cmake_library_name is None:
            log_message += "Please update the CMakeLists.txt file according to the Beman Standard. "
            log_message += "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_name for more information."

            self.log(log_message)

            return False

        return True

    def fix(self):
        self.log(
            "Please update the CMakeLists.txt file so that the CMake library target's name is identical to the library name. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_name for more information."
        )


# TODO cmake.library_alias


# TODO cmake.target_names


# TODO cmake.passive_targets


# TODO cmake.skip_tests


# TODO cmake.skip_examples


# TODO cmake.avoid_passthroughs
