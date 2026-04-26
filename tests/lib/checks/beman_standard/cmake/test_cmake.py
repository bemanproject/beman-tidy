#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

from beman_tidy.lib.checks.beman_standard.cmake import (
    CmakeImplicitDefaultsCheck,
    CmakeNoSingleUseVarsCheck,
)

test_data_prefix = Path("tests/lib/checks/beman_standard/cmake/data")

# --- cmake.implicit_defaults tests ---

def test__cmake_implicit_defaults__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_data_prefix / "implicit_defaults" / "valid"
    check = CmakeImplicitDefaultsCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


def test__cmake_implicit_defaults__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_data_prefix / "implicit_defaults" / "invalid"
    check = CmakeImplicitDefaultsCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


def test__cmake_implicit_defaults__fix_inplace(repo_info, beman_standard_check_config):
    # Auto-fix not supported — fix() must return False
    repo_info["top_level"] = test_data_prefix / "implicit_defaults" / "invalid"
    check = CmakeImplicitDefaultsCheck(repo_info, beman_standard_check_config)
    assert check.check() is False
    assert check.fix() is False


# --- cmake.no_single_use_vars tests ---

def test__cmake_no_single_use_vars__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_data_prefix / "no_single_use_vars" / "valid"
    check = CmakeNoSingleUseVarsCheck(repo_info, beman_standard_check_config)
    assert check.check() is True


def test__cmake_no_single_use_vars__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = test_data_prefix / "no_single_use_vars" / "invalid"
    check = CmakeNoSingleUseVarsCheck(repo_info, beman_standard_check_config)
    assert check.check() is False


def test__cmake_no_single_use_vars__fix_inplace(repo_info, beman_standard_check_config):
    # Auto-fix not supported — fix() must return False
    repo_info["top_level"] = test_data_prefix / "no_single_use_vars" / "invalid"
    check = CmakeNoSingleUseVarsCheck(repo_info, beman_standard_check_config)
    assert check.check() is False
    assert check.fix() is False
