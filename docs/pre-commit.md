# How to Integrate beman-tidy pre-commit Hook in Your Library

## Goal

Run `beman-tidy` on your library and fix any violations found.

Context:
- [The Beman Standard](https://github.com/bemanproject/beman/blob/main/docs/beman_standard.md)
- [beman-tidy](https://github.com/bemanproject/beman-tidy)

## Steps

1. **Add beman-tidy** to library root `.pre-commit-config.yaml` file. Entry example:
Notes:
- Use the same `beman-tidy` stable version from [beman-tidy/releases](https://github.com/bemanproject/beman-tidy/releases) (e.g., `v0.3.1` attach example).
- Check/test/decide if you want to
  - Enable all checks (`requirements` + `recommendations`) -> `args: [".", "--verbose", "--require-all"]`
  -  Or use default set of checks (only `requirements`) -> skip `args` from config.

Example:
```shell
optional [main] $ git diff
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index a9f6e79..629f105 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -45,4 +45,11 @@ repos:
             papers/.*
           )$
 
+    # Beman Standard checking via beman-tidy
+  - repo: https://github.com/bemanproject/beman-tidy
+    rev: v0.3.1
+    hooks:
+    - id: beman-tidy
+      args: [".", "--verbose", "--require-all"]
+
 exclude: 'infra/'
```

2. **Run pre-commit checks**
* example of Beman Standard compliant repo
```shell
optional [main] $ pre-commit run --all-files
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
clang-format.............................................................Passed
CMake linting............................................................Passed
markdownlint.............................................................Passed
codespell................................................................Passed
beman-tidy...............................................................Passed
```

* example of Beman Standard NOT compliant repo
```shell
# In this example, --require-all was used inside the pre-commit config.
optional [main] $ pre-commit run --all-files
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
clang-format.............................................................Passed
CMake linting............................................................Passed
markdownlint.............................................................Passed
codespell................................................................Passed
beman-tidy...............................................................Failed
- hook id: beman-tidy
- exit code: 1

beman-tidy pipeline started ...

Running check [Requirement][license.approved] ... 
[info][license.approved]: Valid Apache License - Version 2.0 with LLVM Exceptions found in LICENSE file.
	check [Requirement][license.approved] ... passed

...

Running check [Requirement][readme.title] ...
[error][readme.title]: The first line of the file 'README.md' is invalid. It should start with '# beman.optional: <short_description>'.
	check [Requirement][readme.title] ... failed

...

beman-tidy pipeline finished.

Summary    Requirement:  21 checks passed, 1 checks failed, 3 checks skipped,  19 checks not implemented.
Summary Recommendation:  0 checks passed, 0 checks failed, 3 checks skipped,  0 checks not implemented.

Coverage    Requirement:  96.43% (27/28 checks passed).
Coverage Recommendation:   0.00% (0/0 checks passed).
Coverage          TOTAL:  96.43% (27/28 checks passed).
```

3. Fix violations. Re-run. Considering doing separate PRs for each type of change. Merge these changes into `main`.

4. Re-run latest `main` of your library. Check that all `pre-commit` hooks (including `beman-tidy`) pass before goint to next step.

5. Last step: commit and push changes from `.pre-commit-config.yaml`. After this PR is merged, future changes in the repo will be automatically checked via CI (supposing it is configured to run pre-commit)
