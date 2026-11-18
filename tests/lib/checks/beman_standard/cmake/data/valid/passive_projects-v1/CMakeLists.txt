# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.30...4.3)

project(
    beman.exemplar
    DESCRIPTION "A Beman Library Exemplar"
    LANGUAGES CXX
    VERSION 0.1.0
)

add_library(beman.exemplar INTERFACE)
add_library(beman::exemplar ALIAS beman.exemplar)

target_sources(
    beman.exemplar
    PUBLIC FILE_SET HEADERS BASE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/include"
)
