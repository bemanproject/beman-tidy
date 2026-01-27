#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

def get_source_files(repo_path):
    """
    Get all source files in the repository.
    Currently considers C++ source and header files.
    Ignores common build and IDE directories.
    """
    source_extensions = {".hpp", ".cpp", ".h", ".c", ".cxx", ".hxx", ".cc", ".hh"}
    exclude_dirs = {".git", "build", ".idea", ".vscode", "__pycache__", "venv", "env"}
    
    source_files = []
    repo_path = Path(repo_path)
    
    for path in repo_path.rglob("*"):
        if path.is_file():
            try:
                rel_path = path.relative_to(repo_path)
            except ValueError:
                continue

            # Check if any part of the relative path is in exclude_dirs
            if any(part in exclude_dirs for part in rel_path.parts):
                continue
                
            if path.suffix in source_extensions:
                source_files.append(rel_path)
                
    return sorted(source_files)
