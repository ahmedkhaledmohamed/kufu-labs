"""Fetch hash-checked refine.bio sources without research data or worker test volumes."""

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def main():
    lock = json.loads((PROJECT / "workflow-lock.json").read_text())
    patch = PROJECT / "preserve-zero.patch"
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == lock["patch_sha256"]
    external = ROOT / ".external"
    external.mkdir(exist_ok=True)
    source = external / "refinebio-source.git"
    baseline, patched = external / "refinebio-clean", external / "refinebio-patched"
    if any(path.exists() for path in [source, baseline, patched]):
        raise RuntimeError(
            "Preserve existing refine.bio checkouts; use a fresh lab worktree"
        )

    def git(*args):
        subprocess.run(["git", *map(str, args)], check=True)

    git("init", "--bare", source)
    git(
        "-C",
        source,
        "remote",
        "add",
        "origin",
        "https://github.com/AlexsLemonade/refinebio.git",
    )
    git("-C", source, "config", "remote.origin.promisor", "true")
    git("-C", source, "config", "remote.origin.partialclonefilter", "blob:none")
    git(
        "-C",
        source,
        "fetch",
        "--filter=blob:none",
        "--depth=1",
        "origin",
        lock["upstream_commit"],
    )
    for checkout in [baseline, patched]:
        git(
            "-C",
            source,
            "worktree",
            "add",
            "--detach",
            "--no-checkout",
            checkout,
            lock["upstream_commit"],
        )
        git("-C", checkout, "sparse-checkout", "init", "--cone")
        git(
            "-C",
            checkout,
            "sparse-checkout",
            "set",
            "config",
            "common/data_refinery_common",
            "common/dockerfiles",
            "common/tests/models",
            "foreman/data_refinery_foreman",
            "workers/data_refinery_workers",
            "workers/tests/processors",
        )
        git("-C", checkout, "checkout", "--detach", lock["upstream_commit"])
        assert not (checkout / "test_volume").exists()
        assert not (checkout / "workers/test_volume").exists()
        for name, digest in lock["source_files"].items():
            assert (
                hashlib.sha256((checkout / name).read_bytes()).hexdigest() == digest
            ), name
    git("-C", patched, "apply", patch)
    print(
        json.dumps(
            {
                "upstream_commit": lock["upstream_commit"],
                "patch_sha256": lock["patch_sha256"],
                "source_only": True,
            }
        )
    )


if __name__ == "__main__":
    main()
