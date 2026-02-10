#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.directory_base_check import DirectoryBaseCheck
from ..system.registry import register_beman_standard_check
from beman_tidy.lib.utils.string import normalize_path_for_display


# [directory.*] checks category.
# All checks in this file extend the DirectoryBaseCheck class.
#
# Note: DirectoryBaseCheck is not a registered check!
class BemanTreeDirectoryCheck(DirectoryBaseCheck):
    """
    Beman tree: ${prefix_path}/beman/${short_name}.
    Available via member: self.path

    Examples for a repo named "exemplar":
    - include/beman/exemplar
    - tests/beman/exemplar
    - src/beman/exemplar

    Note: A path can be optional. Actual implementation will be in the derived's check().

    The short_name is obtained from the repository's remote URL (via repo_info['short_name']),
    not from the local checkout directory name, to avoid coupling to the directory name.
    """

    def __init__(self, repo_info, beman_standard_check_config, prefix_path):
        # Use short_name from repo_info, which is parsed from the remote URL
        # Fall back to 'name' (checkout directory) if short_name is not available
        short_name = repo_info.get("short_name", repo_info["name"])
        self.short_name = short_name
        super().__init__(
            repo_info,
            beman_standard_check_config,
            f"{prefix_path}/beman/{short_name}",
        )


# TODO directory.interface_headers


# TODO directory.implementation_headers


@register_beman_standard_check("directory.sources")
class DirectorySourcesCheck(BemanTreeDirectoryCheck):
    """
    Check if the sources directory is src/beman/<short_name>.
    Note: Allow header-only libraries (missing any source files location).

    Example for a repo named "exemplar": src/beman/exemplar
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "src")

    def pre_check(self):
        # Need to override this, because directory.sources is conditional
        # (a repo without any source files location is still valid - header only libraries)
        return True

    def check(self):
        # TODO: This is a temporary implementation. Use CMakeLists.txt to actually get the source files location.
        # Should not allow other known source locations.
        forbidden_source_locations = ["source/", "sources/", "lib/", "library/"]
        for forbidden_prefix in forbidden_source_locations:
            forbidden_prefix = self.repo_path / forbidden_prefix
            if forbidden_prefix.exists():
                display_path = normalize_path_for_display(forbidden_prefix, self.repo_path)
                self.log(
                    f"Please move source files from {display_path} to src/beman/{self.short_name}. See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorysources for more information."
                )
                return False

        # If `src/` exists, src/beman/<short_name> also should exist.
        if (self.repo_path / "src/").exists() and not self.path.exists():
            self.log(
                f"Please use the required source files location: src/beman/{self.short_name}. See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorysources for more information."
            )
            return False

        # Valid source file location or missing -> Beman Standard compliant.
        return True

    def fix(self):
        # Because we don't know which is the actually invalid source file locations,
        # we cannot do a proper implementation for fix().
        if not self.check():
            self.log(
                f"Please manually move sources to src/beman/{self.short_name}. See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorysources for more information."
            )


@register_beman_standard_check("directory.tests")
class DirectoryTestsCheck(BemanTreeDirectoryCheck):
    """
    Check if all test files reside within tests/beman/<short_name> directory.
    Examples:
    tests
    └── beman
        └── exemplar
            └── identity.test.cpp

    tests
    └── beman
        └── optional
            ├── CMakeLists.txt
            ├── detail
            |   └── iterator.test.cpp
            ├── optional.test.cpp
            ├── optional_constexpr.test.cpp
            ├── optional_monadic.test.cpp
            ├── optional_range_support.test.cpp
            ├── test_types.cpp
            ├── test_types.hpp
            ├── test_utilities.cpp
            └── test_utilities.hpp
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "tests")

    def check(self):
        # Exclude directories that are not part of the tests.
        exclude_dirs = [".github", f"tests/beman/{self.short_name}", ".git", "infra"]
        if self.short_name == "exemplar":
            exclude_dirs.append("cookiecutter")

        # Find all test files in the repository outside the excluded directories.
        misplaced_test_files = []
        for p in self.repo_path.rglob("*.test.*"):
            if not any(excluded in str(p) for excluded in exclude_dirs):
                misplaced_test_files.append(p)

        # Check if any test files are misplaced outside the excluded directories.
        if len(misplaced_test_files) > 0:
            for misplaced_test_file in misplaced_test_files:
                display_path = normalize_path_for_display(misplaced_test_file, self.repo_path)
                self.log(f"Misplaced test file found: {display_path}")

            self.log(
                "Please move all test files within the tests/ directory. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorytests for more information."
            )
            return False

        # Check if the repository has at least one relevant test inside tests/beman/<short_name>.
        relevant_test_files = list(self.path.rglob("*.test.*"))
        relevant_cmake_files = list(self.path.rglob("CMakeLists.txt"))

        if len(relevant_test_files) == 0 or len(relevant_cmake_files) == 0:
            self.log(
                "Missing relevant test files in tests/ directory. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorytests for more information."
            )
            return False

        # Check passes if the tests/ directory exists and contains relevant test files.
        return True

    def fix(self):
        self.log(
            "Please manually move test files to the tests/beman/<short_name> directory. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorytests for more information."
        )


