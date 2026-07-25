#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path

import pytest

from beman_tidy.lib.utils.config import is_ignored
from beman_tidy.lib.utils.file import get_cpp_files, get_matched_paths


def make_repo(root, files):
    """
    Create a repository layout: a {relative path: content} mapping.
    """
    for relative_path, content in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return root


def repo_info_for(root, **config):
    return {"top_level": root, "config": config}


def test_gitignore_is_honored_by_default(tmp_path):
    """Test that .gitignore patterns are applied without any configuration."""
    root = make_repo(tmp_path, {".gitignore": "*.pyc\nbuild/\n"})
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("a.pyc")) is True
    assert is_ignored(repo_info, Path("nested/a.pyc")) is True
    assert is_ignored(repo_info, Path("build")) is True
    assert is_ignored(repo_info, Path("build/main.o")) is True
    assert is_ignored(repo_info, Path("src/main.cpp")) is False


def test_gitignore_can_be_disabled(tmp_path):
    """Test that use_gitignore: false turns the .gitignore source off."""
    root = make_repo(tmp_path, {".gitignore": "*.pyc\ngenerated/\n"})
    repo_info = repo_info_for(root, use_gitignore=False)

    assert is_ignored(repo_info, Path("a.pyc")) is False
    assert is_ignored(repo_info, Path("generated/a.cpp")) is False
    # The built-in ignores still apply.
    assert is_ignored(repo_info, Path("build/main.o")) is True


def test_missing_gitignore(tmp_path):
    """Test that a repository without a .gitignore behaves as before."""
    root = make_repo(tmp_path, {"src/main.cpp": ""})
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("src/main.cpp")) is False
    assert is_ignored(repo_info, Path("build/main.o")) is True


@pytest.mark.parametrize(
    "pattern, ignored, not_ignored",
    [
        # Comments and blank lines are not patterns.
        ("# comment\n\nsecret.txt\n", "secret.txt", "comment"),
        # A leading slash anchors a pattern to the repository root.
        ("/build_root\n", "build_root", "nested/build_root"),
        # Without a slash, a pattern matches at any depth.
        ("generated\n", "a/b/generated/f.cpp", "src/main.cpp"),
        # '**' spans directories.
        ("**/vendor/**\n", "a/vendor/b/c.cpp", "a/vendors/b.cpp"),
        # A trailing slash restricts a pattern to directories.
        ("logs/\n", "logs/today.txt", "logs.txt"),
        # Character ranges are supported.
        ("*.o[123]\n", "a.o2", "a.o4"),
        # An escaped '!' is a literal, not a negation.
        ("\\!important.txt\n", "!important.txt", "important.txt"),
    ],
)
def test_gitignore_pattern_syntax(tmp_path, pattern, ignored, not_ignored):
    """Test that .gitignore pattern syntax is interpreted the way git does."""
    root = make_repo(tmp_path, {".gitignore": pattern})
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path(ignored)) is True
    assert is_ignored(repo_info, Path(not_ignored)) is False


def test_gitignore_negation(tmp_path):
    """Test that a negated pattern re-includes a path."""
    root = make_repo(tmp_path, {".gitignore": "*.hpp\n!keep.hpp\n"})
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("a.hpp")) is True
    assert is_ignored(repo_info, Path("keep.hpp")) is False


def test_gitignore_negation_under_ignored_directory(tmp_path):
    """Test that a path under an ignored directory cannot be re-included."""
    root = make_repo(tmp_path, {".gitignore": "generated/\n!generated/keep.hpp\n"})
    repo_info = repo_info_for(root)

    # git: "It is not possible to re-include a file if a parent directory of
    # that file is excluded."
    assert is_ignored(repo_info, Path("generated/keep.hpp")) is True


def test_nested_gitignore(tmp_path):
    """Test that a .gitignore applies relative to its own directory."""
    root = make_repo(
        tmp_path,
        {
            ".gitignore": "root_only.txt\n",
            "docs/.gitignore": "draft.md\n",
        },
    )
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("docs/draft.md")) is True
    # The nested pattern does not leak outside its directory.
    assert is_ignored(repo_info, Path("draft.md")) is False
    # The root pattern still applies inside the nested directory.
    assert is_ignored(repo_info, Path("docs/root_only.txt")) is True


def test_nested_gitignore_overrides_parent(tmp_path):
    """Test that the deepest .gitignore wins."""
    root = make_repo(
        tmp_path,
        {
            ".gitignore": "*.md\n",
            "docs/.gitignore": "!published.md\n",
        },
    )
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("docs/published.md")) is False
    assert is_ignored(repo_info, Path("docs/draft.md")) is True
    assert is_ignored(repo_info, Path("published.md")) is True


