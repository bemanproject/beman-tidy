#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

import pytest

from beman_tidy.lib.utils.standard_drift import (
    check_standard_drift,
    compare_standard_to_yaml,
    parse_beman_standard_markdown,
    parse_beman_standard_yaml,
)

STANDARD_MD = Path(__file__).resolve().parents[3] / "tests" / "data" / "beman_standard.md"
YAML_CONFIG = (
    Path(__file__).resolve().parents[3] / "beman_tidy" / ".beman-standard.yaml"
)


@pytest.fixture
def standard_markdown() -> str:
    return STANDARD_MD.read_text(encoding="utf-8")


@pytest.fixture
def standard_yaml() -> str:
    return YAML_CONFIG.read_text(encoding="utf-8")


def test__parse_beman_standard_markdown__extracts_rules(standard_markdown):
    rules = parse_beman_standard_markdown(standard_markdown)

    assert rules["license.approved"] == "Requirement"
    assert rules["license.apache_llvm"] == "Recommendation"
    assert rules["cmake.target_names"] == "Recommendation"
    assert rules["cpp.no_flag_forking"] == "Requirement"
    assert rules["release.version"] == "Recommendation"
    assert rules["cpp.min_std_version"] == "Recommendation"
    assert "core.quality" not in rules


def test__parse_beman_standard_yaml__extracts_rules(standard_yaml):
    rules = parse_beman_standard_yaml(standard_yaml)

    assert rules["license.approved"] == "Requirement"
    assert rules["cmake.library_alias"] == "Requirement"
    assert rules["file.copyright"] == "Recommendation"


def test__compare_standard_to_yaml__detects_missing_rules():
    report = compare_standard_to_yaml(
        {
            "release.version": "Recommendation",
            "cpp.min_std_version": "Recommendation",
        },
        {},
    )

    assert report.has_drift
    assert set(report.added) == {"release.version", "cpp.min_std_version"}
    assert report.added["release.version"] == "Recommendation"
    assert report.added["cpp.min_std_version"] == "Recommendation"
    assert report.removed == []
    assert report.type_changed == {}


def test__compare_standard_to_yaml__repo_snapshot_in_sync(standard_markdown, standard_yaml):
    report = compare_standard_to_yaml(
        parse_beman_standard_markdown(standard_markdown),
        parse_beman_standard_yaml(standard_yaml),
    )

    assert not report.has_drift
    assert report.added == {}
    assert report.removed == []
    assert report.type_changed == {}


def test__compare_standard_to_yaml__detects_type_change():
    report = compare_standard_to_yaml(
        {"cmake.default": "Requirement"},
        {"cmake.default": "Recommendation"},
    )

    assert report.has_drift
    assert report.type_changed == {
        "cmake.default": ("Requirement", "Recommendation")
    }


def test__compare_standard_to_yaml__detects_removed_rule():
    report = compare_standard_to_yaml(
        {},
        {"release.notes": "Recommendation"},
    )

    assert report.has_drift
    assert report.removed == ["release.notes"]


def test__compare_standard_to_yaml__in_sync():
    rules = {"license.approved": "Requirement", "library.name": "Recommendation"}
    report = compare_standard_to_yaml(rules, rules.copy())

    assert not report.has_drift


def test__check_standard_drift__uses_repo_files():
    report = check_standard_drift(STANDARD_MD, YAML_CONFIG)

    assert not report.has_drift
