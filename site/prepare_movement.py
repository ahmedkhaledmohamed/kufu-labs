"""Prepare two exact source-only movement checkouts for synthetic CI regressions."""

from __future__ import annotations

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
    external = ROOT / ".external"
    external.mkdir(exist_ok=True)
    for name in ["movement-patched", "movement-clean"]:
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
        git("sparse-checkout", "set", "movement")
        git(
            "-c",
            "remote.origin.promisor=true",
            "fetch",
            "--filter=blob:none",
            "--depth=1",
            "origin",
            SOURCE,
        )
        git("checkout", "--detach", "FETCH_HEAD")
        revision = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
        assert revision == SOURCE
        if name == "movement-patched":
            git(
                "apply",
                str(ROOT / "projects/movement-edit-filtering/movement-pilot.patch"),
            )


if __name__ == "__main__":
    main()
