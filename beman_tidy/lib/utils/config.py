#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys
import yaml
from pathlib import Path
from beman_tidy.lib.utils.file import get_repo_ignorable_subdirectories


def validate_config(config):
    """
    Validate the repository configuration.
    Ensures mandatory files are not ignored.
    Returns True if valid, False otherwise.
    """
    ignored_paths = config.get("ignored_paths", [])
    if not ignored_paths:
        return True

    if not isinstance(ignored_paths, list):
        print(f"Error: 'ignored_paths' in .beman-tidy.yml must be a list, but got {type(ignored_paths).__name__}.")
        return False

    mandatory_files = {"README.md", "LICENSE"}

    for path in ignored_paths:
        if not isinstance(path, str):
            print(f"Error: Invalid entry in 'ignored_paths': {path}. Must be a string.")
            return False

        clean_path = path.rstrip("/")
        # Check for exact match
        if clean_path in mandatory_files:
             print(f"Error: Cannot ignore mandatory file '{clean_path}' in .beman-tidy.yml")
             return False
        
        # Check if ignoring root directory
        if clean_path == "." or clean_path == "":
             print("Error: Cannot ignore root directory in .beman-tidy.yml")
             return False
             
    return True


def load_repo_config(repo_path, config_path=None):
    """
    Load the configuration file.
    """
    if config_path:
        target_path = Path(config_path)
    else:
        target_path = Path(repo_path) / ".beman-tidy.yml" # default name

    if not target_path.exists():
        if config_path:
            print(f"Error: Configuration file specified not found at '{config_path}'")
            sys.exit(1)
        return {}

    try:
        with open(target_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration from '{target_path}': {e}")
        sys.exit(1)

    if config is None:
        return {}

    if not validate_config(config):
        sys.exit(1)

    return config


def get_ignores(repo_info):
    """
    Returns a combined list of default system ignores and user-configured ignores.
    """

    default_ignores = get_repo_ignorable_subdirectories()
    user_ignores = repo_info.get("config", {}).get("ignored_paths", [])
    return list(default_ignores) + user_ignores
