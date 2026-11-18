# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

cmake_minimum_required(VERSION 3.30...4.3)

project(beman.exemplar LANGUAGES CXX)

add_library(beman.exemplar INTERFACE)
add_subdirectory(examples)
