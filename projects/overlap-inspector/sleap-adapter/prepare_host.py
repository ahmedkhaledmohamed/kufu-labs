# SPDX-License-Identifier: GPL-3.0-only
"""Prepare source-only clean/patched SLEAP worktrees; never fetch test assets."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination", type=Path, default=ROOT / ".external/sleap-host"
    )
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        raise SystemExit(
            "Destination already exists; choose a fresh isolated directory."
        )
    lock = json.loads((HERE / "source-lock.json").read_text())
    for name, expected in lock["adapter_sha256"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Adapter digest mismatch: {name}")
    destination.mkdir(parents=True)
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")

    def git(*args):
        subprocess.run(["git", *map(str, args)], check=True, env=env)

    bare = destination / "source.git"
    git("init", "--bare", bare)
    git("--git-dir", bare, "remote", "add", "origin", lock["host_repository"])
    git(
        "--git-dir",
        bare,
        "fetch",
        "--filter=blob:none",
        "--depth=1",
        "origin",
        lock["host_revision"],
    )
    for name in ("baseline", "patched"):
        worktree = destination / name
        git(
            "--git-dir",
            bare,
            "worktree",
            "add",
            "--detach",
            "--no-checkout",
            worktree,
            "FETCH_HEAD",
        )
        git("-C", worktree, "sparse-checkout", "init", "--cone")
        git("-C", worktree, "sparse-checkout", "set", "sleap", "tests/gui")
        git("-C", worktree, "checkout", "--detach", lock["host_revision"])
    patched = destination / "patched"
    git("-C", patched, "apply", "--check", HERE / "sleap-1.6.6.patch")
    git("-C", patched, "apply", HERE / "sleap-1.6.6.patch")
    shutil.copyfile(
        HERE / "pair_overlap.py", patched / "sleap/gui/dialogs/pair_overlap.py"
    )
    print("Prepared baseline and patched SLEAP sources; no recordings or weights.")


if __name__ == "__main__":
    main()
