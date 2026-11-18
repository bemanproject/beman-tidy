// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#ifndef USES_CONFIG_HPP
#define USES_CONFIG_HPP

#include <beman/my_lib/config.hpp>

#if BEMAN_MY_LIB_USE_DEDUCING_THIS
void use_deducing_this();
#endif

// Do not flag __cpp_* mentions in comments, e.g. __cpp_explicit_this_parameter
/*
#if __cpp_concepts
#endif
*/

#if BEMAN_MY_LIB_USE_RANGES // replaces __cpp_lib_ranges
void use_ranges();
#endif

#if BEMAN_MY_LIB_USE_FORMAT /* replaces __cpp_lib_format */
void use_format();
#endif

// Identifiers that merely contain __cpp_ are not feature test macros.
#if 202207 <= disabled__cpp_lib_forward_like
void use_forward_like();
#endif

#if __cplusplus >= 202002L
void use_cpp20();
#endif

inline constexpr const char* ftm_name = "__cpp_concepts";

#endif
