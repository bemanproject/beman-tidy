#!/bin/bash
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

set -e
set +x
TOOL=$1
VERSION=$2

echo "Install ${TOOL} at: ${VERSION}"

shopt -s nocasematch
if [ "$TOOL" = "gcc" ]; then
    sudo apt-get remove -y gcc-"$VERSION" g++-"$VERSION" gcc g++
    sudo apt-get install -y gcc-"$VERSION" g++-"$VERSION" lcov

    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-"$VERSION" 10
    sudo update-alternatives --install /usr/bin/gcc g++ /usr/bin/g++-"$VERSION" 10

    sudo update-alternatives --config gcc
    sudo update-alternatives --config g++

    gcc --version
else
    sudo apt-get install -y lsb-release wget software-properties-common gnupg
    wget https://apt.llvm.org/llvm.sh

    sudo bash llvm.sh "${VERSION}"
    sudo apt-get install -y libc++-"$VERSION"-dev lcov
    
    sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-"$VERSION" 10
    sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-"$VERSION" 10

    sudo update-alternatives --config clang
    sudo update-alternatives --config clang++

    clang --version
fi
