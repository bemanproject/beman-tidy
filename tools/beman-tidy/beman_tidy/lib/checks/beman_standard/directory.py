#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

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


@register_beman_standard_check("DIRECTORY.INTERFACE_HEADERS")
class DirectoryInterfaceHeadersCheck(BemanTreeDirectoryCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "include")

    def pre_check(self):
        # Need to override this, because DIRECTORY.INTERFACE_HEADERS is conditional
        # (a repo without any interface header files is still valid).
        return True

    def check(self):
        """
        Check that all public header files reside within the include/beman/<short_name>/ directory.
        """
        # Exclude certain directories.
        exclude_dirs = ["src"]
        if self.path.exists():
            exclude_dirs.append(f"include/beman/{self.repo_name}")
        if self.repo_name == "exemplar":
            exclude_dirs.append("cookiecutter")

        # Find all misplaced public header files in the repository.
        header_extensions = [".hpp", ".hxx", ".h", ".hh"]
        misplaced_header_files = []

        for extension in header_extensions:
            for p in self.repo_path.rglob(f"*{extension}"):
                # Check if any part of the path contains an excluded directory
                if not any(excluded in str(p) for excluded in exclude_dirs):
                    misplaced_header_files.append(p)

        if len(misplaced_header_files) > 0:
            for misplaced_header_file in misplaced_header_files:
                self.log(f"Misplaced header file found: {misplaced_header_file}")

            self.log(
                "Please move all public header files within the include/beman/<short_name>/ directory. "
                "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directoryinterface_headers for more information."
            )
            return False

        # Check passes if the include/beman/<short_name>/ directory does not exist
        # or all header files are within include/beman/<short_name>/ directory.
        return True

    def fix(self):
        self.log(
            f"Please manually move interface header files to include/beman/{self.repo_name}. "
            "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directoryinterface_headers for more information."
        )


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


@register_beman_standard_check("DIRECTORY.EXAMPLES")
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
                "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directoryexamples for more information."
            )
            return False

        if len(list(self.path.glob("**/*CMakeLists.txt"))) == 0:
            self.log(
                "Missing CMakeLists.txt for examples - cannot find examples/**/*CMakeLists.txt. "
                "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directoryexamples for more information."
            )
            return False

        # Check passes if the examples/ directory exists and contains at least one relevant example.
        return True

    def fix(self):
        self.log(
            "Please add a relevant example to the examples/ directory. "
            "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directoryexamples for more information."
        )


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
        # (a repo without any documentation is still valid).
        return True

    def check(self):
        # Exclude directories that are not part of the documentation.
        exclude_dirs = ["papers", ".github"]
        if self.path.exists():
            exclude_dirs.append("docs")
        if self.repo_name == "exemplar":
            exclude_dirs.extend(["cookiecutter", "infra"])

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
                self.log(f"Misplaced MD file found: {misplaced_md_file}")

            self.log(
                "Please move all documentation files within the docs/ directory, except for the root README.md file. "
                "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorydocs for more information."
            )

            return False

        # Check passes if there is no docs/ directory or no misplaced MD files are found
        return True

    def fix(self):
        self.log(
            "Please manually move documentation files to the docs/ directory, except for the root README.md file. "
            "See https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md#directorydocs for more information."
        )


# TODO DIRECTORY.PAPERS
