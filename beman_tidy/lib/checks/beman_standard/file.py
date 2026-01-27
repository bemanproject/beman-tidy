#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.base_check import BaseCheck
from ..system.registry import register_beman_standard_check
from ...utils.files import get_source_files

# [file.*] checks category.
# All checks in this file extend the BaseCheck class.


# TODO file.names


# TODO file.test_names


# TODO file.license_id


@register_beman_standard_check("file.copyright")
class FileCopyrightCheck(BaseCheck):
    """
    [file.copyright]
    Recommendation: Source code files should NOT include a copyright notice following the SPDX license identifier.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        source_files = get_source_files(self.repo_path)
        all_passed = True
        for relative_path in source_files:
            if not self._check_file(relative_path):
                all_passed = False
        return all_passed

    def fix(self):
        source_files = get_source_files(self.repo_path)
        all_fixed = True
        for relative_path in source_files:
            if not self._fix_file(relative_path):
                all_fixed = False
        return all_fixed

    def _check_file(self, relative_path):
        path = self.repo_path / relative_path
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except Exception:
            return True

        spdx_index = -1
        
        for i, line in enumerate(lines):
            if "SPDX-License-Identifier:" in line:
                spdx_index = i
                break
        
        if spdx_index == -1:
            return True

        spdx_line = lines[spdx_index].strip()
        comment_prefix = None
        if spdx_line.startswith("//"):
            comment_prefix = "//"
        elif spdx_line.startswith("#"):
            comment_prefix = "#"
        
        if comment_prefix is None:
            # TODO: Support block comments (e.g. Markdown <!-- ... --> or C++ /* ... */)
            return True

        # Check subsequent lines
        for i in range(spdx_index + 1, len(lines)):
            line = lines[i].strip()
            
            # Allow empty lines
            if not line:
                continue
                
            # If it doesn't start with comment prefix, assume end of header comments
            if not line.startswith(comment_prefix):
                break
            
            lower_line = line.lower()
            if "copyright" in lower_line or "(c)" in lower_line:
                self.log(f"Copyright notice found in {relative_path} at line {i+1}. It should be removed.")
                return False
                
        return True

    def _fix_file(self, relative_path):
        path = self.repo_path / relative_path
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except Exception:
            return True

        spdx_index = -1
        
        for i, line in enumerate(lines):
            if "SPDX-License-Identifier:" in line:
                spdx_index = i
                break
        
        if spdx_index == -1:
            return True

        spdx_line = lines[spdx_index].strip()
        comment_prefix = None
        if spdx_line.startswith("//"):
            comment_prefix = "//"
        elif spdx_line.startswith("#"):
            comment_prefix = "#"
            
        if comment_prefix is None:
            return True

        new_lines = []
        new_lines.extend(lines[:spdx_index+1])
        
        i = spdx_index + 1
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped:
                new_lines.append(line)
                i += 1
                continue
                
            if not stripped.startswith(comment_prefix):
                new_lines.extend(lines[i:])
                break
            
            lower_line = stripped.lower()
            if "copyright" in lower_line or "(c)" in lower_line:
                self.log(f"Removing copyright line in {relative_path}: {stripped}")
                i += 1
                continue
            
            new_lines.append(line)
            i += 1
            
        try:
            with open(path, "w") as f:
                f.write("".join(new_lines))
        except Exception as e:
            self.log(f"Error writing the file '{path}': {e}")
            return False

        return True
