#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys
import yaml
from pathlib import Path
from importlib.resources import files
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
    # Load default configuration
    default_config_path = files('beman_tidy').joinpath('.beman-tidy.yml')
    with default_config_path.open('r') as f:
        default_config = yaml.safe_load(f) or {}

    # Determine user config path
    if config_path:
        user_config_path = Path(config_path)
    else:
        user_config_path = Path(repo_path) / ".beman-tidy.yml"

    # Load user configuration if it exists
    user_config = {}
    if user_config_path.exists():
        try:
            with open(user_config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading user configuration from '{user_config_path}': {e}")
            sys.exit(1)
    elif config_path:
        print(f"Error: Configuration file specified not found at '{config_path}'")
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
