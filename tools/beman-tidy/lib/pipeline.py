#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys

from .checks.system.registry import get_registered_beman_standard_checks
from .checks.system.git import DisallowFixInplaceAndUnstagedChangesCheck

# Import all the implemented checks.
# from .checks.beman_standard.cmake import
# from .checks.beman_standard.cpp import
# from .checks.beman_standard.directory import
# from .checks.beman_standard.file import
# from .checks.beman_standard.general import
# from .checks.beman_standard.license import
from .checks.beman_standard.readme import ReadmeTitleCheck, ReadmeBadgesCheck, ReadmeLibraryStatusCheck
# from .checks.beman_standard.release import
# from .checks.beman_standard.toplevel import

red_color = "\033[91m"
green_color = "\033[92m"
yellow_color = "\033[93m"
gray_color = "\033[90m"
no_color = "\033[0m"


def run_checks_pipeline(checks_to_run, args, beman_standard_check_config):
    """
    Run the checks pipeline for The Beman Standard.
    Read-only checks if args.fix_inplace is False, otherwise try to fix the issues in-place.
    Verbosity is controlled by args.verbose.

    @return: The number of failed checks.
    """

    """
    Helper function to log messages.
    """
    def log(msg):
        if args.verbose:
            print(msg)

    """
    Helper function to run a check.
    @param check_class: The check class type to run.
    @param log_enabled: Whether to log the check result.
    @return: True if the check passed, False otherwise.
    """
    def run_check(check_class, log_enabled=args.verbose):
        check_instance = check_class(
            args.repo_info, beman_standard_check_config)
        check_instance.log_enabled = log_enabled

        log(
            f"Running check [{check_instance.type}][{check_instance.name}] ... ")

        if (check_instance.pre_check() and check_instance.check()) or (args.fix_inplace and check_instance.fix()):
            log(f"\tcheck [{check_instance.type}][{check_instance.name}] ... {green_color}PASSED{no_color}\n")
            return True
        else:
            log(f"\tcheck [{check_instance.type}][{check_instance.name}] ... {red_color}FAILED{no_color}\n")
            return False

    """
    Main pipeline.
    """
    def run_pipeline_helper():
        # Internal checks
        if args.fix_inplace:
            run_check(DisallowFixInplaceAndUnstagedChangesCheck,
                      log_enabled=False)

        implemented_checks = get_registered_beman_standard_checks()
        cnt_all_beman_standard_checks = len(beman_standard_check_config)
        cnt_implemented_checks = len(implemented_checks)
        cnt_passed = 0
        cnt_failed = 0
        cnt_skipped = cnt_all_beman_standard_checks - cnt_implemented_checks
        for check_name in checks_to_run:
            if not check_name in implemented_checks:
                continue

            if run_check(implemented_checks[check_name]):
                cnt_passed += 1
            else:
                cnt_failed += 1

        return cnt_passed, cnt_failed, cnt_skipped, cnt_implemented_checks, cnt_all_beman_standard_checks

    log("beman-tidy pipeline started ...\n")
    cnt_passed, cnt_failed, cnt_skipped, cnt_implemented_checks, cnt_all_beman_standard_checks = run_pipeline_helper()
    log("\nbeman-tidy pipeline finished.\n")

    # Always print the summary.
    print(f"Summary: {green_color} {cnt_passed} checks PASSED{no_color}, {red_color}{cnt_failed} checks FAILED{no_color}, {gray_color}{cnt_skipped} skipped (NOT implemented).{no_color}")

    # Always print the coverage.
    coverage = round(cnt_passed / cnt_implemented_checks * 100, 2)
    print(
        f"\n{yellow_color}Coverage: {coverage}% ({cnt_passed}/{cnt_implemented_checks} checks passed).{no_color}")

    sys.stdout.flush()

    return cnt_failed
