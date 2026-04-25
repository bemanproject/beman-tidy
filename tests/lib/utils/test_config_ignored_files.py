#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
from pathlib import Path
from beman_tidy.lib.utils.config import is_ignored

def test_is_ignored_exact_file():
    """Test that an exact file path is correctly identified as ignored."""
    repo_info = {
        "config": {
            "ignored_paths": ["include/beman/optional/config.hpp"]
        }
    }
    # Path is ignored
    assert is_ignored(repo_info, Path("include/beman/optional/config.hpp")) is True
    # Similar path is NOT ignored
    assert is_ignored(repo_info, Path("include/beman/optional/other.hpp")) is False

def test_is_ignored_directory():
    """Test that ignoring a directory also ignores all its contents."""
    repo_info = {
        "config": {
            "ignored_paths": ["build/"]
        }
    }
    # Exact directory match
    assert is_ignored(repo_info, Path("build")) is True
    # Child file match
    assert is_ignored(repo_info, Path("build/main.o")) is True
    # Nested child match
    assert is_ignored(repo_info, Path("build/debug/output.log")) is True
    # Unrelated path is NOT ignored
    assert is_ignored(repo_info, Path("src/main.cpp")) is False

def test_is_ignored_multiple_paths():
    """Test that multiple ignored paths are all respected."""
    repo_info = {
        "config": {
            "ignored_paths": ["build/", "temp.txt", "docs/internal/"]
        }
    }
    assert is_ignored(repo_info, Path("build/file.txt")) is True
    assert is_ignored(repo_info, Path("temp.txt")) is True
    assert is_ignored(repo_info, Path("docs/internal/secret.md")) is True
    assert is_ignored(repo_info, Path("docs/readme.md")) is False

def test_is_ignored_no_config():
    """Test behavior when no ignored_paths are configured."""
    repo_info = {"config": {}}
    assert is_ignored(repo_info, Path("src/main.cpp")) is False

def test_is_ignored_slash_handling():
    """Test that trailing slashes in config don't affect matching consistency."""
    repo_info = {
        "config": {
            "ignored_paths": ["build", "docs/"]
        }
    }
    # Both should work whether or not they have a trailing slash in config
    assert is_ignored(repo_info, Path("build/test.o")) is True
    assert is_ignored(repo_info, Path("docs/test.md")) is True
