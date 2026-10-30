"""Prepare two exact source-only movement checkouts for synthetic CI regressions."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = json.loads(
    (
        ROOT / "projects/movement-edit-filtering/movement-pilot-environment.json"
    ).read_text()
)["source_revision"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deletion", action="store_true")
    args = parser.parse_args()
    profile = (
        json.loads(
            (
                ROOT / "projects/movement-edit-filtering/deletion-profile.json"
            ).read_text()
        )
        if args.deletion
        else None
    )
    revision = profile["source_revision"] if profile else SOURCE
    patch = (
        ROOT
        / "projects/movement-edit-filtering"
        / ("deletion-provenance.patch" if profile else "movement-pilot.patch")
    )
    if profile:
        assert hashlib.sha256(patch.read_bytes()).hexdigest() == profile["patch_sha256"]
    prefix = "movement-deletion" if profile else "movement"
    external = ROOT / ".external"
    external.mkdir(exist_ok=True)
    for name in [f"{prefix}-patched", f"{prefix}-clean"]:
        checkout = external / name
        if checkout.exists():
            raise RuntimeError(
                f"{name} already exists; preserve it and use a fresh checkout"
            )
        subprocess.run(["git", "init", str(checkout)], check=True)

        def git(*args, checkout=checkout):
            return subprocess.run(["git", "-C", str(checkout), *args], check=True)

        git(
            "remote",
            "add",
            "origin",
            "https://github.com/neuroinformatics-unit/movement.git",
        )
        git("sparse-checkout", "init", "--cone")
        git(
            "sparse-checkout",
            "set",
            "movement",
            *(
                ["tests/test_unit/test_napari_plugin", "tests/fixtures"]
                if profile
                else []
            ),
        )
        git(
            "-c",
            "remote.origin.promisor=true",
            "fetch",
            "--filter=blob:none",
            "--depth=1",
            "origin",
            revision,
        )
        git("checkout", "--detach", "FETCH_HEAD")
        observed = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
        assert observed == revision
        if name.endswith("-patched"):
            git("apply", str(patch))
            if profile:
                git("add", "-N", "tests/test_deletion_provenance.py")


if __name__ == "__main__":
    main()
