#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
import yaml
from beman_tidy.lib.utils.config import (
    validate_config,
    load_repo_config,
    get_default_config_path,
    get_disabled_rules,
    is_rule_disabled,
    _validate_disabled_rules
)



def test_validate_disabled_rules_valid():
    """Test that a valid disabled_rules configuration passes validation."""
    config = {
        "disabled_rules": ["readme.title", "readme.*"]
    }
    assert _validate_disabled_rules(config) is True

def test_validate_disabled_rules_empty():
    """Test that an empty disabled_rules configuration passes validation."""
    config = {"disabled_rules": []}
    assert _validate_disabled_rules(config) is True

def test_validate_disabled_rules_missing():
    """Test that validation passes if disabled_rules is missing."""
    config = {}
    assert _validate_disabled_rules(config) is True

def test_validate_disabled_rules_not_list(capsys):
    """Test that validation fails if disabled_rules is not a list."""
    config = {
        "disabled_rules": "not a list"
    }
    assert _validate_disabled_rules(config) is False
    captured = capsys.readouterr()
    assert "Error: 'disabled_rules' in .beman-tidy.yaml must be a list" in captured.out

def test_validate_disabled_rules_invalid_entry(capsys):
    """Test that validation fails if disabled_rules contains non-string entries."""
    config = {
        "disabled_rules": [123]
    }
    assert _validate_disabled_rules(config) is False
    captured = capsys.readouterr()
    assert "Error: Invalid entry in 'disabled_rules'" in captured.out

def test_validate_config_with_disabled_rules():
    """Test that validate_config correctly calls disabled_rules validation."""
    config = {
        "ignored_paths": ["build/"],
        "disabled_rules": ["readme.title"]
    }
    assert validate_config(config) is True



SAMPLE_KNOWN_RULES = [
    "readme.title",
    "readme.badges",
    "readme.implements",
    "readme.library_status",
    "cmake.project_name",
    "cmake.library_name",
    "license.approved",
    "file.test_names",
]

def test_get_disabled_rules_exact():
    """Test expanding an exact rule name."""
    repo_info = {"config": {"disabled_rules": ["readme.title"]}}
    result = get_disabled_rules(repo_info, SAMPLE_KNOWN_RULES)
    assert result == {"readme.title"}

def test_get_disabled_rules_glob_suffix():
    """Test expanding a suffix glob pattern (category.*)."""
    repo_info = {"config": {"disabled_rules": ["readme.*"]}}
    result = get_disabled_rules(repo_info, SAMPLE_KNOWN_RULES)
    assert result == {"readme.title", "readme.badges", "readme.implements", "readme.library_status"}

def test_get_disabled_rules_glob_prefix():
    """Test expanding a prefix glob pattern (*.name)."""
    repo_info = {"config": {"disabled_rules": ["*.title"]}}
    result = get_disabled_rules(repo_info, SAMPLE_KNOWN_RULES)
    assert result == {"readme.title"}

def test_get_disabled_rules_mixed():
    """Test expanding a mix of exact and glob patterns."""
    repo_info = {"config": {"disabled_rules": ["readme.*", "license.approved"]}}
    result = get_disabled_rules(repo_info, SAMPLE_KNOWN_RULES)
    expected = {"readme.title", "readme.badges", "readme.implements", "readme.library_status", "license.approved"}
    assert result == expected

def test_get_disabled_rules_unmatched_warning(capsys):
    """Test that unmatched patterns produce a warning and are skipped."""
    repo_info = {"config": {"disabled_rules": ["nonexistent.rule", "repository.*"]}}
    result = get_disabled_rules(repo_info, SAMPLE_KNOWN_RULES)
    assert result == set()
    captured = capsys.readouterr()
    assert "Warning: disabled_rules pattern 'nonexistent.rule' does not match any known rule" in captured.out
    assert "Warning: disabled_rules pattern 'repository.*' does not match any known rule" in captured.out



def test_is_rule_disabled():
    """Test the is_rule_disabled helper function."""
    ignored = {"readme.title", "cmake.project_name"}
    assert is_rule_disabled("readme.title", ignored) is True
    assert is_rule_disabled("cmake.project_name", ignored) is True
    assert is_rule_disabled("readme.badges", ignored) is False
    assert is_rule_disabled("other.rule", ignored) is False



def test_load_repo_config_with_disabled_rules(tmp_path):
    """Test that disabled_rules are correctly loaded from the config file."""
    # Mock default config content
    default_config_path = get_default_config_path()
    with default_config_path.open('r') as f:
        expected_config = yaml.safe_load(f) or {}

    # Define user config with disabled_rules
    user_config_content = {
        "disabled_rules": ["readme.*", "cmake.project_name"]
    }
    expected_config.update(user_config_content)

    # Create temporary config file
    config_file = tmp_path / ".beman-tidy.yaml"
    with open(config_file, "w") as f:
        yaml.dump(user_config_content, f)

    # Load and verify
    config = load_repo_config(tmp_path)
    assert config == expected_config

def test_load_repo_config_invalid_disabled_rules(tmp_path, capsys):
    """Test that loading fails if the config has invalid disabled_rules."""
    config_content = {
        "disabled_rules": "not a list"
    }
    config_file = tmp_path / ".beman-tidy.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    with pytest.raises(SystemExit):
        load_repo_config(tmp_path)
    
    captured = capsys.readouterr()
    assert "Error: 'disabled_rules' in .beman-tidy.yaml must be a list" in captured.out
