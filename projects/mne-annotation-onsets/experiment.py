"""Run bounded annotation-attachment cases and retain actual arrays/output."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path

import mne
import numpy as np
from mne import annotations


def digest(value):
    return hashlib.sha256(value).hexdigest()


def validate_cases(cases):
    if not isinstance(cases, list) or not 1 <= len(cases) <= 4:
        raise ValueError("Choose 1–4 cases")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"sfreq", "sample", "origin"}:
            raise ValueError("Unexpected MNE experiment fields")
        if type(case["sfreq"]) is not int or not 128 <= case["sfreq"] <= 8192:
            raise ValueError("Sampling rate must be an integer from 128 to 8192 Hz")
        if (
            type(case["sample"]) is not int
            or not 0 <= case["sample"] <= 2 * case["sfreq"]
        ):
            raise ValueError("Annotation sample must be between 0 and twice the rate")
        if case["origin"] not in ["relative", "utc"]:
            raise ValueError("Origin must be relative or utc")
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["baseline", "patched"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = validate_cases(json.loads(args.input.read_text()))
    project = Path(__file__).resolve().parent
    profile = json.loads((project / "profile.json").read_text())
    source = Path(annotations.__file__).resolve()
    checkout = source.parents[1]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    assert revision == profile["source_revision"]
    assert digest(source.read_bytes()) == profile[f"{args.mode}_annotations_sha256"]
    assert (
        digest((project / "preserve-interior-onsets.patch").read_bytes())
        == profile["patch_sha256"]
    )
    assert digest((checkout / "LICENSE.txt").read_bytes()) == profile["license_sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    for index, case in enumerate(cases):
        signal = np.linspace(-1e-6, 1e-6, 4 * case["sfreq"], dtype=np.float64).reshape(
            1, -1
        )
        input_hash = digest(signal.tobytes())
        raw = mne.io.RawArray(
            signal.copy(), mne.create_info(["eeg"], case["sfreq"], "eeg"), verbose=False
        )
        origin = (
            dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
            if case["origin"] == "utc"
            else None
        )
        if origin:
            raw.set_meas_date(origin)
        original = mne.Annotations(
            float(raw.times[case["sample"]]),
            0.1,
            "constructed stimulus",
            orig_time=origin,
        )
        reference = {
            "onset_seconds": float(original.onset[0]),
            "duration_seconds": float(original.duration[0]),
            "floor_index": int(raw.time_as_index(original.onset)[0]),
            "rounded_index": int(
                raw.time_as_index(original.onset, use_rounding=True)[0]
            ),
        }
        raw.set_annotations(original)
        actual = raw.get_data()
        attached = {
            "onset_seconds": float(raw.annotations.onset[0]),
            "duration_seconds": float(raw.annotations.duration[0]),
            "floor_index": int(raw.time_as_index(raw.annotations.onset)[0]),
            "rounded_index": int(
                raw.time_as_index(raw.annotations.onset, use_rounding=True)[0]
            ),
        }
        attached["onset_equal"] = (
            attached["onset_seconds"] == reference["onset_seconds"]
        )
        attached["duration_equal"] = (
            attached["duration_seconds"] == reference["duration_seconds"]
        )
        controls = {
            "signal_unchanged": bool(
                actual.dtype == signal.dtype and np.array_equal(signal, actual)
            ),
            "input_annotation_unchanged": float(original.onset[0])
            == reference["onset_seconds"]
            and float(original.duration[0]) == reference["duration_seconds"],
            "rounded_index_matches_sample": attached["rounded_index"]
            == reference["rounded_index"]
            == case["sample"],
        }
        input_file = f"{index}-input.npy"
        output_file = (
            input_file
            if controls["signal_unchanged"]
            else f"{index}-after-attachment.npy"
        )
        np.save(args.output / input_file, signal, allow_pickle=False)
        if output_file != input_file:
            np.save(args.output / output_file, actual, allow_pickle=False)
        results.append(
            {
                "input": case,
                "input_sha256": input_hash,
                "output_sha256": digest(actual.tobytes()),
                "reference": reference,
                "attached": attached,
                "controls": controls,
                "arrays": {"input": input_file, "after_attachment": output_file},
            }
        )
    report = {
        "mode": args.mode,
        "upstream_commit": revision,
        "annotations_sha256": digest(source.read_bytes()),
        "patch_sha256": profile["patch_sha256"] if args.mode == "patched" else None,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name) for name in ["mne", "numpy", "scipy"]
        },
        "input_kind": "Constructed one-channel linear ramp; not neural recordings or a neural simulation",
        "fixed_parameters": {
            "seconds": 4,
            "annotation_duration_seconds": 0.1,
            "first_samp": 0,
            "utc_origin": "2020-01-01T00:00:00+00:00",
        },
        "cases": results,
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
