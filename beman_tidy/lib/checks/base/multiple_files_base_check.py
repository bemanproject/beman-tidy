#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from abc import abstractmethod
from ...utils.files import get_source_files
from .base_check import BaseCheck


class MultipleFilesBaseCheck(BaseCheck):
    """
    Base class for checks that operate on multiple files.
    It iterates over all source files and runs a specific FileBaseCheck on each.
    """

    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    @abstractmethod
    def create_file_check(self, relative_path):
        """
        Create a FileBaseCheck instance for the given relative path.
        This must be implemented by subclasses.
        """
        pass

    def check(self):
        """
        Runs the actual check on all target files.
        Returns True if all files pass the check.
        """
        source_files = get_source_files(self.repo_path)
        all_passed = True
        for relative_path in source_files:
            file_check = self.create_file_check(relative_path)

            file_check.log_enabled = self.log_enabled
            file_check.log_level = self.log_level
            
            if file_check.should_skip():
                continue
                
            if not file_check.pre_check():
                all_passed = False
                continue

            if not file_check.check():
                all_passed = False
        
        return all_passed

    def fix(self):
        """
        Runs the fix on all source files.
        Returns True if all files are fixed (or were already correct).
        """
        source_files = get_source_files(self.repo_path)
        all_fixed = True
        for relative_path in source_files:
            file_check = self.create_file_check(relative_path)

            file_check.log_enabled = self.log_enabled
            file_check.log_level = self.log_level
            
            if file_check.should_skip():
                continue

            if not file_check.pre_check():
                all_fixed = False
                continue

            if file_check.check():
                continue
                
            if not file_check.fix():
                all_fixed = False
        
        return all_fixed
