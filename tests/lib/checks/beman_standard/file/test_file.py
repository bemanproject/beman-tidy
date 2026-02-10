#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shutil
from pathlib import Path

from beman_tidy.lib.checks.beman_standard.file import FileCopyrightCheck

test_data_prefix = Path("tests/lib/checks/beman_standard/file/data")
valid_prefix = test_data_prefix / "valid"
invalid_prefix = test_data_prefix / "invalid"

def test__file_copyright__valid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = valid_prefix
    
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is True

def test__file_copyright__invalid(repo_info, beman_standard_check_config):
    repo_info["top_level"] = invalid_prefix
    
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    assert check.check() is False

def test__file_copyright__fix_inplace(repo_info, beman_standard_check_config, tmp_path):
    for item in invalid_prefix.iterdir():
        if item.is_file():
            shutil.copy(item, tmp_path / item.name)
    
    repo_info["top_level"] = tmp_path
    check = FileCopyrightCheck(repo_info, beman_standard_check_config)
    
    assert check.check() is False
    
    assert check.fix() is True
    
    assert check.check() is True
    
    for item in invalid_prefix.iterdir():
        if not item.is_file():
            continue
            
        fixed_file = tmp_path / item.name
        content = fixed_file.read_text()
        lines = content.splitlines()
        
        for line in lines:
            if "SPDX-License-Identifier:" in line:
                continue
            if line.strip().startswith("//"):
                 assert "Copyright" not in line, f"Copyright still present in {fixed_file.name}: {line}"
