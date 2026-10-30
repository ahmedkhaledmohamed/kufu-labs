"""Verify saved deletion provenance against exact movement source and patch."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = json.loads((PROJECT / "deletion-profile.json").read_text())
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    assert revision == profile["source_revision"]
    assert digest(checkout / "LICENSE") == profile["license_sha256"]
    module = checkout / "movement/napari/convert.py"
    assert digest(module) == profile[f"{args.expect}_convert_sha256"]
    patch_path = PROJECT / "deletion-provenance.patch"
    assert digest(patch_path) == profile["patch_sha256"]
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=checkout)
    if args.expect == "baseline":
        assert not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=checkout
        ).strip(), "Baseline must remain unmodified"
    else:
        assert diff == patch_path.read_bytes(), "Apply only the recorded deletion patch"
    tests = (
        ROOT / ".external/movement-deletion-patched/tests/test_deletion_provenance.py"
    )
    assert digest(tests) == profile["tests_sha256"]
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    sys.path.insert(0, str(checkout))
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="kufu-deletion-") as temporary:
        with patch.object(Path, "home", return_value=Path(temporary)):
            import movement
        from movement.napari import convert

        assert Path(movement.__file__).resolve().is_relative_to(checkout)
        assert Path(convert.__file__).resolve() == module
        import pytest

        xml = output.with_suffix(".xml")
        with (
            output.with_suffix(".log").open("w") as log,
            contextlib.redirect_stdout(log),
            contextlib.redirect_stderr(log),
        ):
            result = pytest.main(
                [
                    "--noconftest",
                    "-o",
                    "addopts=",
                    str(tests),
                    "-q",
                    f"--junitxml={xml}",
                ]
            )
        assert result == (1 if args.expect == "baseline" else 0)
        cases = list(ET.parse(xml).getroot().iter("testcase"))
        assert len(cases) == profile["constructed_cases"]
        assert not any(
            c.find("error") is not None or c.find("skipped") is not None for c in cases
        )
        failures = sorted(
            c.attrib["name"] for c in cases if c.find("failure") is not None
        )
        assert failures == (
            sorted(profile["baseline_failures"]) if args.expect == "baseline" else []
        )

        spec = importlib.util.spec_from_file_location("deletion_cases", tests)
        helpers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helpers)
        observations = {}
        for name, delete, move in [
            ("deletion_only", True, False),
            ("deletion_and_move", True, True),
            ("never_detected", False, False),
        ]:
            first = helpers.convert(helpers.dataset(), delete=delete, move=move)
            second = helpers.convert(first)
            target = {"time": 1 / 30, "keypoint": "nose", "individual": "mouse_0"}

            if name == "never_detected":
                target = {"time": 3 / 30, "keypoint": "tail", "individual": "mouse_1"}

            def flag(ds, target=target):
                return bool(ds.edited.sel(target).item()) if "edited" in ds else None

            observations[name] = {
                "flag_first": flag(first),
                "flag_second": flag(second),
            }
    report = {
        "source_revision": revision,
        "expectation": args.expect,
        "patch_sha256": profile["patch_sha256"] if args.expect == "patched" else None,
        "convert_sha256": digest(module),
        "input_kind": "Constructed poses: 4 frames, 2 keypoints, 2 individuals at 30 Hz; no recordings",
        "tests": len(cases),
        "passed": len(cases) - len(failures),
        "failed": failures,
        "native_reopen_cycles": [1, 2, 4],
        "observations": observations,
        "qt_or_canvas_created": False,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["numpy", "pandas", "xarray", "pytest"]
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
