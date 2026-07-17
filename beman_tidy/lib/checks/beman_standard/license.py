#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from abc import ABC

from ..base.base_check import BaseCheck
from ..base.file_base_check import FileBaseCheck
from ..system.registry import register_beman_standard_check
from beman_tidy.lib.utils.git import get_beman_recommended_license_path
from beman_tidy.lib.utils.string import (
    match_apache_license_v2_with_llvm_exceptions,
    match_boost_software_license_v1_0
)

# [license.*] checks category.
# All checks in this file extend the LicenseBaseCheck class.
#
# Note: LicenseBaseCheck is not a registered check!


class LicenseBaseCheck(FileBaseCheck, ABC):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config, "LICENSE")


@register_beman_standard_check("license.approved")
class LicenseApprovedCheck(LicenseBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        content = self.read()

        if match_apache_license_v2_with_llvm_exceptions(content):
            self.log(
                "Valid Apache License - Version 2.0 with LLVM Exceptions found in LICENSE file.",
                log_level="info",
            )
            return True

        if match_boost_software_license_v1_0(content):
            self.log(
                "Valid Boost Software License - Version 1.0 found in LICENSE file.",
                log_level="info",
            )
            return True

        self.log(
            "Invalid license - cannot find approved license in LICENSE file. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licenseapproved for more information."
        )
        return False

    def fix(self):
        self.log(
            "Please update the LICENSE file to include an approved license. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licenseapproved for more information."
        )


@register_beman_standard_check("license.apache_llvm")
class LicenseApacheLLVMCheck(LicenseBaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def check(self):
        # Compare LICENSE file stored at self.path with the reference one.
        target_content = self.read().splitlines()
        ref_content = get_beman_recommended_license_path().read_text(encoding="utf-8").splitlines()

        if target_content != ref_content:
            self.log(
                "Please update the LICENSE file to include the Apache License v2.0 with LLVM Exceptions. "
                "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licenseapache_llvm for more information."
            )
            return False

        return True

    def fix(self):
        self.log(
            "Please update the LICENSE file to include the Apache License v2.0 with LLVM Exceptions. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licenseapache_llvm for more information."
        )


@register_beman_standard_check("license.criteria")
class LicenseCriteriaCheck(BaseCheck):
    def __init__(self, repo_info, beman_standard_check_config):
        super().__init__(repo_info, beman_standard_check_config)

    def should_skip(self):
        # Cannot actually implement license.criteria, so skip it.
        # No need to run pre_check() and check() as well, as they are not implemented.
        self.log(
            "Skipping license.criteria: beman-tidy cannot reliably automate this policy-level review. "
            "Please manually verify that your project license and usage satisfy the license.criteria requirements; "
            "note that license.approved only checks for an approved LICENSE text and does not prove full criteria compliance. "
            "See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licensecriteria for guidance."
        )
        return True
