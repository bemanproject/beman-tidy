// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#ifndef USES_FEATURE_TEST_MACRO_HPP
#define USES_FEATURE_TEST_MACRO_HPP

#if defined(__cpp_explicit_this_parameter)
void use_deducing_this();
#elif defined(__cpp_concepts)
void use_concepts();
#else
#if __cpp_lib_format >= 201907L
void use_format();
#endif
#endif

#endif
