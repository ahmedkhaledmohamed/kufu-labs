"""Package only reviewed site assets; never deploy a repository root or its secrets."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"


def main():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    files = [
        ROOT / f"{p}.html"
        for p in ["index", "explorations", "problems", "sources", "validation"]
    ]
    files += [ROOT / "site/app.js", ROOT / "site/style.css"]
    files += list((ROOT / "site/records").glob("*.html"))
    files += [
        ROOT / f"site/{p}"
        for p in [
            "catalog.json",
            "build-result.json",
            "validation-results.json",
            "verification.json",
            "README.md",
            "VALIDATION.md",
            "DELIVERY.md",
        ]
    ]
    files += [ROOT / "README.md", ROOT / "WORKSPACE.md"]
    # Linked research/source artifacts are explicit, inert download types.
    tracked = (
        subprocess.check_output(
            ["git", "ls-files", "-z", "--", "projects", "research"], cwd=ROOT
        )
        .decode()
        .split("\0")
    )
    for name in filter(None, tracked):
        source = ROOT / name
        if source.is_file() and (
            source.suffix in {".html", ".md", ".json", ".py", ".cjs", ".patch", ".txt"}
            or source.name in {"COPYING", "UPSTREAM-LICENSE"}
        ):
            files.append(source)
    checksums = {}
    for source in sorted(set(files)):
        relative = source.relative_to(ROOT)
        assert not source.is_symlink(), relative
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        checksums[relative.as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = (
        subprocess.run(
            ["git", "diff", "--quiet", "HEAD"], cwd=ROOT, check=False
        ).returncode
        != 0
    )
    manifest = {
        "source_commit": commit,
        "source_dirty": dirty,
        "files": checksums,
        "execution": "Static browser demos; linked Python is downloadable source, not a server execution endpoint.",
    }
    (OUTPUT / "build-info.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Packaged {len(checksums)} assets; source commit {commit}")


if __name__ == "__main__":
    main()
