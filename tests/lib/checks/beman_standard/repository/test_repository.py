#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
from pathlib import Path

from tests.utils.path_runners import (
    run_check_for_each_path,
    run_check_for_each_repo_info,
)

# Actual tested checks.
from beman_tidy.lib.checks.beman_standard.repository import (
    RepositoryNameCheck,
    RepositoryCodeownersCheck,
    RepositoryDefaultBranchCheck,
    RepositoryDisallowGitSubmodulesCheck,
)

test_data_prefix = "tests/lib/checks/beman_standard/repository/data"
valid_prefix = f"{test_data_prefix}/valid"
invalid_prefix = f"{test_data_prefix}/invalid"


def test__REPOSITORY_NAME__valid(repo_info, beman_standard_check_config):
    """
    Test that repositories with valid repository names pass the check.
    """
    # Create mock repo info with valid repository names
    valid_repo_infos = [
        repo_info.copy() | {"name": "exemplar"},
        repo_info.copy() | {"name": "optional"},
        repo_info.copy() | {"name": "smart_pointer"},
        repo_info.copy() | {"name": "execution"},
        repo_info.copy() | {"name": "utf_view"},
        repo_info.copy() | {"name": "net"},
    ]

    run_check_for_each_repo_info(
        True,
        RepositoryNameCheck,
        valid_repo_infos,
        beman_standard_check_config,
    )


def test__REPOSITORY_NAME__invalid(repo_info, beman_standard_check_config):
    """
    Test that repositories with invalid repository names fail the check.
    """
    # Create mock repo info with invalid repository names
    invalid_repo_infos = [
        repo_info.copy() | {"name": "beman.exemplar"},
        repo_info.copy() | {"name": "exemplar26"},
        repo_info.copy() | {"name": "beman.exemplar26"},
        repo_info.copy() | {"name": "exemplar_"},
        repo_info.copy() | {"name": "_exemplar"},
        repo_info.copy() | {"name": "optional26"},
        repo_info.copy() | {"name": "execution26"},
        repo_info.copy() | {"name": "net29"},
    ]

    run_check_for_each_repo_info(
        False,
        RepositoryNameCheck,
        invalid_repo_infos,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="NOT implemented")
def test__REPOSITORY_NAME__fix_inplace(repo_info, beman_standard_check_config):
    pass


def test__REPOSITORY_CODEOWNERS__valid(repo_info, beman_standard_check_config):
    """
    Test that repositories with valid CODEOWNERS pass the check.
    """
    valid_codeowners_paths = [
        # exemplar/ repo with valid .github/CODEOWNERS file.
        Path(f"{valid_prefix}/repo-exemplar-v1/"),
    ]

    run_check_for_each_path(
        True,
        valid_codeowners_paths,
        RepositoryCodeownersCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__REPOSITORY_CODEOWNERS__invalid(repo_info, beman_standard_check_config):
    """
    Test that repositories with invalid CODEOWNERS fail the check.
    """
    invalid_codeowners_paths = [
        # exemplar/ repo without CODEOWNERS file inside .github/.
        Path(f"{invalid_prefix}/repo-exemplar-v1/"),
        # exemplar/ repo with CODEOWNERS in root.
        Path(f"{invalid_prefix}/repo-exemplar-v2/"),
        # exemplar/ repo with empty .github/CODEOWNERS.
        Path(f"{invalid_prefix}/repo-exemplar-v3/"),
    ]

    run_check_for_each_path(
        False,
        invalid_codeowners_paths,
        RepositoryCodeownersCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="NOT implemented")
def test__REPOSITORY_CODEOWNERS__fix_inplace(repo_info, beman_standard_check_config):
    pass


def test__REPOSITORY_DEFAULT_BRANCH__valid(repo_info, beman_standard_check_config):
    """
    Test that repositories with valid default branch pass the check.
    """
    # Create mock repo info with valid default branch
    valid_repo_infos = [
        repo_info.copy() | {"default_branch": "main"},
    ]

    run_check_for_each_repo_info(
        True,
        RepositoryDefaultBranchCheck,
        valid_repo_infos,
        beman_standard_check_config,
    )


def test__REPOSITORY_DEFAULT_BRANCH__invalid(repo_info, beman_standard_check_config):
    """
    Test that repositories with invalid default branch fail the check.
    """
    # Test various invalid branch names
    invalid_repo_infos = [
        repo_info.copy() | {"default_branch": "master"},
        repo_info.copy() | {"default_branch": "develop"},
        repo_info.copy() | {"default_branch": "dev"},
        repo_info.copy() | {"default_branch": "trunk"},
        repo_info.copy() | {"default_branch": "default"},
        repo_info.copy() | {"default_branch": "production"},
        repo_info.copy() | {"default_branch": "release"},
        repo_info.copy() | {"default_branch": "stable"},
        repo_info.copy() | {"default_branch": "testing"},
        repo_info.copy() | {"default_branch": "alpha"},
        repo_info.copy() | {"default_branch": "beta"},
        repo_info.copy() | {"default_branch": "experimental"},
    ]

    run_check_for_each_repo_info(
        False,
        RepositoryDefaultBranchCheck,
        invalid_repo_infos,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="NOT implemented")
def test__REPOSITORY_DEFAULT_BRANCH__fix_inplace(
    repo_info, beman_standard_check_config
):
    pass


def test__REPOSITORY_DISALLOW_GIT_SUBMODULES__valid(
    repo_info, beman_standard_check_config
):
    """
    Test that repositories with valid git submodules pass the check.
    """
    valid_submodules_paths = [
        # Repo with no .gitsubmodules
        Path(f"{valid_prefix}/repo-exemplar-v1/"),
        # Repo with wg21 git submodule
        Path(f"{valid_prefix}/repo-exemplar-v2/"),
    ]

    run_check_for_each_path(
        True,
        valid_submodules_paths,
        RepositoryDisallowGitSubmodulesCheck,
        repo_info,
        beman_standard_check_config,
    )


def test__REPOSITORY_DISALLOW_GIT_SUBMODULES__invalid(
    repo_info, beman_standard_check_config
):
    """
    Test that repositories with invalid git submodules fail the check.
    """
    invalid_submodules_paths = [
        # Repository with a single non-wg21 submodule
        Path(f"{invalid_prefix}/repo-exemplar-v1/"),
        # Repository with multiple submodules including wg21
        Path(f"{invalid_prefix}/repo-exemplar-v2/"),
        # Repository with multiple non-wg21 submodules
        Path(f"{invalid_prefix}/repo-exemplar-v3/"),
    ]

    run_check_for_each_path(
        False,
        invalid_submodules_paths,
        RepositoryDisallowGitSubmodulesCheck,
        repo_info,
        beman_standard_check_config,
    )


@pytest.mark.skip(reason="NOT implemented")
def test__REPOSITORY_DISALLOW_GIT_SUBMODULES__inplace(
    repo_info, beman_standard_check_config
):
    pass
