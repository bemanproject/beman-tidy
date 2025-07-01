#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pathlib
from pathlib import Path

from tests.utils.file_testcase_runners import (
    file_testcases_run_valid,
    file_testcases_run_fix_not_exist,
)

# Actual tested checks.
from beman_tidy.lib.checks.beman_standard.toplevel import (
    TopLevelLicenseCheck,
)

test_data_prefix = str(pathlib.Path(__file__).parent.resolve())
valid_prefix = f"{test_data_prefix}/valid"
invalid_prefix = f"{test_data_prefix}/invalid"


def test_TOPLEVEL_LICENSE_valid(repo_info, beman_standard_check_config):
    """Test valid cases for the TopLevelLicenseCheck."""

    valid_license_path = [Path(f"{valid_prefix}/LICENSE")]

    file_testcases_run_valid(
        valid_license_path, TopLevelLicenseCheck, repo_info, beman_standard_check_config
    )


def test_TOPLEVEL_LICENSE_not_exist_and_fix(repo_info, beman_standard_check_config):
    """Test valid cases for the TopLevelLicenseCheck."""

    invalid_license_path = [Path(f"{invalid_prefix}/LICENSE")]

    file_testcases_run_fix_not_exist(
        invalid_license_path,
        TopLevelLicenseCheck,
        repo_info,
        beman_standard_check_config,
    )
