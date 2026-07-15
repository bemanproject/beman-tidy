# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

find_package(GTest REQUIRED)

add_executable(beman.exemplar.tests.identity)
target_link_libraries(
    beman.exemplar.tests.identity
    PRIVATE beman::exemplar GTest::gtest_main
)
