// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#ifndef USES_ELIF_BARE_FEATURE_TEST_HPP
#define USES_ELIF_BARE_FEATURE_TEST_HPP

#if defined(BEMAN_MY_LIB_USE_DEDUCING_THIS)
void use_deducing_this();
#elif __cpp_concepts
void use_concepts();
#endif

#endif
