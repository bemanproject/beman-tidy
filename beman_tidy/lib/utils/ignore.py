#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import logging
import os
from functools import lru_cache
from pathlib import Path

from pathspec import GitIgnoreSpec

from .logger_config import setup_logging

setup_logging()

GITIGNORE_FILENAME = ".gitignore"

# Files that must always be checked, whatever the ignore sources say.
# .beman-tidy.yaml is validated against these (see validate_config), but a
# repository's .gitignore is not ours to reject, so a match is only warned about.
MANDATORY_PATHS = frozenset({"README.md", "LICENSE"})

# Build and IDE directories ignored by default in every repository.
DEFAULT_IGNORE_PATTERNS = (
    ".git/",
    "build/",
    "cmake-build-debug/",
    "cmake-build-release/",
    ".idea/",
    ".vscode/",
    "__pycache__/",
    ".pytest_cache/",
    ".ruff_cache/",
    "node_modules/",
    "venv/",
    ".venv/",
    "env/",
)


class IgnoreMatcher:
    """
    Matches repository-relative paths against the configured ignore sources.

    Every source uses .gitignore pattern syntax: the built-in defaults, the
    'ignored_paths' entries of .beman-tidy.yaml and the repository's own
    .gitignore files.

    Layers are consulted from the highest precedence to the lowest:
      1. 'ignored_paths' from the beman-tidy configuration
      2. .gitignore files, deepest directory first
      3. the built-in defaults
    The first layer holding a pattern that matches decides, so a negated entry
    ('!foo') re-includes a path that a lower-precedence layer ignores.
    """

    def __init__(self, root=None, layers=()):
        # root is only needed to tell files from directories on disk; matching
        # itself is purely lexical.
        self.root = Path(root) if root is not None else None
        # Each layer is a (base directory, GitIgnoreSpec) pair, with the base
        # directory relative to the repository root ("." for the root itself).
        self._layers = list(layers)
        self._warned_mandatory = set()

    def add_gitignore_layer(self, base, spec):
        """
        Add a .gitignore layer below the configuration layer, above every layer
        added before it.
        """
        self._layers.insert(1, (base, spec))

    def is_ignored(self, relative_path, is_dir=None):
        """
        Check if a repository-relative path is ignored.

        @param relative_path: The path to check, relative to the repository root.
        @param is_dir: Whether the path is a directory. Determined from disk when
                       None, and if the path does not exist, both interpretations
                       are tried so that e.g. "build/" still matches "build".
        """
        rel_path = Path(relative_path).as_posix().strip("/")
        if not rel_path or rel_path == ".":
            return False

        # A path under an ignored directory is ignored even if a pattern
        # re-includes it: git does not allow re-including below an excluded
        # directory, and the directory is pruned before we ever descend into it.
        parts = rel_path.split("/")
        for depth in range(1, len(parts)):
            if self._check("/".join(parts[:depth]), is_dir=True) is True:
                return self._allow_ignoring(rel_path)

        if is_dir is None:
            is_dir = self._probe_is_dir(rel_path)

        if is_dir is None:
            ignored = self._check(rel_path, is_dir=True) is True or (
                self._check(rel_path, is_dir=False) is True
            )
        else:
            ignored = self._check(rel_path, is_dir=is_dir) is True

        return self._allow_ignoring(rel_path) if ignored else False

    def _allow_ignoring(self, rel_path):
        """
        Keep mandatory files checked, whatever matched them.
        """
        if rel_path not in MANDATORY_PATHS:
            return True

        if rel_path not in self._warned_mandatory:
            self._warned_mandatory.add(rel_path)
            logging.warning(
                f"Warning: '{rel_path}' is ignored by an ignore source, but it is mandatory. Still checking it."
            )
        return False

    def _probe_is_dir(self, rel_path):
        """
        Determine from disk whether a path is a directory.
        Returns None if that cannot be determined.
        """
        if self.root is None:
            return None

        path = self.root / rel_path
        if path.is_dir():
            return True
        if path.exists():
            return False
        return None

    def _check(self, rel_path, is_dir):
        """
        Ask each layer, highest precedence first, whether it matches the path.
        Returns True (ignored), False (explicitly re-included) or None (no match).
        """
        # A trailing slash is what makes directory-only patterns ("build/") match.
        candidate = f"{rel_path}/" if is_dir else rel_path

        for base, spec in self._layers:
            scoped_path = _relative_to(candidate, base)
            if scoped_path is None:
                continue

            result = spec.check_file(scoped_path)
            if result.include is not None:
                return result.include

        return None


def _relative_to(candidate, base):
    """
    Re-root a repository-relative path onto a layer's base directory.
    Returns None if the path is outside that directory or is the directory itself.
    """
    if base in ("", "."):
        return candidate

    prefix = f"{base}/"
    if not candidate.startswith(prefix):
        return None

    scoped_path = candidate[len(prefix):]
    # The .gitignore of a directory cannot ignore that directory itself.
    return scoped_path or None


def _read_gitignore_lines(path):
    """
    Read the patterns of a .gitignore file. Returns [] if it cannot be read.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            return file.read().splitlines()
    except OSError as e:
        logging.warning(f"Warning: could not read '{path}': {e}. Skipping it.")
        return []


def _collect_gitignore_layers(matcher, root):
    """
    Add a layer for every .gitignore file in the repository, deepest first.

    Walks top-down and prunes directories that are already ignored, so that a
    .gitignore inside an ignored directory is never read - which is what git does.
    """
    for dir_path, dir_names, file_names in os.walk(root):
        rel_dir = Path(dir_path).relative_to(root).as_posix()

        if GITIGNORE_FILENAME in file_names:
            lines = _read_gitignore_lines(Path(dir_path) / GITIGNORE_FILENAME)
            if lines:
                # os.walk yields a directory before its subdirectories, so the
                # most recently added .gitignore is always the deepest one.
                matcher.add_gitignore_layer(rel_dir, GitIgnoreSpec.from_lines(lines))

        dir_names[:] = [
            d
            for d in sorted(dir_names)
            if not matcher.is_ignored(
                d if rel_dir == "." else f"{rel_dir}/{d}", is_dir=True
            )
        ]


def build_ignore_matcher(root, config_patterns=(), use_gitignore=True):
    """
    Build an IgnoreMatcher for a repository.

    @param root: The repository root.
    @param config_patterns: The 'ignored_paths' entries of the configuration.
    @param use_gitignore: Whether the repository's .gitignore files are honored.
    """
    root = Path(root)
    matcher = IgnoreMatcher(
        root,
        [
            (".", GitIgnoreSpec.from_lines(config_patterns)),
            (".", GitIgnoreSpec.from_lines(DEFAULT_IGNORE_PATTERNS)),
        ],
    )

    if use_gitignore:
        _collect_gitignore_layers(matcher, root)

    return matcher


@lru_cache(maxsize=None)
def _build_ignore_matcher_cached(root, config_patterns, use_gitignore):
    return build_ignore_matcher(root, config_patterns, use_gitignore)


def get_ignore_matcher(root, config_patterns=(), use_gitignore=True):
    """
    Return the IgnoreMatcher for a repository, building it once per repository.

    Scanning for .gitignore files walks the repository, so the result is cached.
    Call reset_ignore_cache() when the repository contents change underneath.
    """
    return _build_ignore_matcher_cached(
        Path(root).resolve(), tuple(config_patterns), bool(use_gitignore)
    )


def reset_ignore_cache():
    """
    Drop the cached matchers. Mostly useful for tests.
    """
    _build_ignore_matcher_cached.cache_clear()
