#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from abc import abstractmethod
from pathlib import Path

from beman_tidy.lib.utils.string import normalize_path_for_display

from .base_check import BaseCheck
from ...utils.config import get_ignores


class DirectoryBaseCheck(BaseCheck):
    """
    Base class for checks that operate on a directory.
    """

    def __init__(self, repo_info, beman_standard_check_config, relative_path):
        super().__init__(repo_info, beman_standard_check_config)
        self.relative_path = Path(relative_path)

        # set path - e.g. "src/beman/exemplar"
        self.path = self.repo_path / relative_path

    def pre_check(self):
        """
        Override.
        Pre-checks if the directory exists and is not empty.
        """
        if not super().pre_check():
            return False

        if self.path is None:
            self.log("The path is not set.")
            return False

        if not self.path.exists():
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(f"The directory '{display_path}' does not exist.")
            return False

        if self.is_empty():
            display_path = normalize_path_for_display(self.path, self.repo_path)
            self.log(f"The directory '{display_path}' is empty.")
            return False

        return True

    def should_skip(self):
        """
        Check if the file should be skipped based on configuration.
        """
        if super().should_skip():
            return True

        ignores = get_ignores(self.repo_info)
        rel_path_str = self.relative_path.as_posix()
        for ignore in ignores:
            ignore_str = str(ignore)
            if rel_path_str == ignore_str:
                return True
            if ignore_str.endswith("/"):
                if rel_path_str.startswith(ignore_str):
                    return True
            elif rel_path_str.startswith(ignore_str + "/"):
                return True

        return False

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

    def read(self) -> list[Path]:
        """
        Read the directory content.
        """
        try:
            return list(self.path.iterdir())
        except Exception:
            return []

    def is_empty(self):
        """
        Check if the directory is empty.
        """
        return len(self.read()) == 0
