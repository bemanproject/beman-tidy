# beman-tidy: Codebase Beminification Tool

<!--
SPDX-License-Identifier: 2.0 license with LLVM exceptions
-->

## Description

TODO: Add a description.

`beman-tidy` is a tool used to check and apply [The Beman Standard](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_STANDARD.md).

## Installation

TODO: Add an installation section.

## Usage

TODO: Add a usage section.

```shell
$ ./tools/beman-tidy/beman-tidy --help
usage: beman-tidy [-h] --repo_path REPO_PATH [--fix | --no-fix]

optional arguments:
  -h, --help            show this help message and exit
  --repo_path REPO_PATH
                        path to the repository to check
  --fix, --no-fix       try to automatically fix found issues (default: False)

# no errors found example
$ ./tools/beman-tidy/beman-tidy --repo_path ../exemplar
Checks pipeline started ...

Running check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... 
 check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... PASSED

...

Checks pipeline completed.
# errors found example
$ ./tools/beman-tidy/beman-tidy --repo_path ../exemplar      
Checks pipeline started ...

Running check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... 
 check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... FAILED

...

Checks pipeline completed.

# errors found + --fix example
$ ./tools/beman-tidy/beman-tidy
beman-tidy is a tool to check the coding standard of The Beman Project.

/tools/beman-tidy/beman-tidy --repo_path ../exemplar --fix
Checks pipeline started ...

Running check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... 
 check [REQUIREMENT][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES] ... FAILED

[ERROR          ][FIX_INPLACE_INCOMPATIBLE_WITH_UNSTAGED_CHANGES]: The fix cannot be applied inplace. Please commit or stash your changes. STOP.
```
