#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path


def get_repo_ignorable_subdirectories():
    """
    Returns a set of common build and IDE directories to ignore.
    """
    return {".git", "build", ".idea", ".vscode", "__pycache__", "venv", "env"}


def get_cpp_extensions():
    """
    Returns a set of common C++ source and header file extensions.
    """
    return {".hpp", ".h", ".hxx", ".hh", ".cpp", ".cxx", ".cc", ".c"}


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
    Get all C++ source and header files in the repository.
    """
    return get_matched_paths(repo_path, get_cpp_extensions())


def get_spdx_info(lines):
    """
    Helper to find the SPDX line index and the comment prefix.
    Returns (spdx_index, comment_prefix).
    If not found or invalid, returns (-1, None).
    """
    spdx_index = next(
        (i for i, line in enumerate(lines) if "SPDX-License-Identifier:" in line),
        -1
    )
    
    if spdx_index == -1:
        return -1, None

    spdx_line = lines[spdx_index].strip()
    comment_prefix = None
    if spdx_line.startswith("//"):
        comment_prefix = "//"
    elif spdx_line.startswith("#"):
        comment_prefix = "#"
        
    return spdx_index, comment_prefix
