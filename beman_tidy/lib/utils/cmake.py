#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import re

from cmake_parser.ast import Command, If


def cmake_is_subdirectory(command, subdir_name):
    if getattr(command, "identifier", None) != "add_subdirectory" or not command.args:
        return False
    arg = command.args[0].value.strip('"')
    return arg == subdir_name or arg.startswith(f"{subdir_name}/")


def cmake_has_unguarded_subdirectory(nodes, subdir_name, option_name, inside_guard=False):
    for item in nodes:
        if isinstance(item, Command):
            if cmake_is_subdirectory(item, subdir_name) and not inside_guard:
                return True
        elif isinstance(item, If):
            guard = bool(item.args and item.args[0].value == option_name)
            if cmake_has_unguarded_subdirectory(
                item.if_true or [], subdir_name, option_name, inside_guard or guard
            ):
                return True
            if cmake_has_unguarded_subdirectory(
                item.if_false or [], subdir_name, option_name, inside_guard
            ):
                return True
    return False


def cmake_build_skip_subdir_option_pattern(option_name):
    return re.compile(
        r"option\s*\(\s*"
        + re.escape(option_name)
        + r'\s*"(?:[^"\\]|\\.)*"\s*'
        + re.escape("${PROJECT_IS_TOP_LEVEL}")
        + r"\s*\)",
    )
