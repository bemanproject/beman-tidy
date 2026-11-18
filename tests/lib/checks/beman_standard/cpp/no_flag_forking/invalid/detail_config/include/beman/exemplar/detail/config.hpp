// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

// Only include/beman/<library>/config.hpp is exempt, not nested config headers.
#if defined(__cpp_lib_three_way_comparison)
#define BEMAN_EXEMPLAR_DETAIL_USE_SPACESHIP 1
#endif
