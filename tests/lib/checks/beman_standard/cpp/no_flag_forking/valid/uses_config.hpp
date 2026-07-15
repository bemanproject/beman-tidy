// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#ifndef USES_CONFIG_HPP
#define USES_CONFIG_HPP

#include <beman/my_lib/config.hpp>

#if BEMAN_MY_LIB_USE_DEDUCING_THIS
void use_deducing_this();
#endif

// Do not flag __cpp_* mentions in comments, e.g. __cpp_explicit_this_parameter

#endif