@register_beman_standard_check("directory.examples")
class DirectoryExamplesCheck(DirectoryBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "examples")

    def check(self):
        """
        All example files must reside within the top-level examples/ directory. Each project must have at least one relevant example.
        Tree Example:
        examples/
        ├── CMakeLists.txt
        ├── identity_as_default_projection.cpp
        └── identity_direct_usage.cpp
        """
        # Check if the examples/ directory contains at least one relevant example.
        if len(list(self.path.glob("**/*.cpp"))) == 0:
            self.log(
                "Missing one relevant example - cannot find examples/**/*.cpp. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directoryexamples for more information."
            )
            return False

        if len(list(self.path.glob("**/*CMakeLists.txt"))) == 0:
            self.log(
                "Missing CMakeLists.txt for examples - cannot find examples/**/*CMakeLists.txt. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directoryexamples for more information."
            )
            return False

        # Check passes if the examples/ directory exists and contains at least one relevant example.
        return True

    def fix(self):
        self.log(
            "Please add a relevant example to the examples/ directory. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directoryexamples for more information."
        )


@register_beman_standard_check("directory.docs")
class DirectoryDocsCheck(DirectoryBaseCheck):
    """
    Check if the all documentation files reside within docs/ directory.
    Exception: root README.md file.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "docs")

    def pre_check(self):
        # Need to override this, because directory.docs is conditional
        # (a repo without any documentation is still valid).
        return True

    def check(self):
        # Exclude directories that are not part of the documentation.
        exclude_dirs = ["src", "papers", "examples", ".github", "infra"]
        if self.path.exists():
            exclude_dirs.append("docs")
        if self.repo_name == "exemplar":
            exclude_dirs.append("cookiecutter")

        # Find all MD files in the repository.
        misplaced_md_files = [
            p
            for p in self.repo_path.rglob("*.md")
            if not any(
                excluded in p.parts for excluded in exclude_dirs
            )  # exclude files in excluded directories
            and p != self.repo_path / "README.md"  # exclude root README.md
        ]

        # Check if any MD files are misplaced.
        if len(misplaced_md_files) > 0:
            for misplaced_md_file in misplaced_md_files:
                display_path = normalize_path_for_display(misplaced_md_file, self.repo_path)
                self.log(f"Misplaced MD file found: {display_path}")

            self.log(
                "Please move all documentation files within the docs/ directory, except for the root README.md file. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorydocs for more information."
            )

            return False

        # Check passes if there is no docs/ directory or no misplaced MD files are found
        return True

    def fix(self):
        self.log(
            "Please manually move documentation files to the docs/ directory, except for the root README.md file. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorydocs for more information."
        )


@register_beman_standard_check("directory.papers")
class DirectoryPapersCheck(DirectoryBaseCheck):
    """
    Check if the all paper related files reside within papers/ directory.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "papers")

    def pre_check(self):
        # Need to override this, because directory.papers is conditional
        # (a repo without any paper files is still valid - no papers/ directory required)
        return True

    def check(self):
        """
        If present, all paper related files (e.g., WIP LaTeX/Markdown projects for ISO Standardization), must reside within the top-level papers/ directory.
        Tree Example:
        papers/
        └── P2988
            ├── Makefile
            ├── README.md
            └── abstract.bst
        """
        # Exclude directories that are not part of the papers/ directory.
        exclude_dirs = ["src", "docs", "examples", ".github", "infra"]
        if self.path.exists():
            exclude_dirs.append("papers")
        if self.repo_name == "exemplar":
            exclude_dirs.append("cookiecutter")

        # File extensions that are considered "paper-related"
        paper_extensions = [
            ".md",
            ".bib",
            ".bst",
            ".tex",
            ".sty",
            ".cls",
            ".pdf",
            ".docx",
            ".org",
            ".html",
            ".css",
            ".js",
            ".asciidoc",
            ".asc",
            ".ad",
            ".ascdoc",
            ".rst",
            ".wip",
            ".draft",
            ".proposal",
            ".standard",
        ]

        # Find all misplaced paper-related files in the repository.
        misplaced_paper_files = []
        for extension in paper_extensions:
            for p in self.repo_path.rglob(f"*{extension}"):
                # Exclude files that are already in excluded directories.
                if (
                    not any(excluded in str(p) for excluded in exclude_dirs)
                    and p != self.repo_path / "README.md"
                ):
                    misplaced_paper_files.append(p)

        if len(misplaced_paper_files) > 0:
            for misplaced_paper_file in misplaced_paper_files:
                display_path = normalize_path_for_display(misplaced_paper_file, self.repo_path)
                self.log(f"Misplaced paper file found: {display_path}")

            self.log(
                "Please move all paper related files (and directories if applicable) within the papers/ directory. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorypapers for more information."
            )

            return False

        # Check passes if there is no papers/ directory and no misplaced paper files are found
        return True

    def fix(self):
        self.log(
            "Please move all paper related files (and directories if applicable) to papers/ directory. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#directorypapers for more information."
        )
