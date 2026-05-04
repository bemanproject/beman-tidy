#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from ..base.file_base_check import FileBaseCheck, BatchFileBaseCheck
from ..system.registry import register_beman_standard_check
from ...utils.file import get_cpp_files, get_spdx_info, get_commentable_files
from ...utils.string import normalize_path_for_display
from ...utils.comments import find_in_comment, CommentType, BLOCK_ENDS, BLOCK_STARTS, LINE_PREFIXES

# [file.*] checks category.
# All checks in this file extend the BaseCheck class.


@register_beman_standard_check("file.names")
class FileNamesCheck(BatchFileBaseCheck):
    """
    [file.names]
    Recommendation: File names must be lowercase and use snake_case.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.file_check_class = self.FileNamesCheckImpl
        self.file_path_generator = get_cpp_files

    class FileNamesCheckImpl(FileBaseCheck):
        """
        Implementation of the "file.names" check for a single file.
        """

        def __init__(self, repo_info, beman_standard_check_config, relative_path):
            super().__init__(
                repo_info, beman_standard_check_config, relative_path, name="file.names"
            )

        def check(self):
            filename_stem = self.path.stem

            # lowercase and snake_case
            is_valid = filename_stem == filename_stem.lower() and all(
                c.isalnum() or c == "_" for c in filename_stem
            )

            if not is_valid:
                display_path = normalize_path_for_display(self.path, self.repo_path)
                self.log(
                    f"File name {display_path} does not follow the snake_case naming convention. "
                    f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#filenames"
                )
                return False
            return True

        def fix(self):
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(
                f"Please manually rename {display_path} to follow the snake_case naming convention."
            )
            return False


# TODO file.test_names


@register_beman_standard_check("file.license_id")
class FileLicenseIdCheck(BatchFileBaseCheck):
    """
    [file.license_id]
    Requirement: The SPDX license identifier must be added at the first possible line
    in all files which can contain a comment (C++, CMake, Python, shell, YAML, etc.).
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.file_check_class = self.FileLicenseIdCheckImpl
        self.file_path_generator = get_commentable_files

    class FileLicenseIdCheckImpl(FileBaseCheck):
        """
        Implementation of the "file.license_id" check for a single file.
        """

        def __init__(self, repo_info, beman_standard_check_config, relative_path):
            super().__init__(repo_info, beman_standard_check_config, relative_path, name="file.license_id")

        def _expected_spdx_line_index(self, lines):
            """
            Returns the expected line index for the SPDX identifier.
            If the first line is a shebang (#!), SPDX goes on line 1; otherwise line 0.
            """
            if lines and lines[0].startswith("#!"):
                return 1
            return 0

        def check(self):
            lines = self.read_lines()
            spdx_index, _ = get_spdx_info(lines)
            display_path = normalize_path_for_display(self.path, self.repo_path)

            if spdx_index == -1:
                self.log(
                    f"Missing SPDX-License-Identifier in {display_path}. "
                    f"Please add it at the first line. "
                    f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#filelicense_id"
                )
                return False

            expected = self._expected_spdx_line_index(lines)
            if spdx_index != expected:
                self.log(
                    f"SPDX-License-Identifier must be at line {expected + 1} in {display_path}, "
                    f"but found at line {spdx_index + 1}. "
                    f"See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#filelicense_id"
                )
                return False

            return True

        def fix(self):
            lines = self.read_lines()
            spdx_index, _ = get_spdx_info(lines)
            display_path = normalize_path_for_display(self.path, self.repo_path)

            if spdx_index == -1:
                self.log(
                    f"Cannot auto-fix {display_path}: SPDX-License-Identifier is missing. "
                    f"Please add it manually."
                )
                return False

            expected = self._expected_spdx_line_index(lines)
            if spdx_index == expected:
                return True  # Already correct

            # Move the SPDX line to the expected position
            spdx_line = lines.pop(spdx_index)
            lines.insert(expected, spdx_line)
            self.write("".join(lines))
            return True


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

        def _get_copyright_search_start_info(self, lines):
            """
            Finds the starting point for searching for copyright notices.
            This is the comment block immediately following the SPDX identifier.
            Returns (start_index, comment_type) or (None, None) if no further processing is needed.
            """
            spdx_index, comment_type = get_spdx_info(lines)
            if not self._has_valid_spdx(spdx_index, comment_type):
                return None, None

            start_index = spdx_index + 1
            search_comment_type = comment_type
            if self._is_single_line_block_comment(lines, spdx_index, comment_type):
                next_index, next_comment_type = self._find_next_comment_start(lines, spdx_index + 1)
                if next_index != -1:
                    start_index = next_index
                    search_comment_type = next_comment_type
                else:
                    return None, None

            return start_index, search_comment_type

        def check(self):
            lines = self.read_lines()
            start_search_index, search_comment_type = self._get_copyright_search_start_info(lines)
            if start_search_index is None:
                return True

            # Start searching from the line after SPDX identifier
            line_index, found_text = find_in_comment(lines, start_search_index, search_comment_type, ["copyright", "(c)"], ignore_case=True)

            if line_index is not None:
                self.log(f"Copyright notice found in {self.path.name} at line {line_index+1}. It should be removed.")
                return False

            return True

        def fix(self):
            lines = self.read_lines()
            start_fix_index, fix_comment_type = self._get_copyright_search_start_info(lines)
            if start_fix_index is None:
                return True

            # Start removing from the line after SPDX identifier
            new_lines = self._remove_lines_with_text_in_comment(
                lines,
                start_fix_index,
                fix_comment_type,
                ["copyright", "(c)"],
                log_func=lambda msg: self.log(f"{msg} in {self.path.name}")
            )

            self.write("".join(new_lines))
            return True

        def _has_valid_spdx(self, spdx_index, comment_type):
            return spdx_index != -1 and comment_type is not None

        def _is_single_line_block_comment(self, lines, spdx_index, comment_info):
            if comment_info == CommentType.BLOCK:
                if any(end in lines[spdx_index] for end in BLOCK_ENDS):
                    return True
            return False

        def _find_next_comment_start(self, lines, start_index):
            for i in range(start_index, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                if any(line.startswith(prefix) for prefix in LINE_PREFIXES):
                    return i, CommentType.LINE
                
                if any(line.startswith(start) for start in BLOCK_STARTS):
                    return i, CommentType.BLOCK
                
                # Found non-comment code
                return -1, None
            
            return -1, None

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
                processed_lines, next_index = self._process_line_comments(lines, start_index, texts, log_func)
                new_lines.extend(processed_lines)
                new_lines.extend(lines[next_index:])
            elif comment_type == CommentType.BLOCK:
                processed_lines, next_index = self._process_block_comments(lines, start_index, texts, log_func)
                new_lines.extend(processed_lines)
                new_lines.extend(lines[next_index:])
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
                    if new_line is not None:
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
                 start_index = pre.find(block_start)
                 
                 # Check if we can remove the line entirely
                 if not pre[:start_index].strip() and not post.strip():
                     return None

                 new_line_content += pre[:start_index + len(block_start)] + " "
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
