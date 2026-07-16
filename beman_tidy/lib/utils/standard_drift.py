#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""Compare beman_standard.md rules against beman_tidy/.beman-standard.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

RULE_HEADING_RE = re.compile(r"^###\s+\*\*\[([^\]]+)\]\*\*", re.MULTILINE)
RULE_TYPE_RE = re.compile(r"^\*\*(Requirement|Recommendation)\*\*:", re.MULTILINE)


@dataclass
class DriftReport:
    added: dict[str, str] = field(default_factory=dict)
    removed: list[str] = field(default_factory=list)
    type_changed: dict[str, tuple[str, str]] = field(default_factory=dict)

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.type_changed)

    def format_markdown(self, standard_url: str) -> str:
        lines = [
            "The upstream [Beman Standard](" + standard_url + ") "
            "and [`beman_tidy/.beman-standard.yaml`]"
            "(https://github.com/bemanproject/beman-tidy/blob/main/beman_tidy/.beman-standard.yaml) "
            "are out of sync.",
            "",
        ]

        if self.added:
            lines.append("## New rules in the standard (missing from YAML)")
            lines.append("")
            for rule_id, rule_type in sorted(self.added.items()):
                lines.append(f"- `{rule_id}` — **{rule_type}**")
            lines.append("")

        if self.removed:
            lines.append("## Rules removed from the standard (still in YAML)")
            lines.append("")
            for rule_id in sorted(self.removed):
                lines.append(f"- `{rule_id}`")
            lines.append("")

        if self.type_changed:
            lines.append("## Category mismatches")
            lines.append("")
            for rule_id, (md_type, yaml_type) in sorted(self.type_changed.items()):
                lines.append(
                    f"- `{rule_id}`: standard says **{md_type}**, "
                    f"YAML has **{yaml_type}**"
                )
            lines.append("")

        lines.extend(
            [
                "## Action",
                "",
                "Update `beman_tidy/.beman-standard.yaml` to match the standard, "
                "then implement or track any new checks as needed.",
                "",
                "_This issue was opened automatically by the "
                "[Sync Beman Standard workflow]"
                "(https://github.com/bemanproject/beman-tidy/actions/workflows/sync-beman-standard.yml)._",
            ]
        )
        return "\n".join(lines)


def parse_beman_standard_markdown(text: str) -> dict[str, str]:
    """Extract check identifiers and types from beman_standard.md."""
    rules: dict[str, str] = {}

    for match in RULE_HEADING_RE.finditer(text):
        rule_id = match.group(1).strip()
        section_start = match.end()
        next_heading = RULE_HEADING_RE.search(text, section_start)
        section_end = next_heading.start() if next_heading else len(text)
        section = text[section_start:section_end]

        type_match = RULE_TYPE_RE.search(section)
        if type_match is None:
            raise ValueError(
                f"No Requirement/Recommendation line found for rule '{rule_id}'"
            )

        rules[rule_id] = type_match.group(1)

    return rules


def parse_beman_standard_yaml(text: str) -> dict[str, str]:
    """Extract check identifiers and types from .beman-standard.yaml."""
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Beman Standard YAML must be a mapping")

    rules: dict[str, str] = {}
    for rule_id, entries in data.items():
        if not isinstance(entries, list):
            raise ValueError(f"Invalid config for rule '{rule_id}'")

        rule_type = None
        for entry in entries:
            if isinstance(entry, dict) and "type" in entry:
                rule_type = entry["type"]
                break

        if rule_type is None:
            raise ValueError(f"No type entry found for rule '{rule_id}'")

        rules[rule_id] = rule_type

    return rules


def compare_standard_to_yaml(
    markdown_rules: dict[str, str],
    yaml_rules: dict[str, str],
) -> DriftReport:
    """Compare upstream standard rules against the local YAML snapshot."""
    markdown_ids = set(markdown_rules)
    yaml_ids = set(yaml_rules)

    added = {
        rule_id: markdown_rules[rule_id]
        for rule_id in sorted(markdown_ids - yaml_ids)
    }
    removed = sorted(yaml_ids - markdown_ids)
    type_changed = {
        rule_id: (markdown_rules[rule_id], yaml_rules[rule_id])
        for rule_id in sorted(markdown_ids & yaml_ids)
        if markdown_rules[rule_id] != yaml_rules[rule_id]
    }

    return DriftReport(added=added, removed=removed, type_changed=type_changed)


def check_standard_drift(
    markdown_path: Path | str,
    yaml_path: Path | str,
) -> DriftReport:
    markdown_text = Path(markdown_path).read_text(encoding="utf-8")
    yaml_text = Path(yaml_path).read_text(encoding="utf-8")
    return compare_standard_to_yaml(
        parse_beman_standard_markdown(markdown_text),
        parse_beman_standard_yaml(yaml_text),
    )
