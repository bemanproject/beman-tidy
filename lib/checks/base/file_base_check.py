#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from .base_check import BaseCheck
import os
import sys


class FileBaseCheck(BaseCheck):
    """
    Base class for checks that operate on a file.
    """

    def __init__(self, repo_info, beman_standard_check_config, relative_path):
        super().__init__(repo_info, beman_standard_check_config)

        # set path - e.g. "README.md"
        self.path = os.path.join(repo_info["top_level"], relative_path)

    def default_check(self):
        """
        Checks if this rule is properly initialized.
        """
        if not super().default_check():
            return False

        if self.path is None:
            self.log("The path is not set.")
            return False

        if not os.path.exists(self.path):
            self.log(f"The file '{self.path}' does not exist.")
            return False

        if len(self.read_lines()) == 0:
            self.log(f"The file '{self.path}' is empty.")
            return False

        return True

    def read(self):
        """
        Read the file content.
        """
        try:
            with open(self.path, 'r') as file:
                return file.read()
        except Exception as e:
            return ""

    def read_lines(self):
        """
        Read the file content as lines.
        """
        try:
            with open(self.path, 'r') as file:
                return file.readlines()
        except Exception as e:
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
            with open(self.path, 'w') as file:
                file.write(content)
        except Exception as e:
            self.log(f"Error writing the file '{self.path}': {e}")

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
