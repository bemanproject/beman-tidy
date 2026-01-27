#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.multiple_files_base_check import MultipleFilesBaseCheck
from ..base.file_base_check import FileBaseCheck
from ..system.registry import register_beman_standard_check

# [file.*] checks category.
# All checks in this file extend the BaseCheck class.


# TODO file.names


# TODO file.test_names


# TODO file.license_id


@register_beman_standard_check("internal.file.copyright.impl")
class FileCopyrightCheckImpl(FileBaseCheck):
    """
    Implementation of the file.copyright check for a single file.
    """
    def __init__(self, repo_info, beman_standard_check_config, relative_path):

        super().__init__(repo_info, beman_standard_check_config, relative_path)
        self.name = "file.copyright" #for logging

    def check(self):
        try:
            lines = self.read_lines()
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
                self.log(f"Copyright notice found in {self.path.name} at line {i+1}. It should be removed.")
                return False
                
        return True

    def fix(self):
        try:
            lines = self.read_lines()
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
                self.log(f"Removing copyright line in {self.path.name}: {stripped}")
                i += 1
                continue
            
            new_lines.append(line)
            i += 1
            
        self.write_lines(new_lines)
        return True


@register_beman_standard_check("file.copyright")
class FileCopyrightCheck(MultipleFilesBaseCheck):
    """
    [file.copyright]
    Recommendation: Source code files should NOT include a copyright notice following the SPDX license identifier.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.beman_standard_check_config = beman_standard_check_config

    def create_file_check(self, relative_path):
        return FileCopyrightCheckImpl(self.repo_info, self.beman_standard_check_config, relative_path)
