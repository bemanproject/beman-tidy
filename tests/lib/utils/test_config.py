#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import pytest
import yaml
from beman_tidy.lib.utils.config import validate_config, load_repo_config

def test_validate_config_valid():
    """Test that a valid configuration passes validation."""
    config = {
        "ignored_paths": ["build/", ".git/"]
    }
    assert validate_config(config) is True

def test_validate_config_empty():
    """Test that an empty configuration passes validation."""
    config = {}
    assert validate_config(config) is True

def test_validate_config_ignored_paths_not_list(capsys):
    """Test that validation fails if ignored_paths is not a list."""
    config = {
        "ignored_paths": "not a list"
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: 'ignored_paths' in .beman-tidy.yml must be a list" in captured.out

def test_validate_config_ignored_paths_invalid_entry(capsys):
    """Test that validation fails if ignored_paths contains non-string entries."""
    config = {
        "ignored_paths": [123]
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: Invalid entry in 'ignored_paths'" in captured.out

def test_validate_config_mandatory_file_ignored(capsys):
    """Test that validation fails if a mandatory file is ignored."""
    config = {
        "ignored_paths": ["README.md"]
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: Cannot ignore mandatory file 'README.md'" in captured.out

    config = {
        "ignored_paths": ["LICENSE"]
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: Cannot ignore mandatory file 'LICENSE'" in captured.out

def test_validate_config_root_ignored(capsys):
    """Test that validation fails if the root directory is ignored."""
    config = {
        "ignored_paths": ["."]
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: Cannot ignore root directory" in captured.out

    config = {
        "ignored_paths": ["./"]
    }
    assert validate_config(config) is False
    captured = capsys.readouterr()
    assert "Error: Cannot ignore root directory" in captured.out

def test_load_repo_config_default(tmp_path):
    """Test loading the default configuration file."""
    config_content = {
        "ignored_paths": ["build/"]
    }
    config_file = tmp_path / ".beman-tidy.yml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    config = load_repo_config(tmp_path)
    assert config == config_content

def test_load_repo_config_custom_path(tmp_path):
    """Test loading a configuration file from a custom path."""
    config_content = {
        "ignored_paths": ["dist/"]
    }
    config_file = tmp_path / "custom_config.yml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    config = load_repo_config(tmp_path, config_path=str(config_file))
    assert config == config_content

def test_load_repo_config_not_found_default(tmp_path):
    """Test loading when the default configuration file does not exist."""
    config = load_repo_config(tmp_path)
    assert config == {}

def test_load_repo_config_not_found_custom(tmp_path, capsys):
    """Test loading when a custom configuration file does not exist."""
    with pytest.raises(SystemExit):
        load_repo_config(tmp_path, config_path=str(tmp_path / "nonexistent.yml"))
    
    captured = capsys.readouterr()
    assert "Error: Configuration file specified not found" in captured.out

def test_load_repo_config_invalid_yaml(tmp_path, capsys):
    """Test loading an invalid YAML file."""
    config_file = tmp_path / ".beman-tidy.yml"
    with open(config_file, "w") as f:
        f.write("invalid: yaml: :")

    with pytest.raises(SystemExit):
        load_repo_config(tmp_path)
    
    captured = capsys.readouterr()
    assert "Error loading user configuration" in captured.out

def test_load_repo_config_invalid_validation(tmp_path, capsys):
    """Test loading a configuration that fails validation."""
    config_content = {
        "ignored_paths": ["README.md"]
    }
    config_file = tmp_path / ".beman-tidy.yml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    with pytest.raises(SystemExit):
        load_repo_config(tmp_path)
    
    captured = capsys.readouterr()
    assert "Error: Cannot ignore mandatory file 'README.md'" in captured.out
