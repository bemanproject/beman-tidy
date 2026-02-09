#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path


def get_repo_ignorable_subdirectories():
    """
    Returns a set of common build and IDE directories to ignore.
    """
    return {".git", "build", ".idea", ".vscode", "__pycache__", "venv", "env"}


def get_matched_paths(repo_path, extensions, exclude_dirs=None):
    """
    Get all files in the repository matching the given extensions.
    Ignores directories specified in exclude_dirs.
    """
    if exclude_dirs is None:
        exclude_dirs = get_repo_ignorable_subdirectories()

    matched_files = []
    repo_path = Path(repo_path)

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        try:
            relative_path = path.relative_to(repo_path)
        except ValueError:
            continue

        # Check if any part of the relative path is in exclude_dirs
        if any(part in exclude_dirs for part in relative_path.parts):
            continue

        # Found match.
        if path.suffix in extensions:
            matched_files.append(relative_path)

    return sorted(list(set(matched_files)))


def get_cpp_files(repo_path):
    """
    Get all C++ files in the repository.
    Currently considers C++ source and header files.
    Ignores common build and IDE directories.
    """
    cpp_extensions = {".hpp", ".h", ".hxx", ".hh", ".cpp", ".cxx", ".cc", ".c"}
    return get_matched_paths(repo_path, cpp_extensions)
