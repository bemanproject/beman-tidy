#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

from ..base.directory_base_check import DirectoryBaseCheck
from ..system.registry import register_beman_standard_check


# [DIRECTORY.*] checks category.
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
    """

    def __init__(self, repo_info, beman_standard_check_config, prefix_path):
        super().__init__(
            repo_info,
            beman_standard_check_config,
            f"{prefix_path}/beman/{repo_info['name']}",
        )


# TODO DIRECTORY.INTERFACE_HEADERS


# TODO DIRECTORY.IMPLEMENTATION_HEADERS


@register_beman_standard_check("DIRECTORY.SOURCES")
class DirectorySourcesCheck(BemanTreeDirectoryCheck):
    """
    Check if the sources directory is src/beman/<short_name>.
    Note: Allow header-only libraries (missing any source files location).

    Example for a repo named "exemplar": src/beman/exemplar
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "src")

    def pre_check(self):
        # Need to override this, because DIRECTORY.SOURCES is conditional
        # (a repo without any source files location is still valid - header only libraries)
        return True

    def check(self):
        # TODO: This is a temporary implementation. Use CMakeLists.txt to actually get the source files location.
        # Should not allow other known source locations.
        forbidden_source_locations = ["source/", "sources/", "lib/", "library/"]
        for forbidden_prefix in forbidden_source_locations:
            forbidden_prefix = self.repo_path / forbidden_prefix
            if forbidden_prefix.exists():
                self.log(
                    f"Please move source files from {forbidden_prefix} to src/beman/{self.repo_name}. See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorysources for more information."
                )
                return False

        # If `src/` exists, src/beman/<short_name> also should exist.
        if (self.repo_path / "src/").exists() and not self.path.exists():
            self.log(
                f"Please use the required source files location: src/beman/{self.repo_name}. See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorysources for more information."
            )
            return False

        # Valid source file location or missing -> Beman Standard compliant.
        return True

    def fix(self):
        # Because we don't know which is the actually invalid source file locations,
        # we cannot do a proper implementation for fix().
        if not self.check():
            self.log(
                f"Please manually move sources to src/beman/{self.repo_name}. See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorysources for more information."
            )


# TODO DIRECTORY.TESTS


# TODO DIRECTORY.EXAMPLES


@register_beman_standard_check("DIRECTORY.DOCS")
class DirectoryDocsCheck(DirectoryBaseCheck):
    """
    Check if the all documentation files reside within docs/ directory.
    Exception: root README.md file.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "docs")

    def pre_check(self):
        # Need to override this, because DIRECTORY.DOCS is conditional
        # (a repo without any documentation is still valid)
        return True

    def check(self):
        repo_path = Path(self.repo_path)
        root_readme = repo_path / "README.md"

        # Exclude directories that are not part of the documentation.
        exclude_dirs = ["papers", ".github"]

        if self.path.exists():
            exclude_dirs.append("docs")

        if self.repo_name == "exemplar":
            exclude_dirs.extend(["cookiecutter", "infra"])

        # Find all markdown files in the repository.
        misplaced_md_files = [
            p
            for p in repo_path.rglob("*.md")
            if not any(
                excluded in p.parts for excluded in exclude_dirs
            )  # exclude files in excluded directories
            and p != root_readme  # exclude root README.md
        ]

        # Check if any markdown files are misplaced.
        if len(misplaced_md_files) > 0:
            for misplaced_md_file in misplaced_md_files:
                self.log(f"Misplaced markdown file found: {misplaced_md_file}")

            self.log(
                "Please move all documentation files within the docs/ directory, except for the root README.md file. "
                "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorydocs for more information."
            )

            return False

        # Check passes if there is no docs/ directory or no misplaced markdown files are found
        return True

    def fix(self):
        self.log(
            "Please manually move documentation files to the docs/ directory, except for the root README.md file. "
            "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorydocs for more information."
        )


# TODO DIRECTORY.PAPERS
