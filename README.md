# beman-tidy: The Codebase Bemanification Tool

<!--
SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
-->
`beman-tidy` is a tool aimed at Beman Project contributors to check (`--dry-run`)
and apply (`--fix-inplace`) the [Beman Standard](https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md)
to their repositories.

**Note `2025-06-07`:** The first iteration of the tool will not support `--fix-inplace` in order to
expedite adoption across the Beman Project.

## Usage

- Display help:

```shell
$ beman-tidy --help
usage: beman-tidy [-h] [--fix-inplace | --no-fix-inplace] [--verbose | --no-verbose] [--require-all | --no-require-all] [--checks CHECKS] repo_path

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
```

- Run beman-tidy on the exemplar repository **(default: dry-run mode)**

```shell
# dry-run, require-all, non-verbose
$ beman-tidy /path/to/exemplar --require-all
Summary    Requirement:  18 checks passed, 1 checks failed, 5 checks skipped,  23 checks not implemented.
Summary Recommendation:  0 checks passed, 0 checks failed, 0 checks skipped,  0 checks not implemented.

Coverage    Requirement:  95.83% (23/24 checks passed).
Coverage Recommendation:   0.00% (0/0 checks passed).
Coverage          TOTAL:  95.83% (23/24 checks passed).

# dry-run, non-require-all, non-verbose
Summary    Requirement:  13 checks passed, 1 checks failed, 3 checks skipped,  9 checks not implemented.
Summary Recommendation:  5 checks passed, 0 checks failed, 2 checks skipped,  14 checks not implemented.

Coverage    Requirement:  66.67% (16/24 checks passed).
Coverage Recommendation: 100.00% (7/7 checks passed).
Coverage          TOTAL:  74.19% (23/31 checks passed).
```

or verbose mode without errors:

```shell
# dry-run, require-all, verbose mode - no errors
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
beman-tidy path/to/exemplar --fix-inplace --verbose
```

## Working on beman-tidy

Please refer to the [Beman Tidy Development Guide](https://github.com/bemanproject/beman-tidy/blob/main/docs/dev-guide.md) for more details.
