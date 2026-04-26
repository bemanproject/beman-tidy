#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import re

from ..base.base_check import BaseCheck
from ..base.file_base_check import FileBaseCheck
from ..system.registry import register_beman_standard_check
from ...utils.file import get_cmake_files
from ...utils.config import get_ignores

# [cmake.*] checks category.
# All checks in this file extend the CMakeBaseCheck class.
#
# Note: CMakeBaseCheck is not a registered check!


class CMakeBaseCheck(FileBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "CMakeLists.txt")


# TODO cmake.default


# TODO cmake.use_find_package


# TODO cmake.project_name


# TODO cmake.passive_projects


# TODO cmake.library_name


# TODO cmake.library_alias


# TODO cmake.target_names


# TODO cmake.passive_targets


# TODO cmake.skip_tests


# TODO cmake.skip_examples


# TODO cmake.avoid_passthroughs


@register_beman_standard_check("cmake.implicit_defaults")
class CmakeImplicitDefaultsCheck(BaseCheck):
    """
    [cmake.implicit_defaults]
    Recommendation: Where CMake commands have reasonable default values, and the
    project does not intend to change those values, the parameters should be left
    implicitly defaulted rather than enumerated in the command.

    Specifically checks for redundant DESTINATION arguments in install() calls
    that match GNUInstallDirs defaults.
    """

    # Redundant destination patterns inside install() calls.
    # These are the GNUInstallDirs defaults — specifying them explicitly is noise.
    _REDUNDANT_PATTERNS = [
        (
            re.compile(r'\bDESTINATION\s+\$\{CMAKE_INSTALL_LIBDIR\}'),
            "DESTINATION ${CMAKE_INSTALL_LIBDIR} (this is the default for libraries)",
        ),
        (
            re.compile(r'\bRUNTIME\s+DESTINATION\s+\$\{CMAKE_INSTALL_BINDIR\}'),
            "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} (this is the default)",
        ),
        (
            re.compile(r'\bFILE_SET\s+HEADERS\s+DESTINATION\s+\$\{CMAKE_INSTALL_INCLUDEDIR\}'),
            "FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR} (this is the default)",
        ),
    ]

    _COMMENT_RE = re.compile(r"#[^\n]*")

    def _read_cmake_files(self):
        ignores = get_ignores(self.repo_info)
        result = {}
        for rel_path in get_cmake_files(self.repo_path, ignores=ignores):
            abs_path = self.repo_path / rel_path
            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
                result[rel_path] = self._COMMENT_RE.sub("", content)
            except Exception:
                pass
        return result

    def check(self):
        cmake_files = self._read_cmake_files()
        all_passed = True

        for rel_path, content in cmake_files.items():
            for pattern, description in self._REDUNDANT_PATTERNS:
                if pattern.search(content):
                    self.log(
                        f"{rel_path}: Redundant install() argument: {description}. "
                        f"Remove it and rely on the CMake default. "
                        f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakeimplicit_defaults"
                    )
                    all_passed = False

        return all_passed

    def fix(self):
        # Auto-removing install() arguments requires careful CMake parsing;
        # flag as not auto-fixable to avoid corrupting CMake files.
        self.log(
            "Auto-fix is not supported for cmake.implicit_defaults. "
            "Please remove the redundant DESTINATION arguments manually."
        )
        return False


@register_beman_standard_check("cmake.no_single_use_vars")
class CmakeNoSingleUseVarsCheck(BaseCheck):
    """
    [cmake.no_single_use_vars]
    Recommendation: Avoid using set() to create variables that are only used once.
    Prefer using the value(s) directly in such cases.
    """

    # Matches: set(VAR_NAME ...) — captures VAR_NAME
    _SET_RE = re.compile(r"^\s*set\s*\(\s*(\w+)", re.MULTILINE)
    # Cache variables are exempt (they serve a different purpose)
    _CACHE_RE = re.compile(r"\bCACHE\b")
    _COMMENT_RE = re.compile(r"#[^\n]*")

    def _read_cmake_files(self):
        ignores = get_ignores(self.repo_info)
        result = {}
        for rel_path in get_cmake_files(self.repo_path, ignores=ignores):
            abs_path = self.repo_path / rel_path
            try:
                content = abs_path.read_text(encoding="utf-8", errors="ignore")
                result[rel_path] = self._COMMENT_RE.sub("", content)
            except Exception:
                pass
        return result

    def _find_set_call_end(self, content, match_start):
        """Find the closing paren of the set() call starting at match_start."""
        depth = 0
        for i in range(match_start, min(match_start + 500, len(content))):
            if content[i] == "(":
                depth += 1
            elif content[i] == ")":
                depth -= 1
                if depth == 0:
                    return i
        return match_start + 500

    def _find_violations(self, cmake_files):
        """
        Returns list of (var_name, rel_path) for variables set once and used once.
        Cross-file analysis: counts usages across all cmake files.
        """
        all_content = "\n".join(cmake_files.values())

        # Collect non-cache set() definitions: {var_name: [rel_path, ...]}
        definitions = {}
        for rel_path, content in cmake_files.items():
            for m in self._SET_RE.finditer(content):
                var_name = m.group(1)
                end = self._find_set_call_end(content, m.start())
                call_text = content[m.start():end]
                if self._CACHE_RE.search(call_text):
                    continue
                definitions.setdefault(var_name, []).append(rel_path)

        # Count ${VAR_NAME} references across all files
        violations = []
        for var_name, def_paths in definitions.items():
            ref_re = re.compile(r"\$\{" + re.escape(var_name) + r"\}")
            total_uses = len(ref_re.findall(all_content))
            if total_uses == 1:
                for rel_path in def_paths:
                    violations.append((var_name, rel_path))

        return violations

    def check(self):
        cmake_files = self._read_cmake_files()
        if not cmake_files:
            return True

        violations = self._find_violations(cmake_files)
        for var_name, rel_path in violations:
            self.log(
                f"{rel_path}: Variable '{var_name}' is defined with set() but used only once. "
                f"Consider inlining the value directly. "
                f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cmakeno_single_use_vars"
            )
        return len(violations) == 0

    def fix(self):
        # Inlining a variable requires replacing the ${VAR} reference with the
        # original value and removing the set() call — too risky to automate.
        self.log(
            "Auto-fix is not supported for cmake.no_single_use_vars. "
            "Please inline the variable value manually."
        )
        return False
