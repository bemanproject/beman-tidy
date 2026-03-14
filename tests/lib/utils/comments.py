#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from beman_tidy.lib.utils.comments import (
    BLOCK_ENDS,
    BLOCK_STARTS,
    LINE_PREFIXES,
    CommentType,
    determine_comment_type,
    find_in_comment,
    find_in_line,
    iterate_comment_lines,
)


def test__comments__determine_comment_style__out_of_bounds():
    assert determine_comment_type([], 0) is None
    assert determine_comment_type(["// hi"], -1) is None
    assert determine_comment_type(["// hi"], 1) is None


def test__comments__determine_comment_style__line_comment():
    lines = [
        "int x = 0;\n",
        "// comment\n",
    ]
    assert determine_comment_type(lines, 1) == CommentType.LINE


def test__comments__determine_comment_style__block_comment_start():
    lines = [
        "/* comment start\n",
        " * middle\n",
        " */\n",
    ]
    assert determine_comment_type(lines, 0) == CommentType.BLOCK


def test__comments__determine_comment_style__inside_block_comment():
    lines = [
        "/* comment start\n",
        " * middle\n",
        " */\n",
        "int x = 0;\n",
    ]
    assert determine_comment_type(lines, 1) == CommentType.BLOCK


def test__comments__determine_comment_style__after_block_comment_is_none():
    lines = [
        "/* comment start\n",
        " */\n",
        "int x = 0;\n",
    ]
    assert determine_comment_type(lines, 2) is None


def test__comments__determine_comment_style__single_line_block_comment():
    lines = [
        "/* single-line block comment */\n",
        "int x = 0;\n",
    ]
    assert determine_comment_type(lines, 0) == CommentType.BLOCK


def test__comments__determine_comment_style__after_single_line_block_comment():
    lines = [
        "/* single-line block comment */\n",
        "int x = 0;\n",
    ]
    assert determine_comment_type(lines, 1) is None


def test__comments__determine_comment_style__not_inside_single_line_block_comment():
    lines = [
        "/* SPDX-License-Identifier: Apache-2.0 */\n",
        "\n",
        "/* Copyright notice */\n",
    ]
    # Line 2 (the blank line) should NOT be considered inside a block comment
    assert determine_comment_type(lines, 1) is None
    # Line 2 (the Copyright line) is its own single-line block comment
    assert determine_comment_type(lines, 2) == CommentType.BLOCK


def test__comments__iterate_comment_lines__line_comment_block_with_blank_lines():
    lines = [
        "// a\n",
        "\n",
        "// b\n",
        "int x = 0;\n",
        "// c\n",  # should not be reached
    ]
    out = list(iterate_comment_lines(lines, 0, CommentType.LINE))
    assert out == [
        (0, "// a\n"),
        (1, "\n"),
        (2, "// b\n"),
    ]


def test__comments__iterate_comment_lines__block_comment_until_end_marker():
    lines = [
        "/* a\n",
        " * b\n",
        " */ trailing\n",
        "int x = 0;\n",
    ]
    out = list(iterate_comment_lines(lines, 0, CommentType.BLOCK))
    assert out == [
        (0, "/* a\n"),
        (1, " * b\n"),
        (2, " */ trailing\n"),
    ]


def test__comments__iterate_comment_lines__invalid_start_index_or_type_yields_nothing():
    lines = ["// a\n"]
    assert list(iterate_comment_lines(lines, -1, CommentType.LINE)) == []
    assert list(iterate_comment_lines(lines, 0, None)) == []


def test__comments__iterate_comment_lines__single_line_block_comment():
    lines = [
        "/* single-line block */\n",
        "int x = 0;\n",
    ]
    out = list(iterate_comment_lines(lines, 0, CommentType.BLOCK))
    assert out == [
        (0, "/* single-line block */\n"),
    ]


def test__comments__find_in_line__case_sensitive_and_insensitive():
    assert find_in_line("Hello World", ["world"]) is None
    assert find_in_line("Hello World", ["world"], ignore_case=True) == "world"
    assert find_in_line("abc", ["x", "b"]) == "b"


def test__comments__find_in_comment__line_comment_finds_text():
    lines = [
        "// SPDX-License-Identifier: X\n",
        "// Copyright 2026 Durlea Andrei\n",
        "int x = 0;\n",
    ]
    line_idx, found = find_in_comment(lines, 1, CommentType.LINE, ["copyright"], ignore_case=True)
    assert line_idx == 1
    assert found == "copyright"


def test__comments__find_in_comment__block_comment_finds_text_before_end():
    lines = [
        "/* SPDX-License-Identifier: X\n",
        " * Copyright 2026 Beman\n",
        " */\n",
    ]
    line_idx, found = find_in_comment(lines, 0, CommentType.BLOCK, ["copyright"], ignore_case=True)
    assert line_idx == 1
    assert found == "copyright"


def test__comments__find_in_comment__block_comment_ignores_text_after_block_end_on_same_line():
    # The implementation truncates the line at '*/' before searching.
    lines = [
        "/* header */ copyright SHOULD_NOT_MATCH\n",
        "int x = 0;\n",
    ]
    line_idx, found = find_in_comment(lines, 0, CommentType.BLOCK, ["copyright"], ignore_case=True)
    assert (line_idx, found) == (None, None)


def test__comments__find_in_comment__single_line_block_comment_finds_text():
    lines = [
        "/* SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception */\n",
        "\n",
        "/* Copyright 2026 Beman */\n",
    ]
    # Should find copyright in the separate single-line block comment on line 2
    line_idx, found = find_in_comment(lines, 2, CommentType.BLOCK, ["copyright"], ignore_case=True)
    assert line_idx == 2
    assert found == "copyright"


def test__comments__find_in_comment__does_not_find_in_next_single_line_block():
    lines = [
        "/* SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception */\n",
        "\n",
        "/* Copyright 2026 Beman */\n",
    ]
    # Starting search from line 1 (after SPDX single-line comment) should NOT find copyright
    # because we're not inside a block comment at line 1
    line_idx, found = find_in_comment(lines, 1, None, ["copyright"], ignore_case=True)
    assert (line_idx, found) == (None, None)


def test__comments__comment_markers_are_non_empty():
    assert LINE_PREFIXES
    assert BLOCK_STARTS
    assert BLOCK_ENDS
