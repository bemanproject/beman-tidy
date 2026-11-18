#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from abc import ABC
from collections.abc import Iterable
import re
from pathlib import Path

import cmake_parser
from cmake_parser.ast import AstNode, Command, If, Option

from beman_tidy.lib.utils.cmake import (
    cmake_build_skip_subdir_option_pattern,
    cmake_has_unguarded_subdirectory,
)

from ..base.base_check import BaseCheck
from ..system.registry import register_beman_standard_check
from ..base.file_base_check import FileBaseCheck
from ...utils.config import get_ignore_matcher
from ...utils.file import get_cmake_files
from ...utils.string import normalize_path_for_display

# [cmake.*] checks category.
# All checks in this file extend the CMakeBaseCheck class.
#
# Note: CMakeBaseCheck is not a registered check!
class CMakeBaseCheck(FileBaseCheck, ABC):
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

    def get_cmake_parse_raw(self, skip_comments=True) -> Iterable[AstNode]:
        return cmake_parser.parser.parse_raw(self.read(), skip_comments=skip_comments)

    def get_cmake_parse_tree(self, skip_comments=True) -> Iterable[AstNode]:
        return cmake_parser.parser.parse_tree(self.read(), skip_comments=skip_comments)

    @staticmethod
    def get_cmake_library_name(ast):
        cmake_library_name = None

        for item in ast:
            if not isinstance(item, Command):
                continue

            if item.identifier == "add_library":
                if item.args:
                    cmake_library_name = item.args[0].value
                    break

        return cmake_library_name

    @staticmethod
    def get_cmake_project_name(ast):
        cmake_project_name = None

        for item in ast:
            if not isinstance(item, Command):
                continue

            if item.identifier == "project":
                if item.args:
                    cmake_project_name = item.args[0].value
                    break

        return cmake_project_name

    def get_cmake_library_alias(self):
        ast = self.get_cmake_parse_raw()
        cmake_library_alias = None

        for item in ast:
            if item.identifier == "add_library":
                args = [arg.value for arg in item.args]

                # Check that there are 3 args [library_alias, 'ALIAS', library_name]
                if len(args) != 3:
                    continue

                # Check that the 2nd arg is 'ALIAS'
                if args[1].upper() != "ALIAS":
                    continue

                # Ensure the alias's final component matches the library target's final component.
                # E.g., "beman::foo" -> "foo"
                alias_last = args[0].split("::")[-1]
                target_last = args[2].split(".")[-1]
                if alias_last != target_last:
                    continue

                # If the alias matches the expected alias, return it.
                if args[0] == self.library_alias:
                    cmake_library_alias = args[0]
                    break

        return cmake_library_alias

    def get_cmake_target_names(self):
        ast = self.get_cmake_parse_raw()
        cmake_target_names = []

        for item in ast:
            if item.identifier == "add_library" or item.identifier == "add_executable":
                if item.args:
                    cmake_target_names.append(item.args[0].value)

        return cmake_target_names


