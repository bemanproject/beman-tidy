#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import os
from pathlib import Path
from .comments import determine_comment_type


def get_repo_ignorable_subdirectories():
    """
    Returns a set of common build and IDE directories to ignore.
    """
    return {
        ".git/",
        "build/",
        "cmake-build-debug/",
        "cmake-build-release/",
        ".idea/",
        ".vscode/",
        "__pycache__/",
        ".pytest_cache/",
        ".ruff_cache/",
        "node_modules/",
        "venv/",
        "env/",
    }


def get_cpp_header_extensions():
    """
    Returns a set of common C++ header file extensions.
    """
    return {".hpp", ".h", ".hxx", ".hh"}


def get_cpp_source_extensions():
    """
    Returns a set of common C++ source file extensions.
    """
    return {".cpp", ".cxx", ".cc", ".c"}


def get_cpp_extensions():
    """
    Returns a set of common C++ source and header file extensions.
    """
    return get_cpp_header_extensions() | get_cpp_source_extensions()


def _is_ignored(path, ignores):
    path_str = path.as_posix()

    for pattern in ignores:
        clean_pattern = pattern.rstrip("/") # trailing slash is optional
        if path_str == clean_pattern or path_str.startswith(clean_pattern + "/"):
            return True
    return False


def get_matched_paths(repo_path, extensions, ignores=None):
    """
    Get all files in the repository matching the given extensions.
    Ignores paths specified in 'ignores'.
    """
    if ignores is None:
        ignores = get_repo_ignorable_subdirectories()

    matched_files = []
    repo_path = Path(repo_path)

    for root, dirs, files in os.walk(repo_path):
        rel_root = Path(root).relative_to(repo_path)

        for d in list(dirs):
            d_path = rel_root / d
            if _is_ignored(d_path, ignores):
                dirs.remove(d)

        for f in files:
            f_path = rel_root / f
            if f_path.suffix in extensions:
                if not _is_ignored(f_path, ignores):
                    matched_files.append(f_path)

    return sorted(list(set(matched_files)))


def get_cpp_files(repo_path, ignores=None):
    """
    Get all C++ source and header files in the repository.
    """
    return get_matched_paths(repo_path, get_cpp_extensions(), ignores=ignores)


def get_non_test_cpp_files(repo_path, ignores=None):
    """
    Get all C++ source and header files NOT under a tests/ directory.
    """
    all_files = get_cpp_files(repo_path, ignores=ignores)

    non_test_files = []
    for path in all_files:
        if "tests" not in path.parts:
            non_test_files.append(path)

    return non_test_files


def get_beman_include_headers(repo_path, ignores=None):
    """
    Get all header files in the repository under an include/beman directory.
    """
    all_headers = get_matched_paths(repo_path, get_cpp_header_extensions(), ignores=ignores)
    
    beman_headers = []
    for path in all_headers:
        try:
            parts = path.parts
            include_index = parts.index('include')
            if include_index + 1 < len(parts) and parts[include_index + 1] == 'beman':
                beman_headers.append(path)
        except ValueError:
            continue
            
    return beman_headers


COMMENTABLE_EXTENSIONS = {
    # C++
    ".cpp", ".hpp", ".h", ".hxx", ".cxx", ".cc",
    # CMake
    ".cmake",
    # Python
    ".py",
    # Shell
    ".sh",
    # YAML/YML
    ".yml", ".yaml",
}

COMMENTABLE_FILENAMES = {
    "CMakeLists.txt",
    "Dockerfile",
}


def get_commentable_files(repo_path, ignores=None):
    """
    Get all files that can contain a comment (and thus should have an SPDX identifier).
    Covers C++, CMake, Python, shell scripts, and YAML files.
    """
    if ignores is None:
        ignores = get_repo_ignorable_subdirectories()

    matched_files = []
    repo_path = Path(repo_path)

    for root, dirs, files in os.walk(repo_path):
        rel_root = Path(root).relative_to(repo_path)

        for d in list(dirs):
            d_path = rel_root / d
            if _is_ignored(d_path, ignores):
                dirs.remove(d)

        for f in files:
            f_path = rel_root / f
            if f_path.suffix in COMMENTABLE_EXTENSIONS or f_path.name in COMMENTABLE_FILENAMES:
                if not _is_ignored(f_path, ignores):
                    matched_files.append(f_path)

    return sorted(list(set(matched_files)))


def get_spdx_info(lines):
    """
    Helper to find the SPDX line index and the comment info.
    Returns (spdx_index, comment_info).

    If not found or invalid, returns (-1, None).
    """
    spdx_index = next(
        (i for i, line in enumerate(lines) if "SPDX-License-Identifier:" in line),
        -1
    )

    if spdx_index == -1:
        return -1, None

    comment_info = determine_comment_type(lines, spdx_index)
    return spdx_index, comment_info


def get_test_files(repo_path, ignores=None):
    """
    Get all C++ files in the tests/ directory.
    """
    all_cpp_files = get_cpp_files(repo_path, ignores=ignores)
    return [p for p in all_cpp_files if "tests" in p.parts]
