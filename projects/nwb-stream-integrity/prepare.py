"""Prepare exact source-only baseline and patched NWB Inspector worktrees."""

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def main():
    metadata = json.loads((PROJECT / "verification.json").read_text())
    revision = metadata["upstream_commit"]
    patch = PROJECT / "non-consuming-shape.patch"
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == metadata["patch_sha256"]
    external = ROOT / ".external"
    external.mkdir(exist_ok=True)
    source = external / "nwb-source.git"
    baseline = external / "nwb-clean"
    patched = external / "nwb-patched"
    if any(path.exists() for path in [source, baseline, patched]):
        raise RuntimeError(
            "NWB checkouts already exist; preserve them and use a fresh lab worktree"
        )

    def git(*args):
        return subprocess.run(["git", *map(str, args)], check=True)

    git("init", "--bare", source)
    git(
        "-C",
        source,
        "remote",
        "add",
        "origin",
        "https://github.com/NeurodataWithoutBorders/nwbinspector.git",
    )
    git("-C", source, "fetch", "--filter=blob:none", "--depth=1", "origin", revision)
    for checkout in [baseline, patched]:
        git(
            "-C",
            source,
            "worktree",
            "add",
            "--detach",
            "--no-checkout",
            checkout,
            revision,
        )
        git("-C", checkout, "sparse-checkout", "init", "--cone")
        git("-C", checkout, "sparse-checkout", "set", "src", "tests/unit_tests")
        git("-C", checkout, "checkout", "--detach", revision)
        observed = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
        ).strip()
        assert observed == revision
    git("-C", patched, "apply", patch)
    print(
        json.dumps(
            {
                "upstream_commit": revision,
                "patch_sha256": metadata["patch_sha256"],
                "prepared": True,
            }
        )
    )


if __name__ == "__main__":
    main()
