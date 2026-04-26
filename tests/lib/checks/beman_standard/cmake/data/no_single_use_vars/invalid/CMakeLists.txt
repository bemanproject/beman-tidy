# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.23)
project(beman.example VERSION 0.0.1 LANGUAGES CXX)

# Variable only used once - violation
set(SOURCES
    a.cpp
    b.cpp
    c.cpp
)

target_sources(beman.example PRIVATE ${SOURCES})