@register_beman_standard_check("cmake.default")
class CMakeDefaultCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def _is_library_add_library_command(self, command):
        if command.identifier != "add_library":
            return False
        if not command.args:
            return False
        if command.args[0].value != self.library_name:
            return False
        if len(command.args) >= 2 and command.args[1].value.upper() == "ALIAS":
            return False
        return True

    def _has_unconditional_library_target(self, ast_tree):
        for item in ast_tree:
            if isinstance(item, Command) and self._is_library_add_library_command(item):
                return True
        return False

    def _get_option_defaults(self, ast_tree):
        options = {}
        for item in ast_tree:
            if isinstance(item, Option) and item.args:
                args = [arg.value for arg in item.args]
                if args:
                    options[args[0]] = args[2] if len(args) >= 3 else None
        return options

    def _library_if_conditions(self, ast_tree):
        conditions = []
        for item in ast_tree:
            if isinstance(item, If) and item.args:
                condition = item.args[0].value
                for sub in item.if_true or []:
                    if isinstance(sub, Command) and self._is_library_add_library_command(sub):
                        conditions.append(condition)
        return conditions

    def check(self):
        ast_raw = list(self.get_cmake_parse_raw())
        ast_tree = list(self.get_cmake_parse_tree())
        has_library_in_raw = any(
            self._is_library_add_library_command(item)
            for item in ast_raw
            if isinstance(item, Command)
        )

        if not has_library_in_raw:
            self.log("CMake library target is not built by default. "
                     f"Expected unconditional add_library('{self.library_name}') in the root CMakeLists.txt. "
                     "Please update the CMakeLists.txt file according to the Beman Standard. "
                     "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakedefault for more information.")
            return False

        if self._has_unconditional_library_target(ast_tree):
            return True

        option_defaults = self._get_option_defaults(ast_tree)
        if_conditions = self._library_if_conditions(ast_tree)

        for condition in if_conditions:
            if condition in option_defaults and (option_defaults[condition] or "").upper() == "OFF":
                self.log("CMake library target is guarded by an option defaulting to OFF. "
                         f"The library target '{self.library_name}' must be built unconditionally. "
                         "Please update the CMakeLists.txt file according to the Beman Standard. "
                         "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakedefault for more information.")
                return False

        self.log("CMake library target is only built conditionally. "
                 f"Expected unconditional add_library('{self.library_name}') in the root CMakeLists.txt. "
                 "Please update the CMakeLists.txt file according to the Beman Standard. "
                 "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakedefault for more information.")
        return False

    def fix(self):
        self.log(
            "Please update the root CMakeLists.txt so that the main library target is built unconditionally by default. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakedefault for more information."
        )
        return False


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
                     f"Expected project name: '{self.library_name}'. "
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

        if cmake_library_name is None:
            self.log("CMake library target name not found. "
                     f"Expected library target name: '{self.library_name}'. "
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


@register_beman_standard_check("cmake.library_alias")
class CMakeLibraryAliasCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        ast = self.get_cmake_parse_raw()

        expected_library_alias = "beman::" + self.short_name

        for item in ast:
            if not isinstance(item, Command):
                continue

            if item.identifier == "add_library":
                args = [arg.value for arg in item.args]

                # Check that there are 3 args [library_alias, 'ALIAS', library_name]
                if len(args) != 3:
                    continue

                # Check that the 2nd arg is 'ALIAS'
                if args[1] != "ALIAS":
                    continue

                # Check that the 1st argument stripped of the prefix matches the 3rd arg stripped
                if list(filter(None, args[0].split(":"))) != args[2].split("."):
                    continue

                if args[0] == expected_library_alias:
                    return True

        self.log("Missing or invalid CMake library alias target. "
                 f"Expected alias target: '{expected_library_alias}'. "
                 "Please update the CMakeLists.txt file according to the Beman Standard. "
                 "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_alias for more information.")
        return False

    def fix(self):
        self.log(
            "Please update the CMakeLists.txt file so that it creates an alias of the library target named 'beman::<short_name>'. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakelibrary_alias for more information."
        )
        return False


# Note: this check currently parses only the top-level CMakeLists.txt,
# so it will not see targets defined in add_subdirectory() files.
# TODO: extend check to recurse into subdirectories for full coverage
@register_beman_standard_check("cmake.target_names")
class CMakeTargetNamesCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        wrong_prefix = False

        cmake_target_names = self.get_cmake_target_names()

        for target_name in cmake_target_names:
            # skip the library name and library alias targets
            if target_name == self.library_name or target_name == self.library_alias:
                continue

            # all other targets must begin with '<library_name>.'
            if not target_name.startswith(f"{self.library_name}."):
                wrong_prefix = True
                self.log(f"Invalid CMake target name - got: '{target_name}', expected prefix: '{self.library_name}.'")

        if wrong_prefix:
            self.log(
                "Please update the CMakeLists.txt file according to the Beman Standard. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmaketarget_names for more information."
            )

            return False

        return True

    def fix(self):
        self.log(
            "Please update the CMakeLists.txt file so that all targets, aside from the library target, begin with the '<library_name>.' prefix. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmaketarget_names for more information."
        )
        return False


@register_beman_standard_check("cmake.passive_targets")
class CMakePassiveTargetsCheck(BaseCheck):
    """
    [cmake.passive_targets]
    Requirement: External targets must not modify compilation flags of dependents.
    """

    _TARGET_COMPILE_FEATURES_RE = re.compile(r"target_compile_features\s*\(")
    _TARGET_COMPILE_DEFINITIONS_RE = re.compile(
        r"target_compile_definitions\s*\([^)]*\b(PUBLIC|INTERFACE)\b"
    )
    _COMMENT_RE = re.compile(r"#[^\n]*")

    def _read_cmake_files(self):
        path_override = getattr(self, "path", None)
        if path_override is not None:
            path = Path(path_override)
            if not path.is_absolute():
                path = self.repo_path / path
            if not path.is_file():
                self.log(f"CMake file '{path}' does not exist or is not a file.")
                return None
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                self.log(f"Unable to read CMake file '{path}': {exc}")
                return None
            rel_path = path
            try:
                rel_path = path.relative_to(self.repo_path)
            except ValueError:
                pass
            return {rel_path: self._COMMENT_RE.sub("", content)}

        ignores = get_ignore_matcher(self.repo_info)
        result = {}
        for rel_path in get_cmake_files(self.repo_path, ignores=ignores):
            abs_path = self.repo_path / rel_path
            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
                result[rel_path] = self._COMMENT_RE.sub("", content)
            except OSError as exc:
                self.log(f"Unable to read CMake file '{rel_path}': {exc}")
                return None
        return result

    def check(self):
        cmake_files = self._read_cmake_files()
        if cmake_files is None:
            return False
        all_passed = True

        for rel_path, content in cmake_files.items():
            display_path = normalize_path_for_display(
                self.repo_path / rel_path, self.repo_path
            )

            if self._TARGET_COMPILE_FEATURES_RE.search(content):
                self.log(
                    f"{display_path}: target_compile_features must not be used because it "
                    "modifies the compilation environment of dependent targets. "
                    "Please update the CMake file according to the Beman Standard. "
                    "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakepassive_targets "
                    "for more information."
                )
                all_passed = False

            if self._TARGET_COMPILE_DEFINITIONS_RE.search(content):
                self.log(
                    f"{display_path}: target_compile_definitions with PUBLIC or INTERFACE "
                    "visibility must not be used because definitions are propagated to "
                    "dependent targets. "
                    "Please update the CMake file according to the Beman Standard. "
                    "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakepassive_targets "
                    "for more information."
                )
                all_passed = False

        return all_passed

    def fix(self):
        self.log(
            "Please remove target_compile_features and target_compile_definitions with "
            "PUBLIC or INTERFACE visibility from CMake files. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakepassive_targets "
            "for more information."
        )
        return False


@register_beman_standard_check("cmake.skip_tests")
class CMakeSkipTestsCheck(CMakeBaseCheck):
    _SUBDIR_NAME = "tests"
    _STANDARD_ANCHOR = "cmakeskip_tests"

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def _build_option_name(self):
        return f"BEMAN_{self.short_name.upper()}_BUILD_TESTS"

    def check(self):
        content = self.read()
        option_name = self._build_option_name()

        if not cmake_build_skip_subdir_option_pattern(option_name).search(content):
            self.log(
                f"Missing or invalid CMake option '{option_name}' with default "
                f"'${{PROJECT_IS_TOP_LEVEL}}'. "
                "Please update the CMakeLists.txt file according to the Beman Standard. "
                f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
            )
            return False

        ast_tree = list(self.get_cmake_parse_tree())
        if cmake_has_unguarded_subdirectory(ast_tree, self._SUBDIR_NAME, option_name):
            self.log(
                f"Tests are not guarded by 'if({option_name})' before "
                "'add_subdirectory(tests...)'. "
                "Please update the CMakeLists.txt file according to the Beman Standard. "
                f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
            )
            return False

        return True

    def fix(self):
        option_name = self._build_option_name()
        self.log(
            "Please update the CMakeLists.txt file so that tests are controlled by "
            f"'option({option_name} ... ${{PROJECT_IS_TOP_LEVEL}})' "
            f"and guarded by 'if({option_name})' before "
            "'add_subdirectory(tests...)'. "
            f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
        )
        return False


@register_beman_standard_check("cmake.skip_examples")
class CMakeSkipExamplesCheck(CMakeBaseCheck):
    _SUBDIR_NAME = "examples"
    _STANDARD_ANCHOR = "cmakeskip_examples"

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def _build_option_name(self):
        return f"BEMAN_{self.short_name.upper()}_BUILD_EXAMPLES"

    def check(self):
        content = self.read()
        option_name = self._build_option_name()

        if not cmake_build_skip_subdir_option_pattern(option_name).search(content):
            self.log(
                f"Missing or invalid CMake option '{option_name}' with default "
                f"'${{PROJECT_IS_TOP_LEVEL}}'. "
                "Please update the CMakeLists.txt file according to the Beman Standard. "
                f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
            )
            return False

        ast_tree = list(self.get_cmake_parse_tree())
        if cmake_has_unguarded_subdirectory(ast_tree, self._SUBDIR_NAME, option_name):
            self.log(
                f"Examples are not guarded by 'if({option_name})' before "
                "'add_subdirectory(examples...)'. "
                "Please update the CMakeLists.txt file according to the Beman Standard. "
                f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
            )
            return False

        return True

    def fix(self):
        option_name = self._build_option_name()
        self.log(
            "Please update the CMakeLists.txt file so that examples are controlled by "
            f"'option({option_name} ... ${{PROJECT_IS_TOP_LEVEL}})' "
            f"and guarded by 'if({option_name})' before "
            "'add_subdirectory(examples...)'. "
            f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#{self._STANDARD_ANCHOR} for more information."
        )
        return False


# TODO cmake.avoid_passthroughs
