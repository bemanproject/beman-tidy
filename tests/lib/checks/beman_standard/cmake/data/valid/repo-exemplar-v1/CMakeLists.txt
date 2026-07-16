# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.30...4.3)

project(
    beman.exemplar
    DESCRIPTION "A Beman Library Exemplar"
    LANGUAGES CXX
    VERSION 0.1.0
)

include(infra/cmake/beman-install-library.cmake)

add_library(beman.exemplar INTERFACE)
add_library(beman::exemplar ALIAS beman.exemplar)

if(BEMAN_EXEMPLAR_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests/beman/exemplar)
endif()

if(BEMAN_EXEMPLAR_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()
