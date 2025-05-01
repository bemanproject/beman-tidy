#!/usr/bin/env python3

import argparse
import filecmp
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

def directory_compare(dir1, dir2, ignore):
    compared = filecmp.dircmp(dir1, dir2, ignore=ignore)
    if compared.left_only or compared.right_only or compared.diff_files:
        return False
    for common_dir in compared.common_dirs:
        path1 = os.path.join(dir1, common_dir)
        path2 = os.path.join(dir2, common_dir)
        if not directory_compare(path1, path2, ignore):
            return False
    return True

class Submodule:
    def __init__(self, dirpath, url, commit_hash):
        self.dirpath = dirpath
        self.url = url
        self.commit_hash = commit_hash

def get_submodule(dir):
    with open(os.path.join(dir, ".bemanmodule"), 'r') as f:
        return Submodule(dir, f.readline().strip(), f.readline().strip())

def find_submodule_dirs_in(dir):
    assert os.path.isdir(dir)
    result = []
    for dirpath, _, filenames in os.walk(dir):
        if ".bemanmodule" in filenames:
            result.append(dirpath)
    return result

def pull_submodule_into_tmpdir(submodule):
    tmpdir = tempfile.TemporaryDirectory()
    subprocess.run(
        ["git", "clone", submodule.url, tmpdir.name], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", tmpdir.name, "reset", "--hard", submodule.commit_hash],
        capture_output=True, check=True)
    return tmpdir

def submodule_pull(submodule):
    print(
        "Pulling", submodule.url, "at commit", submodule.commit_hash, "to",
        submodule.dirpath)
    tmpdir = pull_submodule_into_tmpdir(submodule)
    shutil.rmtree(os.path.join(tmpdir.name, ".git"))
    shutil.copytree(tmpdir.name, submodule.dirpath, dirs_exist_ok=True)

def submodule_check(submodule):
    print(
        "Checking", submodule.dirpath, "equivalence with", submodule.url, "at commit",
        submodule.commit_hash)
    tmpdir = pull_submodule_into_tmpdir(submodule)
    if not directory_compare(tmpdir.name, submodule.dirpath, [".bemanmodule", ".git"]):
        print(
            "Mismatch between", submodule.dirpath, "and", submodule.url, "at commit",
            submodule.commit_hash, file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Beman pseudo-submodule tool")
    parser.add_argument('--pull', help="Update all pseudo-submodules to latest main",
                        action="store_true")
    parser.add_argument('--check', help="Check pseudo-submodule consistency",
                        action="store_true")
    args = parser.parse_args();
    script_path = pathlib.Path(__file__).resolve().parent
    script_parent = script_path.parent
    submodule_dirs = find_submodule_dirs_in(script_parent)
    print("Found bemanmodules at: ", submodule_dirs)
    submodules = [get_submodule(dir) for dir in submodule_dirs]
    for submodule in submodules:
        if args.pull:
            submodule_pull(submodule)
        elif args.check:
            submodule_check(submodule)
        else:
            raise Exception("Specify either --pull or --check")

if __name__ == "__main__":
    main()
