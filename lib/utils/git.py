#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from .terminal import run_command
import markdown
import os
import re
import requests
import sys
import yaml

from git import Repo, InvalidGitRepositoryError


def get_repo_info(path):
    """
    Get information about the repository at the given path.
    Returns data as a dictionary.
    """

    try:
        # Initialize the repository object
        repo = Repo(os.path.abspath(path), search_parent_directories=True)

        # Get the top-level directory of the repository
        top_level_dir = repo.git.rev_parse("--show-toplevel")

        # Get the repository name (directory name of the top level)
        repo_name = os.path.basename(top_level_dir)

        # Get the remote URL (assuming 'origin' is the remote name)
        remote_url = None
        if "origin" in repo.remotes:
            remote_url = repo.remotes.origin.url

        # Get the current branch
        current_branch = repo.active_branch.name

        # Get the commit hash
        commit_hash = repo.head.commit.hexsha

        # Get the status of the repository
        status = repo.git.status()

        # Get unstaged changes
        unstaged_changes = repo.git.diff("--stat")

        return {
            "top_level": top_level_dir,
            "name": repo_name,
            "remote_url": remote_url,
            "current_branch": current_branch,
            "commit_hash": commit_hash,
            "status": status,
            "unstaged_changes": unstaged_changes,
        }
    except InvalidGitRepositoryError:
        print(f"The path '{path}' is not inside a valid Git repository.")
        sys.exit(1)
    except Exception as e:
        print(
            f"An error occurred while getting repository information. Check {path}.")
        sys.exit(1)

def load_beman_standard_config(path):
    """
    Load the Beman Standard YAML configuration file from the given path.
    """
    with open(path, "r") as file:
        beman_standard_yml = yaml.safe_load(file)

    beman_standard_check_config = {}
    for check_name in beman_standard_yml:
        check_config = {
            "name": check_name,
            "full_text_body": "",
            "type": "",
            "regex": "",
            "file_name": "",
            "directory_name": "",
            "badge_lines": "",
            "status_lines": "",
            "licenses": "",
            "default_group": "",
        }
        for entry in beman_standard_yml[check_name]:
            if "type" in entry:
                check_config["type"] = entry["type"]
            elif "regex" in entry:
                # TODO: Implement the regex check.
                pass
            elif "file_name" in entry:
                check_config["file_name"] = entry["file_name"]
            elif "directory_name" in entry:
                check_config["directory_name"] = entry["directory_name"]
            elif "badge_lines" in entry:
                # TODO: Implement the badge check.
                pass
            elif "status_lines" in entry:
                # TODO: Implement the status check.
                pass
            elif "licenses" in entry:
                # TODO: Implement the license check.
                pass
            elif "default_group" in entry:
                check_config["default_group"] = entry["default_group"]
            else:
                raise ValueError(f"Invalid entry in Beman Standard YAML: {entry}")

        beman_standard_check_config[check_name] = check_config

    return beman_standard_check_config
