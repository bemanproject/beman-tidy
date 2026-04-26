# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.23)
project(beman.example VERSION 0.0.1 LANGUAGES CXX)

# Variable used multiple times - OK
set(BEMAN_EXAMPLE_VERSION 1.0)
message(STATUS "Version: ${BEMAN_EXAMPLE_VERSION}")
message(STATUS "Again: ${BEMAN_EXAMPLE_VERSION}")

# Cache variable - exempt
set(BEMAN_EXAMPLE_BUILD_TESTS ON CACHE BOOL "Build tests")

target_sources(beman.example
    PRIVATE
        a.cpp
        b.cpp
        c.cpp
)
