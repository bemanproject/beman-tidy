#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
from enum import Enum, auto

class CommentType(Enum):
    LINE = auto()
    BLOCK = auto()

# Currently only supports C/C++ comments
LINE_PREFIX = '//'
BLOCK_START = '/*'
BLOCK_END = '*/'

def determine_comment_style(lines, line_index):
    """
    Determines the comment style at the given line index.
    Returns CommentType or None.
    """
    if line_index < 0 or line_index >= len(lines):
        return None
        
    line = lines[line_index].strip()
    
    # Check for line comments
    if line.startswith(LINE_PREFIX):
        return CommentType.LINE
        
    # Check for block comment start
    if line.startswith(BLOCK_START):
        return CommentType.BLOCK
        
    # Check if inside block comment (look backwards)
    for i in range(line_index - 1, -1, -1):
        prev_line = lines[i].strip()
        if BLOCK_END in prev_line:
            # Found an end marker before a start marker, so we are not inside a block
            return None
            
        if prev_line.startswith(BLOCK_START):
            return CommentType.BLOCK
             
    return None


def iterate_comment_lines(lines, start_index, comment_type):
    """
    Iterates over the lines of a comment block starting at start_index.
    Yields (line_index, line_content).
    Stops when the comment block ends.
    """
    if start_index < 0 or start_index >= len(lines) or comment_type is None:
        return

    i = start_index
    if comment_type == CommentType.LINE:
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                yield i, line
                i += 1
                continue
            if not stripped.startswith(LINE_PREFIX):
                break
            yield i, line
            i += 1

    elif comment_type == CommentType.BLOCK:
        while i < len(lines):
            line = lines[i]
            yield i, line
            if BLOCK_END in line:
                break
            i += 1


def find_in_comment(lines, start_index, comment_type, texts, ignore_case=False):
    """
    Searches for any of the text in texts list within the comment block.
    Returns (line_index, found_text) or (None, None).
    """
    for i, line in iterate_comment_lines(lines, start_index, comment_type):
        if comment_type == CommentType.BLOCK and BLOCK_END in line:
            line = line.split(BLOCK_END)[0]

        found_text = find_in_line(line, texts, ignore_case)
        if found_text:
            return i, found_text
    return None, None


def find_in_line(line, texts, ignore_case=False):
    """
    Checks if line contains any of the texts.
    Optionally ignores case.
    Returns the found text or None.
    """
    if ignore_case:
        line = line.lower()
    for text in texts:
        if (text.lower() if ignore_case else text) in line:
            return text
    return None
