#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import re
from beman_tidy.lib.checks.base.base_check import BaseCheck
from beman_tidy.lib.checks.base.file_base_check import FileBaseCheck, BatchFileBaseCheck
from beman_tidy.lib.checks.system.registry import register_beman_standard_check
from beman_tidy.lib.utils.file import get_beman_include_headers

@register_beman_standard_check("cpp.namespace")
class CppNamespaceCheck(BatchFileBaseCheck):
    """
    [cpp.namespace]
    Recommendation: Headers in include/beman/<short_name>/ should export entities in the beman::<short_name> namespace.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.file_check_class = self.CppNamespaceCheckImpl
        self.file_path_generator = get_beman_include_headers

    class CppNamespaceCheckImpl(FileBaseCheck):
        """
        Implementation of the "cpp.namespace" check for a single file.
        """
        def __init__(self, repo_info, beman_standard_check_config, relative_path):
            super().__init__(repo_info, beman_standard_check_config, relative_path, name="cpp.namespace")
            self.short_name = ""

        def _get_code_body_indices(self, lines):
            """
            Finds the start and end indices of the main code body, excluding headers and footers.
            """
            start_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('#include', '#define')):
                    start_index = i + 1
            
            end_index = len(lines)
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith('#endif'):
                    end_index = i
                    break
            return start_index, end_index

        def check(self):
            parts = self.path.parts
            include_index = parts.index('include')
            self.short_name = parts[include_index + 2]
            lines = self.read_lines()
            
            code_start_index, code_end_index = self._get_code_body_indices(lines)
            
            has_actual_code = False
            for i in range(code_start_index, code_end_index):
                line = lines[i].strip()
                if line and not line.startswith('//') and not line.startswith('#'):
                    has_actual_code = True
                    break
            
            if not has_actual_code:
                return True

            # Pattern to match either "namespace beman::my_lib" or "namespace beman { ... namespace my_lib"
            pattern = re.compile(
                r"namespace\s+beman\s*::\s*" + re.escape(self.short_name) +
                r"|namespace\s+beman\s*\{\s*\n\s*namespace\s+" + re.escape(self.short_name)
            )

            content = "".join(lines)
            if not pattern.search(content):
                self.log(f"File does not contain the expected namespace 'beman::{self.short_name}'.")
                return False

            return True

        def fix(self):
            parts = self.path.parts
            include_index = parts.index('include')
            self.short_name = parts[include_index + 2]
            lines = self.read_lines()
            
            insert_line, close_line = self._get_code_body_indices(lines)
                    
            new_lines = lines[:insert_line]
            # blank line for style
            if insert_line > 0 and lines[insert_line-1].strip():
                 new_lines.append("")
            
            new_lines.append(f"namespace beman::{self.short_name} {{")
            new_lines.extend(lines[insert_line:close_line])
            new_lines.append(f"}} // namespace beman::{self.short_name}")
            
            # blank line for style
            if close_line < len(lines) and lines[close_line].strip():
                 new_lines.append("")

            new_lines.extend(lines[close_line:])

            self.write_lines(new_lines)
            return True


# TODO cpp.no_flag_forking

@register_beman_standard_check("cpp.extension_identifiers")
class CppExtensionIdentifiersCheck(BaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def should_skip(self):
        self.log(
            "beman-tidy cannot actually check cpp.extension_identifiers. Please ensure that extension identifiers are prefixed with 'ext_'. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#cppextensionidentifiers for more information."
        )
        return True
