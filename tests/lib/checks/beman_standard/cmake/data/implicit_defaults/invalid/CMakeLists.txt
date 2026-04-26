# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.23)
project(beman.example VERSION 0.0.1 LANGUAGES CXX)

install(
    TARGETS beman.example
    EXPORT beman.example-targets
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME
        DESTINATION ${CMAKE_INSTALL_BINDIR}
    FILE_SET HEADERS
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
