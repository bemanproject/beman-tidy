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
