"""Assess movement PR 1190 against pinned upstream and existing Kufu cases."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", choices=["base", "head"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rendered", action="store_true")
    args = parser.parse_args()
    profile = json.loads((PROJECT / "upstream-1190-profile.json").read_text())
    checkout = ROOT / f".external/movement-1190-{args.expect}"
    head = ROOT / ".external/movement-1190-head"
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    assert revision == profile[f"{args.expect}_revision"]
    assert not subprocess.check_output(
        ["git", "-C", str(checkout), "status", "--porcelain"]
    ).strip(), "Preserve the upstream checkout unchanged"
    assert digest(checkout / "LICENSE") == profile["license_sha256"]
    module = checkout / "movement/napari/convert.py"
    assert digest(module) == profile[f"{args.expect}_convert_sha256"]
    upstream_tests = head / "tests/test_unit/test_napari_plugin/test_convert.py"
    assert digest(upstream_tests) == profile["head_tests_sha256"]
    local_patch = PROJECT / "deletion-provenance.patch"
    assert digest(local_patch) == profile["local_patch_sha256"]
    original = json.loads((PROJECT / "deletion-profile.json").read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    os.environ.setdefault("QT_API", "pyqt6")
    sys.path.insert(0, str(checkout))

    def offline(*unused, **kwargs):
        raise OSError("Network disabled during constructed upstream comparison")

    socket.create_connection = offline
    socket.socket.connect = offline
    started = time.monotonic()
    with (
        tempfile.TemporaryDirectory(prefix="kufu-upstream-") as temporary,
        contextlib.ExitStack() as log_files,
    ):
        with patch.object(Path, "home", return_value=Path(temporary)):
            import movement
        from movement.napari import convert

        assert Path(movement.__file__).resolve().is_relative_to(checkout)
        assert Path(convert.__file__).resolve() == module
        import pytest

        # Reuse the exact existing tests without applying the local repair.
        test_patch = local_patch.read_text().split(
            "+++ b/tests/test_deletion_provenance.py\n", 1
        )[1]
        test_source = "".join(
            line[1:]
            for line in test_patch.splitlines(keepends=True)
            if line.startswith("+")
        )
        tests = Path(temporary) / "test_deletion_provenance.py"
        tests.write_text(test_source)
        assert digest(tests) == profile["local_tests_sha256"]
        suites = {}
        for name, file, plugins in [
            ("independent", tests, []),
            (
                "upstream_conversion",
                upstream_tests,
                [
                    "-p",
                    "pytestqt.plugin",
                    "-p",
                    "napari.utils._testsupport",
                    "-p",
                    "tests.fixtures.datasets",
                    "-p",
                    "tests.fixtures.napari",
                ],
            ),
        ]:
            xml = args.output / f"{name}.xml"
            log = log_files.enter_context((args.output / f"{name}.log").open("w"))
            with (
                contextlib.redirect_stdout(log),
                contextlib.redirect_stderr(log),
            ):
                result = pytest.main(
                    [
                        "--noconftest",
                        "-o",
                        "addopts=",
                        "-p",
                        "no:cacheprovider",
                        *plugins,
                        str(file),
                        "-q",
                        f"--junitxml={xml}",
                    ]
                )
            cases = list(ET.parse(xml).getroot().iter("testcase"))
            assert not any(
                c.find("error") is not None or c.find("skipped") is not None
                for c in cases
            )
            failures = sorted(
                c.attrib["name"] for c in cases if c.find("failure") is not None
            )
            assert len(cases) == (15 if name == "independent" else 49)
            expected = []
            if args.expect == "base":
                expected = (
                    sorted(original["baseline_failures"])
                    if name == "independent"
                    else sorted(
                        f"test_removed_point_edited_round_trip[{location}]"
                        for location in [
                            "None",
                            "nan_location1",
                            "nan_location2",
                            "nan_location3",
                        ]
                    )
                )
            assert failures == expected, failures
            assert result == (1 if expected else 0)
            suites[name] = {
                "tests": len(cases),
                "passed": len(cases) - len(failures),
                "failed": failures,
            }
        rendered = None
        if args.rendered:
            from verify_deletion import rendered_replay

            rendered = rendered_replay(
                args.output / "result.json",
                "baseline" if args.expect == "base" else "patched",
            )
    report = {
        "pr": profile["pr"],
        "expectation": args.expect,
        "source_revision": revision,
        "convert_sha256": digest(module),
        "runner_sha256": digest(Path(__file__)),
        "profile_sha256": digest(PROJECT / "upstream-1190-profile.json"),
        "local_patch_applied": False,
        "input_kind": "Constructed poses only; no recordings or biological simulation",
        "suites": suites,
        "rendered": rendered,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["numpy", "pandas", "xarray", "pytest", "napari", "PyQt6"]
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "limits": "Pinned draft PR and constructed conversion/rendered cases only. Not the full napari suite, re-add/reset UI, recordings, upstream acceptance or measured researcher benefit.",
    }
    assert digest(module) == profile[f"{args.expect}_convert_sha256"]
    (args.output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
