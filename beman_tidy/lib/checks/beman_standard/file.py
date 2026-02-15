#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.file_base_check import FileBaseCheck, BatchFileBaseCheck
from ..system.registry import register_beman_standard_check
from ...utils.file import get_cpp_files, get_spdx_info
from ...utils.comments import find_in_comment, CommentType, BLOCK_ENDS, BLOCK_STARTS, LINE_PREFIXES

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
            spdx_index, comment_info = get_spdx_info(lines)

            if spdx_index == -1:
                return True
            
            if comment_info is None:
                return True

            # Start searching from the line after SPDX identifier
            line_idx, found_text = find_in_comment(lines, spdx_index + 1, comment_info, ["copyright", "(c)"], ignore_case=True)
            
            if line_idx is not None:
                self.log(f"Copyright notice found in {self.path.name} at line {line_idx+1}. It should be removed.")
                return False

            return True

        def fix(self):
            lines = self.read_lines()
            spdx_index, comment_info = get_spdx_info(lines)

            if spdx_index == -1 or comment_info is None:
                return True

            # Start removing from the line after SPDX identifier
            new_lines = self._remove_lines_with_text_in_comment(
                lines, 
                spdx_index + 1,
                comment_info, 
                ["copyright", "(c)"], 
                log_func=lambda msg: self.log(f"{msg} in {self.path.name}")
            )

            self.write("".join(new_lines))
            return True

        def _remove_lines_with_text_in_comment(self, lines, start_index, comment_type, texts, log_func=None):
            """
            Removes lines from the comment block that contain any of the texts.
            Preserves block comment structure.
            Returns the new list of lines.
            """
            if start_index < 0 or start_index >= len(lines) or comment_type is None:
                return lines

            new_lines = lines[:start_index]
            
            if comment_type == CommentType.LINE:
                processed_lines, next_idx = self._process_line_comments(lines, start_index, texts, log_func)
                new_lines.extend(processed_lines)
                new_lines.extend(lines[next_idx:])
            elif comment_type == CommentType.BLOCK:
                processed_lines, next_idx = self._process_block_comments(lines, start_index, texts, log_func)
                new_lines.extend(processed_lines)
                new_lines.extend(lines[next_idx:])
            else:
                new_lines.extend(lines[start_index:])
            
            return new_lines

        def _process_line_comments(self, lines, start_index, texts, log_func):
            processed_lines = []
            i = start_index
            
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                if not stripped:
                    processed_lines.append(line)
                    i += 1
                    continue
                    
                if not any(stripped.startswith(prefix) for prefix in LINE_PREFIXES):
                    break
                
                if self._contains_text(stripped, texts):
                    if log_func:
                        log_func(f"Removing line: {stripped}")
                    i += 1
                    continue
                
                processed_lines.append(line)
                i += 1
            
            return processed_lines, i

        def _process_block_comments(self, lines, start_index, texts, log_func):
            processed_lines = []
            i = start_index
            
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                block_end = None
                for end in BLOCK_ENDS:
                    if end in line:
                        block_end = end
                        break
                
                if block_end:
                    new_line = self._handle_block_end_line(line, texts, block_end, log_func)
                    processed_lines.append(new_line)
                    i += 1
                    break
                
                # Normal block line
                if self._contains_text(stripped, texts):
                    if log_func:
                        log_func(f"Removing line: {stripped}")
                    i += 1
                    continue
                    
                processed_lines.append(line)
                i += 1
                
            return processed_lines, i

        def _handle_block_end_line(self, line, texts, block_end, log_func):
            pre, sep, post = line.partition(block_end)
            lower_pre = pre.lower()
            
            found_text = None
            for text in texts:
                if text.lower() in lower_pre:
                    found_text = text
                    break
            
            if found_text:
                if log_func:
                    log_func(f"Removing line content: {line.strip()}")
                return self._reconstruct_block_end_line(pre, sep, post)
            
            return line

        def _reconstruct_block_end_line(self, pre, sep, post):
            new_line_content = ""
            
            block_start = None
            for start in BLOCK_STARTS:
                if start in pre:
                    block_start = start
                    break
            
            if block_start:
                 start_idx = pre.find(block_start)
                 new_line_content += pre[:start_idx + len(block_start)] + " "
            else:
                 stripped_pre = pre.strip()
                 if stripped_pre.startswith("*"):
                     indent = pre[:pre.find("*")+1]
                     new_line_content += indent + " "
                 else:
                     new_line_content += pre[:len(pre)-len(pre.lstrip())]
            
            new_line_content += sep + post
            return new_line_content

        def _contains_text(self, line, texts):
            lower_line = line.lower()
            for text in texts:
                if text.lower() in lower_line:
                    return True
            return False
