#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import fnmatch
import sys
import yaml
import logging

from pathlib import Path
from beman_tidy.lib.utils.file import get_repo_ignorable_subdirectories
from beman_tidy.lib.utils.logger_config import setup_logging

setup_logging()

def validate_config(config):
    """
    Validate the repository configuration.
    Ensures mandatory files are not ignored.
    Returns True if valid, False otherwise.
    """
    ignored_paths = config.get("ignored_paths", [])
    if not isinstance(ignored_paths, list):
        logging.error(f"Error: 'ignored_paths' in .beman-tidy.yaml must be a list, but got {type(ignored_paths).__name__}.")
        return False

    mandatory_files = {"README.md", "LICENSE"}

    for path in ignored_paths:
        if not isinstance(path, str):
            logging.error(f"Error: Invalid entry in 'ignored_paths': {path}. Must be a string.")
            return False

        clean_path = path.rstrip("/")
        # Check for exact match
        if clean_path in mandatory_files:
             logging.error(f"Error: Cannot ignore mandatory file '{clean_path}' in .beman-tidy.yaml")
             return False
        
        # Check if ignoring root directory
        if clean_path == "." or clean_path == "":
             logging.error("Error: Cannot ignore root directory in .beman-tidy.yaml")
             return False
             
    if not _validate_ignored_rules(config):
        return False

    return True


def _validate_ignored_rules(config):
    """
    Validate the 'ignored_rules' configuration.
    Returns True if valid, False otherwise.
    """
    ignored_rules = config.get("ignored_rules", [])
    if not ignored_rules:
        return True

    if not isinstance(ignored_rules, list):
        print(f"Error: 'ignored_rules' in .beman-tidy.yaml must be a list, but got {type(ignored_rules).__name__}.")
        return False

    for entry in ignored_rules:
        if not isinstance(entry, str):
            print(f"Error: Invalid entry in 'ignored_rules': {entry}. Must be a string.")
            return False

    return True


def get_ignored_rules(repo_info, known_rule_names):
    """
    Get the expanded set of ignored rule names from the configuration.
    Resolves glob patterns against the known rule names.
    Returns an empty set if no ignored_rules are configured.

    @param repo_info: The repository info dict containing the config.
    @param known_rule_names: A list/set of all known rule names to match against.
    @return: A set of rule names to ignore.
    """
    config = repo_info.get("config", {})
    raw_patterns = config.get("ignored_rules", [])
    if not raw_patterns:
        return set()

    all_matched = set()
    for pattern in raw_patterns:
        if "*" in pattern:
            # Expand glob pattern
            matched = {name for name in known_rule_names if fnmatch.fnmatch(name, pattern)}
            if not matched:
                print(f"{yellow_color}Warning: ignored_rules pattern '{pattern}' does not match any known rule. Skipping.{no_color}")
            else:
                all_matched.update(matched)
        else:
            # Exact match
            if pattern in known_rule_names:
                all_matched.add(pattern)
            else:
                print(f"{yellow_color}Warning: ignored_rules pattern '{pattern}' does not match any known rule. Skipping.{no_color}")

    return all_matched


def is_rule_ignored(rule_name, ignored_rules):
    """
    Check if a specific rule name is in the set of ignored rules.
    """
    return rule_name in ignored_rules


def get_default_config_path():
    """
    Returns the path to the default configuration file.
    """
    return Path(__file__).parent.parent.parent / ".beman-standard.yaml"


def load_repo_config(repo_path, config_path=None):
    """
    Load the configuration file.
    """
    # Load default configuration
    default_config_path = get_default_config_path()
    with default_config_path.open('r') as f:
        default_config = yaml.safe_load(f) or {}

    # Determine user config path
    if config_path:
        user_config_path = Path(config_path)
    else:
        user_config_path = Path(repo_path) / ".beman-tidy.yaml"

    # Load user configuration if it exists
    user_config = {}
    if user_config_path.exists():
        try:
            with open(user_config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
        except Exception as e:
            logging.error(f"Error loading user configuration from '{user_config_path}': {e}")
            sys.exit(1)
    elif config_path:
        logging.error(f"Error: Configuration file specified not found at '{config_path}'")
        sys.exit(1)

    # Merge configurations
    merged_config = default_config.copy()
    merged_config.update(user_config)

    if not validate_config(merged_config):
        sys.exit(1)

    return merged_config


def get_ignores(repo_info):
    """
    Returns a combined list of default system ignores and user-configured ignores.
    """

    default_ignores = get_repo_ignorable_subdirectories()
    user_ignores = repo_info.get("config", {}).get("ignored_paths", [])
    return list(default_ignores) + user_ignores


def is_ignored(repo_info, relative_path):
    """
    Check if a given path is ignored by the configuration.
    A path can be a file or a directory.
    If a directory is ignored, all its children are also ignored.
    """
    ignores = get_ignores(repo_info)
    rel_path_str = relative_path.as_posix()
    for ignore in ignores:
        ignore_str = str(ignore).rstrip('/')

        if rel_path_str == ignore_str:
            return True
        
        if rel_path_str.startswith(ignore_str + '/'):
            return True

    return False
