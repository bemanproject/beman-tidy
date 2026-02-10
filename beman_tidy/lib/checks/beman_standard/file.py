#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.file_base_check import FileBaseCheck, BatchFileBaseCheck
from ..system.registry import register_beman_standard_check
from ...utils.file import get_cpp_files, get_spdx_info

# [file.*] checks category.
# All checks in this file extend the BaseCheck class.


# TODO file.names


# TODO file.test_names


# TODO file.license_id


@register_beman_standard_check("file.copyright")
class FileCopyrightCheck(BatchFileBaseCheck):
    """
    [file.copyright]
    Recommendation: Source code files should NOT include a copyright notice following the SPDX license identifier.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.file_check_class = self.FileCopyrightCheckImpl
        self.file_path_generator = get_cpp_files

    class FileCopyrightCheckImpl(FileBaseCheck):
        """
        Implementation the "file.copyright" check for a single file.
        """
        def __init__(self, repo_info, beman_standard_check_config, relative_path):
            super().__init__(repo_info, beman_standard_check_config, relative_path, name="file.copyright")

        def check(self):
            lines = self.read_lines()
            spdx_index, comment_prefix = get_spdx_info(lines)

            if spdx_index == -1:
                return True
            
            if comment_prefix is None:
                # TODO: Support block comments (e.g. Markdown <!-- ... --> or C++ /* ... */)
                return True

            for i in range(spdx_index + 1, len(lines)):
                line = lines[i].strip()
                
                # Allows empty lines
                if not line:
                    continue
                    
                # If it doesn't start with comment prefix, assumes end of header comments
                if not line.startswith(comment_prefix):
                    break
                
                lower_line = line.lower()
                if "copyright" in lower_line or "(c)" in lower_line:
                    self.log(f"Copyright notice found in {self.path.name} at line {i+1}. It should be removed.")
                    return False
                    
            return True

        def fix(self):
            lines = self.read_lines()
            spdx_index, comment_prefix = get_spdx_info(lines)

            if spdx_index == -1 or comment_prefix is None:
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
