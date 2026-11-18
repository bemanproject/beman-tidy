// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#ifndef BEMAN_EXEMPLAR_CONFIG_HPP
#define BEMAN_EXEMPLAR_CONFIG_HPP

// The library's config.hpp may probe feature test macros in its fallback for users
// who vendor the include/ directory without config_generated.hpp.
#if !defined(__has_include) || __has_include(<beman/exemplar/config_generated.hpp>)
    #include <beman/exemplar/config_generated.hpp>
#else
    #include <version>
    #if defined(__cpp_explicit_this_parameter) && __cpp_explicit_this_parameter >= 202110L
        #define BEMAN_EXEMPLAR_USE_DEDUCING_THIS() 1
    #else
        #define BEMAN_EXEMPLAR_USE_DEDUCING_THIS() 0
    #endif
#endif

#endif
