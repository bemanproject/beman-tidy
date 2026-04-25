# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.23)
project(beman.example VERSION 0.0.1 LANGUAGES CXX)

install(
    TARGETS beman.example
    EXPORT beman.example-targets
    FILE_SET HEADERS
)
