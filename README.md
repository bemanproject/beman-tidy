# beman-tidy: The Codebase Bemanification Tool

<!-- markdownlint-disable-next-line line-length -->
![CI Tests](https://github.com/bemanproject/beman-tidy/actions/workflows/beman-tidy.yml/badge.svg)

<!--
SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
-->
`beman-tidy` is a tool aimed at Beman Project contributors to check (`--dry-run`)
and apply (`--fix-inplace`) the [Beman Standard](https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md)
to their repositories.

**Note `2025-06-07`:** The first iteration of the tool will not support `--fix-inplace` in order to
expedite adoption across the Beman Project.

## Installation

```shell
uv tool install beman-tidy
```

To update:

```shell
uv tool upgrade beman-tidy
```

Post-install sanity check:

```shell
beman-tidy --help
```

## Requirements

- Python 3.12+
- `uv` (Python package and project manager - [Installation](https://docs.astral.sh/uv/getting-started/installation/))

## Compatibility

- Linux
- macOS
- Windows

## Usage

- Display help:

```shell
$ beman-tidy --help
usage: beman-tidy [-h] [--fix-inplace | --no-fix-inplace] [--verbose | --no-verbose] [--require-all | --no-require-all] [--checks CHECKS] [--config CONFIG] repo_path

positional arguments:
  repo_path             path to the repository to check

options:
  -h, --help            show this help message and exit
  --fix-inplace, --no-fix-inplace
                        Try to automatically fix found issues
  --verbose, --no-verbose
                        print verbose output for each check
  --require-all, --no-require-all
                        all checks are required regardless of the check type (e.g., Recommendation becomes Requirement)
  --checks CHECKS       array of checks to run
  --config CONFIG       path to the configuration file (default: .beman-tidy.yaml in repo root)
```

- Run beman-tidy on the exemplar repository **(default: dry-run mode)**

```shell
# dry-run, require-all, non-verbose
$ beman-tidy --require-all /path/to/exemplar
Summary    Requirement:  18 checks passed, 1 checks failed, 5 checks skipped,  23 checks not implemented.
Summary Recommendation:  0 checks passed, 0 checks failed, 0 checks skipped,  0 checks not implemented.

Coverage    Requirement:  95.83% (23/24 checks passed).
Coverage Recommendation:   0.00% (0/0 checks passed).
Coverage          TOTAL:  95.83% (23/24 checks passed).

# dry-run, no-require-all, non-verbose
$ beman-tidy /path/to/exemplar
Summary    Requirement:  13 checks passed, 1 checks failed, 3 checks skipped,  9 checks not implemented.
Summary Recommendation:  5 checks passed, 0 checks failed, 2 checks skipped,  14 checks not implemented.

Coverage    Requirement:  66.67% (16/24 checks passed).
Coverage Recommendation: 100.00% (7/7 checks passed).
Coverage          TOTAL:  74.19% (23/31 checks passed).
```

or verbose mode without errors:

```shell
# dry-run, require-all, verbose mode - no errors
$ beman-tidy --require-all --verbose /path/to/exemplar
beman-tidy pipeline started ...

Running check [Requirement][license.approved] ...
[info           ][license.approved         ]: Valid Apache License - Version 2.0 with LLVM Exceptions found in LICENSE file.
	check [Requirement][license.approved] ... passed

Running check [Requirement][license.apache_llvm] ...
	check [Requirement][license.apache_llvm] ... passed

Running check [Requirement][license.criteria] ...
[skipped        ][license.criteria         ]: beman-tidy cannot actually check license.criteria. Please ignore this message if license.approved has passed. See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licensecriteria for more information.
Running check [Requirement][license.criteria] ... skipped

...

Running check [Requirement][readme.title] ...
	check [Requirement][readme.title] ... passed

Running check [Requirement][readme.badges] ...
	check [Requirement][readme.badges] ... passed

Running check [Requirement][readme.implements] ...
	check [Requirement][readme.implements] ... passed

...

beman-tidy pipeline finished.

Summary    Requirement:  19 checks passed, 0 checks failed, 3 checks skipped,  23 checks not implemented.
Summary Recommendation:  0 checks passed, 0 checks failed, 2 checks skipped,  0 checks not implemented.

Coverage    Requirement: 100.00% (24/24 checks passed).
Coverage Recommendation:   0.00% (0/0 checks passed).
Coverage          TOTAL: 100.00% (24/24 checks passed).
```

or verbose mode with errors:

```shell
# dry-run, require-all, verbose mode - with errors
$ beman-tidy --require-all --verbose /path/to/exemplar
beman-tidy pipeline started ...

Running check [Requirement][license.approved] ...
[info           ][license.approved         ]: Valid Apache License - Version 2.0 with LLVM Exceptions found in LICENSE file.
	check [Requirement][license.approved] ... passed

Running check [Requirement][license.apache_llvm] ...
	check [Requirement][license.apache_llvm] ... passed

Running check [Requirement][license.criteria] ...
[skipped        ][license.criteria         ]: beman-tidy cannot actually check license.criteria. Please ignore this message if license.approved has passed. See https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md#licensecriteria for more information.
Running check [Requirement][license.criteria] ... skipped

...

Running check [Requirement][readme.implements] ...
	check [Requirement][readme.implements] ... passed

Running check [Requirement][readme.library_status] ...
[error          ][readme.library_status    ]: The file '/Users/dariusn/dev/dn/git/Beman/exemplar/README.md' does not contain exactly one of the required statuses from ['**Status**: [Under development and not yet ready for production use.](https://github.com/bemanproject/beman/blob/main/docs/beman_library_maturity_model.md#under-development-and-not-yet-ready-for-production-use)', '**Status**: [Production ready. API may undergo changes.](https://github.com/bemanproject/beman/blob/main/docs/beman_library_maturity_model.md#production-ready-api-may-undergo-changes)', '**Status**: [Production ready. Stable API.](https://github.com/bemanproject/beman/blob/main/docs/beman_library_maturity_model.md#production-ready-stable-api)', '**Status**: [Retired. No longer maintained or actively developed.](https://github.com/bemanproject/beman/blob/main/docs/beman_library_maturity_model.md#retired-no-longer-maintained-or-actively-developed)']
	check [Requirement][readme.library_status] ... failed

...

beman-tidy pipeline finished.

Summary    Requirement:  18 checks passed, 1 checks failed, 3 checks skipped,  23 checks not implemented.
Summary Recommendation:  0 checks passed, 0 checks failed, 2 checks skipped,  0 checks not implemented.

Coverage    Requirement:  95.83% (23/24 checks passed).
Coverage Recommendation:   0.00% (0/0 checks passed).
Coverage          TOTAL:  95.83% (23/24 checks passed).
```

- Run beman-tidy on the exemplar repository (fix issues in-place):

```shell
beman-tidy --fix-inplace --verbose path/to/exemplar
```

## CI Usage (GitHub Actions)

This repository already includes a full workflow in `.github/workflows/beman-tidy.yml` covering linting,
tests, build/install, and running `beman-tidy` on `bemanproject/exemplar`.

## Configuration

`beman-tidy` attempts to read configuration for each source file from a `.beman-tidy.yaml` file located in the root of your repository. You can also specify a custom configuration file path using the `--config` option.

The following configuration options may be used in a `.beman-tidy.yaml` file:

- `ignored_paths` - A list of paths to be excluded from all checks.
  - To ignore a specific file, provide its full path relative to the repository root.
  - To ignore a directory, provide the path to that directory. This will ignore the directory itself and all files and subdirectories within it. A trailing slash (`/`) is optional.

- Example:
  ```yaml
  ignored_paths:
    # Ignores a single file
    - include/beman/optional/detail/stl_interfaces/config.hpp

    # Ignores a directory and everything inside it
    - include/beman/optional/another_dir
  ```

- `disabled_rules` - A list of rule names (or patterns) to be completely skipped during checks.
  - To ignore a specific rule, provide its exact name (e.g., `readme.title`).
  - To ignore all rules in a category, use a glob pattern with `*` (e.g., `readme.*` to skip all readme checks).
  - To ignore a specific rule across all categories, use `*.rule_name` (e.g., `*.title`).
  - Unknown patterns that don't match any known rule will produce a warning and be skipped.
  - Ignored rules appear as "ignored" in the summary and are excluded from coverage calculations.

- Example:
  ```yaml
  disabled_rules:
    # Ignores a single rule
    - readme.title

    # Ignores all readme checks
    - readme.*

    # Ignores all rules named "title" across categories
    - "*.title"
  ```

## Fix-inplace Status

- The CLI exposes `--fix-inplace`, but auto-fix support is currently limited.

## Troubleshooting / FAQ

- Why is a check reported as skipped?
  - Some checks are intentionally skippable/dummy implementations and emit a reason in verbose mode.
- Why do I see "not implemented" in the summary?
  - The check exists in the Beman Standard snapshot but does not yet have an implemented checker.
- How do I ignore files/directories?
  - Use `ignored_paths` in `.beman-tidy.yaml`.
- How do I ignore specific rules?
  - Use `disabled_rules` in `.beman-tidy.yaml`. You can specify exact rule names or glob patterns like `readme.*`.
- How do I get more detail?
  - Run with `--verbose` to print per-check diagnostics.

## Integrating beman-tidy into Your Library

Please refer to the [How to Integrate beman-tidy pre-commit Hook in Your Library](./docs/pre-commit.md) for more details.

## Contributing on beman-tidy

Please refer to the [Beman Tidy Development Guide](./docs/dev-guide.md) for more details.

## License

Licensed under Apache-2.0 WITH LLVM-exception. See `LICENSE`.
