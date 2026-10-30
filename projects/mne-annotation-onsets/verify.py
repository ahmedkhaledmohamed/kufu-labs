"""Replay onset precision and existing crop checks without recordings."""

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
    profile = json.loads((PROJECT / "profile.json").read_text())
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    assert revision == profile["source_revision"]
    assert digest(checkout / "LICENSE.txt") == profile["license_sha256"]
    source = checkout / "mne/annotations.py"
    assert digest(source) == profile[f"{args.expect}_annotations_sha256"]
    patch_path = PROJECT / "preserve-interior-onsets.patch"
    assert digest(patch_path) == profile["patch_sha256"]
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=checkout)
    if args.expect == "baseline":
        assert not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=checkout
        ).strip()
    else:
        assert diff == patch_path.read_bytes()
    tests = ROOT / ".external/mne-patched/mne/tests/test_annotations.py"
    assert digest(tests) == profile["tests_sha256"]
    sys.path.insert(0, str(checkout))
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    started = time.monotonic()
    signal_bytes_max = 0
    with tempfile.TemporaryDirectory(prefix="kufu-mne-") as temporary:
        os.environ["MNE_DATA"] = temporary
        import mne
        import numpy as np
        import pytest
        from mne import annotations

        assert Path(mne.__file__).resolve().is_relative_to(checkout)
        assert Path(annotations.__file__).resolve() == source
        xml = output.with_suffix(".xml")
        test_args = [
            "--noconftest",
            "--import-mode=importlib",
            "-o",
            "addopts=",
            "-q",
            f"--junitxml={xml}",
        ]
        test_args += [f"{tests}::{name}" for name in profile["selected_tests"]]
        with (
            output.with_suffix(".log").open("w") as log,
            contextlib.redirect_stdout(log),
            contextlib.redirect_stderr(log),
            patch.object(
                socket.socket,
                "connect",
                side_effect=AssertionError(
                    "Scientific replay must not access the network"
                ),
            ),
        ):
            result = pytest.main(test_args)
        assert result == (1 if args.expect == "baseline" else 0)
        cases = list(ET.parse(xml).getroot().iter("testcase"))
        assert len(cases) == 12
        assert not any(
            c.find("error") is not None or c.find("skipped") is not None for c in cases
        )
        failures = sorted(
            c.attrib["name"] for c in cases if c.find("failure") is not None
        )
        assert failures == (
            sorted(profile["baseline_failures"]) if args.expect == "baseline" else []
        )
        observations = []
        for sfreq in [300, 512, 1000, 2048]:
            signal = np.zeros((1, sfreq * 4))
            signal_bytes_max = max(signal_bytes_max, signal.nbytes)
            raw = mne.io.RawArray(
                signal,
                mne.create_info(["eeg"], sfreq, "eeg"),
                verbose=False,
            )
            original = float(raw.times[1])
            raw.set_annotations(mne.Annotations(original, 0.1, "constructed stimulus"))
            observations.append(
                {
                    "sfreq_hz": sfreq,
                    "original_onset_seconds": original,
                    "attached_onset_seconds": float(raw.annotations.onset[0]),
                    "sample_index_before": int(raw.time_as_index(original)[0]),
                    "sample_index_after": int(
                        raw.time_as_index(raw.annotations.onset)[0]
                    ),
                    "sample_index_with_rounding": int(
                        raw.time_as_index(raw.annotations.onset, use_rounding=True)[0]
                    ),
                }
            )
    report = {
        "source_revision": revision,
        "annotations_sha256": digest(source),
        "expectation": args.expect,
        "patch_sha256": profile["patch_sha256"] if args.expect == "patched" else None,
        "tests": len(cases),
        "passed": len(cases) - len(failures),
        "failed": failures,
        "input_kind": "Constructed zero array; 1 EEG channel, 4 seconds; not a neural recording or simulation",
        "observations": observations,
        "python": platform.python_version(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "largest_constructed_signal_bytes": signal_bytes_max,
        "runtime_versions": {
            name: importlib.metadata.version(name)
            for name in ["mne", "numpy", "scipy", "pytest"]
        },
        "version_note": "mne distribution version identifies the installed runtime wheel; imported source is the separately pinned Git revision",
        "limits": "Unclipped interior onsets only; no hardware-clock, recording, general datetime precision or serialization claim",
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
