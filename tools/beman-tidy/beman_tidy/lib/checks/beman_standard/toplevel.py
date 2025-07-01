#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
import pathlib

from ..base.file_base_check import FileBaseCheck
from .cmake import CMakeBaseCheck
from ..system.registry import register_beman_standard_check


# [TOPLEVEL.*] checks category.
# All checks in this file extend the ToplevelBaseCheck class.
#
# Note: ToplevelBaseCheck is not a registered check!


@register_beman_standard_check(check="TOPLEVEL.CMAKE")
class ToplevelCmakeCheck(CMakeBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        return super().pre_check()

    def fix(self):
        # TODO: Implement the fix.
        pass


# TODO TOPLEVEL.LICENSE - use FileBaseCheck


@register_beman_standard_check("TOPLEVEL.LICENSE")
class TopLevelLicenseCheck(FileBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "LICENSE")

    def check(self):
        return super().pre_check()

    def fix(self):
        license_path = pathlib.Path(__file__).parent.resolve() / "files/LICENSE.txt"
        with license_path.open("r") as src:
            content = src.read()
        target_path = self.path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w") as file:
            file.write(content)
        return True


# TODO TOPLEVEL.README - use ReadmeBaseCheck
