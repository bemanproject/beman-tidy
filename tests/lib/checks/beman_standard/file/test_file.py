#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
import os
from pathlib import Path
from unittest.mock import patch

from beman_tidy.lib.checks.beman_standard.file import FileCopyrightCheck
from tests.utils.conftest import mock_repo_info, mock_beman_standard_check_config  # noqa: F401

test_data_prefix = "tests/lib/checks/beman_standard/file/data"
valid_prefix = f"{test_data_prefix}/valid"
invalid_prefix = f"{test_data_prefix}/invalid"

@pytest.fixture(autouse=True)
def repo_info(mock_repo_info):  # noqa: F811
    return mock_repo_info

@pytest.fixture
def beman_standard_check_config(mock_beman_standard_check_config):  # noqa: F811
    return mock_beman_standard_check_config

def test__file_copyright__valid(repo_info, beman_standard_check_config):
    valid_paths = [
        Path(f"{valid_prefix}/valid.hpp"),
        Path(f"{valid_prefix}/valid.cpp"),
    ]
    
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    
    # Mock get_source_files to return our test files
    with patch('beman_tidy.lib.checks.beman_standard.file.get_source_files') as mock_get_files:
        mock_get_files.return_value = valid_paths
        assert check.check() is True

def test__file_copyright__invalid(repo_info, beman_standard_check_config):
    invalid_paths = [
        Path(f"{invalid_prefix}/invalid.hpp"),
        Path(f"{invalid_prefix}/invalid.cpp"),
    ]
    
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    
    # Mock get_source_files to return our test files
    with patch('beman_tidy.lib.checks.beman_standard.file.get_source_files') as mock_get_files:
        mock_get_files.return_value = invalid_paths
        assert check.check() is False

def test__file_copyright__fix_inplace(repo_info, beman_standard_check_config):
    invalid_paths = [
        Path(f"{invalid_prefix}/invalid.hpp"),
        Path(f"{invalid_prefix}/invalid.cpp"),
    ]
    
    for path in invalid_paths:
        # Create temp file
        temp_path = Path(f"{path}.delete_me")
        temp_path.write_text(path.read_text())
        
        check = FileCopyrightCheck(repo_info, beman_standard_check_config)
        
        # Mock get_source_files to return our temp file
        with patch('beman_tidy.lib.checks.beman_standard.file.get_source_files') as mock_get_files:
            mock_get_files.return_value = [temp_path]
            
            assert check.check() is False
            assert check.fix() is True
            assert check.check() is True
        
        # Verify content
        content = temp_path.read_text()
        
        lines = content.splitlines()
        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            if line.strip().startswith("//"):
                 assert "Copyright" not in line, f"Copyright still present in {line}"
        
        # Cleanup
        os.remove(temp_path)
