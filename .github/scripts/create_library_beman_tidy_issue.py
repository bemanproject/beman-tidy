#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""Open or update a beman-tidy failure issue in a Beman library repository."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ISSUE_TITLE = "[beman-tidy] Beman Standard check failure"
EXTRA_ASSIGNEES = ("neatudarius",)
ORG = "bemanproject"
LOG_TRUNCATE_BYTES = 12000


def _extract_users_from_line(line: str) -> list[str]:
    users: list[str] = []
    for token in line.split():
        if not token.startswith("@"):
            continue
        if "/" in token:
            continue
        users.append(token[1:])
    return users


def parse_codeowners(repo_path: Path) -> list[str]:
    codeowners = repo_path / ".github" / "CODEOWNERS"
    if not codeowners.is_file():
        return []

    users: list[str] = []
    seen: set[str] = set()
    for raw_line in codeowners.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        for user in _extract_users_from_line(line):
            if user not in seen:
                seen.add(user)
                users.append(user)
    return users


def gh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def find_open_issue(repo: str) -> int | None:
    result = gh(
        "issue",
        "list",
        "--repo",
        f"{ORG}/{repo}",
        "--state",
        "open",
        "--search",
        ISSUE_TITLE,
        "--limit",
        "1",
        "--json",
        "number",
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return None

    issues = json.loads(result.stdout or "[]")
    if not issues:
        return None
    return int(issues[0]["number"])


def build_body(
    repo: str,
    mode: str,
    tidy_version: str,
    run_url: str,
    tidy_log: str,
    assignees: list[str],
) -> str:
    mentions = " ".join(f"@{user}" for user in assignees)
    log_excerpt = tidy_log[-LOG_TRUNCATE_BYTES:] if len(tidy_log) > LOG_TRUNCATE_BYTES else tidy_log

    return f"""## beman-tidy check failure

Până acum toate check-urile treceau în modul **`{mode}`** (conform configurației pre-commit din acest repo). Acum nu mai trec după ultima rulare `beman-tidy` din workflow-ul [Run on all Beman libraries]({run_url}).

| Field | Value |
|-------|-------|
| Library | `beman.{repo}` |
| Mode | `{mode}` |
| beman-tidy | `{tidy_version}` |
| Workflow run | {run_url} |

### Output (truncated)

```
{log_excerpt}
```

### Owners

{mentions}

Please investigate which newly implemented or newly enforced checks are failing and update the repository accordingly.
"""


def create_or_update_issue(
    repo: str,
    mode: str,
    tidy_version: str,
    run_url: str,
    tidy_log: str,
    repo_path: Path,
) -> int:
    assignees = list(
        dict.fromkeys([*parse_codeowners(repo_path), *EXTRA_ASSIGNEES])
    )
    body = build_body(repo, mode, tidy_version, run_url, tidy_log, assignees)
    target = f"{ORG}/{repo}"

    existing = find_open_issue(repo)
    if existing is not None:
        comment = gh("issue", "comment", "--repo", target, str(existing), "--body", body)
        if comment.returncode != 0:
            print(comment.stderr, file=sys.stderr)
            return 1
        print(f"Updated existing issue #{existing} in {target}")
        return 0

    create_args = [
        "issue",
        "create",
        "--repo",
        target,
        "--title",
        ISSUE_TITLE,
        "--body",
        body,
    ]
    for assignee in assignees:
        create_args.extend(["--assignee", assignee])

    created = gh(*create_args)
    if created.returncode != 0:
        print(created.stderr, file=sys.stderr)
        return 1

    print(created.stdout.strip())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Repository short name, e.g. optional")
    parser.add_argument("--mode", required=True, choices=("default", "require-all"))
    parser.add_argument("--log", required=True, type=Path, help="beman-tidy log file")
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--tidy-version", default="unknown")
    parser.add_argument(
        "--repo-path",
        type=Path,
        help="Path to cloned repository (defaults to ./<repo>)",
    )
    args = parser.parse_args()

    if not os.environ.get("GH_TOKEN"):
        print("GH_TOKEN is required to create issues", file=sys.stderr)
        return 1

    repo_path = args.repo_path or Path(args.repo)
    tidy_log = args.log.read_text(encoding="utf-8", errors="replace")
    return create_or_update_issue(
        args.repo,
        args.mode,
        args.tidy_version,
        args.run_url,
        tidy_log,
        repo_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
