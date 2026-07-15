# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.30...4.3)

project(beman.exemplar LANGUAGES CXX)

include(FetchContent)

FetchContent_Declare(
    task
    GIT_REPOSITORY https://github.com/bemanproject/task
    GIT_TAG main
)

add_library(beman.exemplar INTERFACE)