def test_nested_gitignore_inside_ignored_directory_is_not_read(tmp_path):
    """Test that a .gitignore below an ignored directory is never applied."""
    root = make_repo(
        tmp_path,
        {
            ".gitignore": "vendor/\n",
            "vendor/.gitignore": "!keep.cpp\n",
        },
    )
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("vendor/keep.cpp")) is True


def test_config_overrides_gitignore(tmp_path):
    """Test that ignored_paths has the last word over .gitignore."""
    root = make_repo(tmp_path, {".gitignore": "*.hpp\n"})
    repo_info = repo_info_for(root, ignored_paths=["!include/beman/api.hpp"])

    # Re-included by the configuration...
    assert is_ignored(repo_info, Path("include/beman/api.hpp")) is False
    # ...while everything else the .gitignore covers stays ignored.
    assert is_ignored(repo_info, Path("include/beman/other.hpp")) is True


def test_config_cannot_rescue_paths_below_an_ignored_directory(tmp_path):
    """Test that not even ignored_paths can re-include below an ignored directory."""
    root = make_repo(tmp_path, {".gitignore": "generated/\n"})
    repo_info = repo_info_for(root, ignored_paths=["!generated/api.hpp"])

    # git excludes the whole directory, so nothing below it can come back:
    # the repository has to ignore 'generated/*' rather than 'generated/'.
    assert is_ignored(repo_info, Path("generated/api.hpp")) is True


def test_config_rescues_paths_below_an_ignored_directory_content_pattern(tmp_path):
    """Test the git idiom for re-including: ignore the contents, not the directory."""
    root = make_repo(tmp_path, {".gitignore": "generated/*\n"})
    repo_info = repo_info_for(root, ignored_paths=["!generated/api.hpp"])

    assert is_ignored(repo_info, Path("generated/api.hpp")) is False
    assert is_ignored(repo_info, Path("generated/other.hpp")) is True


def test_config_patterns_use_gitignore_syntax(tmp_path):
    """Test that ignored_paths entries accept .gitignore pattern syntax."""
    root = make_repo(tmp_path, {"src/main.cpp": ""})
    repo_info = repo_info_for(
        root,
        ignored_paths=["*.inc", "/anchored.hpp", "**/detail/**"],
        use_gitignore=False,
    )

    assert is_ignored(repo_info, Path("a/b.inc")) is True
    assert is_ignored(repo_info, Path("anchored.hpp")) is True
    assert is_ignored(repo_info, Path("nested/anchored.hpp")) is False
    assert is_ignored(repo_info, Path("include/detail/impl.hpp")) is True


def test_mandatory_files_are_never_ignored(tmp_path, caplog):
    """Test that a .gitignore cannot exclude README.md or LICENSE."""
    root = make_repo(tmp_path, {".gitignore": "README.md\nLICENSE\n*.md\n"})
    repo_info = repo_info_for(root)

    assert is_ignored(repo_info, Path("README.md")) is False
    assert is_ignored(repo_info, Path("LICENSE")) is False
    assert "mandatory" in caplog.text
    # Other markdown files are still ignored.
    assert is_ignored(repo_info, Path("CHANGELOG.md")) is True


def test_gitignore_applies_to_file_generators(tmp_path):
    """Test that the file generators skip .gitignore-ignored paths."""
    root = make_repo(
        tmp_path,
        {
            ".gitignore": "generated/\nscratch.cpp\n",
            "src/main.cpp": "",
            "src/scratch.cpp": "",
            "generated/api.cpp": "",
            "generated/.gitignore": "!api.cpp\n",
        },
    )
    repo_info = repo_info_for(root)

    from beman_tidy.lib.utils.config import get_ignore_matcher

    found = get_cpp_files(root, ignores=get_ignore_matcher(repo_info))

    assert found == [Path("src/main.cpp")]


def test_generators_accept_plain_pattern_lists(tmp_path):
    """Test that the generators still accept a plain list of patterns."""
    root = make_repo(tmp_path, {"src/main.cpp": "", "src/gen/a.cpp": ""})

    found = get_matched_paths(root, {".cpp"}, ignores=["gen/"])

    assert found == [Path("src/main.cpp")]


def test_generators_keep_pattern_list_order(tmp_path):
    """Test that a caller's pattern order is not rearranged: the last match wins."""
    root = make_repo(tmp_path, {"gen/a.cpp": "", "gen/keep.cpp": ""})

    found = get_matched_paths(root, {".cpp"}, ignores=["gen/*", "!gen/keep.cpp"])

    assert found == [Path("gen/keep.cpp")]
