#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from abc import abstractmethod
import re

from beman_tidy.lib.utils.string import normalize_path_for_display

from .base_check import BaseCheck

class FileBaseCheck(BaseCheck):
    """
    Base class for checks that operate on a file.
    """

    def __init__(self, repo_info, beman_standard_check_config, relative_path, name=None):
        super().__init__(repo_info, beman_standard_check_config, name=name)

        # set path - e.g. "README.md"
        self.path = self.repo_path / relative_path

    def pre_check(self):
        """
        Override.
        Pre-checks if the file exists and is not empty.
        """
        if not super().pre_check():
            return False

        if self.path is None:
            self.log("The path is not set.")
            return False

        if not self.path.exists():
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(f"The file '{display_path}' does not exist.")
            return False

        if self.is_empty():
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(f"The file '{display_path}' is empty.")
            return False

        return True

    @abstractmethod
    def check(self):
        """
        Override this method, make it abstract because this is style an abstract class.
        """
        pass

    @abstractmethod
    def fix(self):
        """
        Override this method, make it abstract because this is style an abstract class.
        """
        pass

    def read(self):
        """
        Read the file content.
        """
        try:
            with open(self.path, "r") as file:
                return file.read()
        except Exception:
            return ""

    def read_lines(self):
        """
        Read the file content as lines.
        """
        try:
            with open(self.path, "r") as file:
                return file.readlines()
        except Exception:
            return []

    def read_lines_strip(self):
        """
        Read the file content as lines and strip them.
        """
        return [line.strip() for line in self.read_lines()]

    def write(self, content):
        """
        Write the content to the file.
        """
        try:
            with open(self.path, "w") as file:
                file.write(content)
        except Exception as e:
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(f"Error writing the file '{display_path}': {e}")

    def write_lines(self, lines):
        """
        Write the lines to the file.
        """
        self.write("\n".join(lines))

    def replace_line(self, line_number, new_line):
        """
        Replace the line at the given line number with the new line.
        """
        lines = self.read_lines()
        lines[line_number] = new_line
        self.write_lines(lines)

    def is_empty(self):
        """
        Check if the file is empty.
        """
        return len(self.read()) == 0

    def has_content(self, content_to_match):
        """
        Check if the file contains the given content (literal string match).
        """
        readme_content = self.read()
        if not readme_content or len(readme_content) == 0:
            return False
        return re.search(re.escape(content_to_match), readme_content) is not None


class BatchFileBaseCheck(BaseCheck):
    """
    Base class for checks that operate on multiple files.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)
        self.beman_standard_check_config = beman_standard_check_config
        self.file_check_class = None
        self.file_path_generator = None

    def _validate(self):
        """
        Validates that the subclass has set the required attributes.
        """
        if self.file_check_class is None:
            raise NotImplementedError("Subclasses must set self.file_check_class")
        if self.file_path_generator is None:
            raise NotImplementedError("Subclasses must set self.file_path_generator")

    def _create_and_init_file_check(self, relative_path):
        """
        Helper to create and initialize a file check instance.
        Returns
            the instance, if it should run,
            None, if it should be skipped, or
            False, if it failed pre_check.
        """
        file_check = self.file_check_class(self.repo_info, self.beman_standard_check_config, relative_path)
        file_check.name = self.name

        file_check.log_enabled = self.log_enabled
        file_check.log_level = self.log_level
        
        if file_check.should_skip():
            return None
            
        if not file_check.pre_check():
            return False

        return file_check

    def _run_batch_operation(self, operation_callback):
        """
        Runs a batch operation on all files.
        @param operation_callback: A function that takes a file_check instance and returns True if successful.
        @return: True if all operations were successful.
        """
        self._validate()

        source_files = self.file_path_generator(self.repo_path)
        all_successful = True
        
        for relative_path in source_files:
            file_check = self._create_and_init_file_check(relative_path)

            if file_check is None:
                continue
            if file_check is False:
                all_successful = False
                continue
            if not operation_callback(file_check):
                all_successful = False
        
        return all_successful

    def check(self):
        """
        Runs the actual check on all target files.
        Returns True if all files pass the check.
        """
        return self._run_batch_operation(lambda fc: fc.check())

    def fix(self):
        """
        Runs the fix on all source files.
        Returns True if all files are fixed (or were already correct).
        """
        # If check passes, it's good. If not, try fix.
        return self._run_batch_operation(lambda fc: fc.check() or fc.fix())
