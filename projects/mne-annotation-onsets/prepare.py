"""Prepare source-only MNE baseline and candidate checkouts."""

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def main():
    profile = json.loads((PROJECT / "profile.json").read_text())
    patch = PROJECT / "preserve-interior-onsets.patch"
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == profile["patch_sha256"]
    external = ROOT / ".external"
    external.mkdir(exist_ok=True)
    for name in ["mne-clean", "mne-patched"]:
        checkout = external / name
        if checkout.exists():
            raise RuntimeError(
                "Preserve existing MNE checkouts; use a fresh lab worktree"
            )

        def git(*args, checkout=checkout):
            return subprocess.run(["git", "-C", str(checkout), *args], check=True)

        subprocess.run(["git", "init", str(checkout)], check=True)
        git("remote", "add", "origin", "https://github.com/mne-tools/mne-python.git")
        # Source and package metadata only; never check out recording fixtures.
        git(
            "sparse-checkout",
            "set",
            "--no-cone",
            "/*",
            "!/*/",
            "/mne/**/*.py",
            "/mne/**/*.pyi",
            "/mne/**/*.json",
            "/mne/data/*.dat",
        )
        git(
            "fetch",
            "--depth=1",
            "--filter=blob:none",
            "origin",
            profile["source_revision"],
        )
        git("checkout", "--detach", "FETCH_HEAD")
        assert (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
            ).strip()
            == profile["source_revision"]
        )
        assert (
            hashlib.sha256((checkout / "LICENSE.txt").read_bytes()).hexdigest()
            == profile["license_sha256"]
        )
        if name == "mne-patched":
            git("apply", str(patch))


if __name__ == "__main__":
    main()
