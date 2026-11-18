# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.30...4.3)

project(beman.exemplar LANGUAGES CXX)

# Only a default: the user's CMAKE_CXX_STANDARD wins.
if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 23)
endif()

add_library(beman.exemplar INTERFACE)
