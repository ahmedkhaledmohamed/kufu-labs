"""Compare actual annotation attachment, FIF IO, events and epochs on pinned MNE."""

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def digest(value):
    return hashlib.sha256(value).hexdigest()


def reject_network(*args, **kwargs):
    raise RuntimeError("Network access is disabled during the scientific workflow")


def run_mode(mode, output):
    import mne
    from mne import annotations

    project = Path(__file__).resolve().parent
    profile = json.loads((project / "profile.json").read_text())
    source = Path(annotations.__file__).resolve()
    checkout = source.parents[1]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    assert revision == profile["source_revision"]
    assert digest(source.read_bytes()) == profile[f"{mode}_annotations_sha256"]
    assert (
        digest((project / "preserve-interior-onsets.patch").read_bytes())
        == profile["patch_sha256"]
    )
    assert digest((checkout / "LICENSE.txt").read_bytes()) == profile["license_sha256"]
    # Lock the additional host implementations, not just the patched method.
    host_hashes = {}
    for name in ["mne/io/base.py", "mne/io/fiff/raw.py", "mne/epochs.py"]:
        original = subprocess.check_output(
            ["git", "show", f"{revision}:{name}"], cwd=checkout
        )
        actual = (checkout / name).read_bytes()
        assert actual == original, f"Unexpected host change: {name}"
        host_hashes[name] = digest(actual)
    socket.socket.connect = reject_network
    socket.create_connection = reject_network
    results = []
    for rate in [300, 512, 1000, 2048]:
        for sample in [1, rate + 1]:
            for offset in [0, 2 * rate + 7]:
                for origin_kind in ["relative", "utc"]:
                    directory = output / str(len(results))
                    directory.mkdir()
                    signal = np.linspace(-1e-6, 1e-6, 4 * rate, dtype=np.float64)[
                        None, :
                    ]
                    raw = mne.io.RawArray(
                        signal.copy(),
                        mne.create_info(["eeg"], rate, "eeg"),
                        first_samp=offset,
                        verbose=False,
                    )
                    origin = (
                        dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
                        if origin_kind == "utc"
                        else None
                    )
                    if origin is not None:
                        raw.set_meas_date(origin)
                    relative_onset = float(raw.times[sample])
                    onset = relative_onset + (offset / rate if origin else 0)
                    annotation = mne.Annotations(
                        onset, 0.1, "constructed stimulus", orig_time=origin
                    )
                    reference_onset = relative_onset + offset / rate
                    reference = annotation.copy()
                    reference_truncated = int(
                        raw.time_as_index(
                            [reference_onset], use_rounding=False, origin=origin
                        )[0]
                    )
                    if origin is not None:
                        reference_truncated += offset
                    raw.set_annotations(annotation)
                    attached = raw.annotations.copy()
                    assert float(attached.duration[0]) == 0.1
                    filename = directory / "constructed_raw.fif"
                    raw.save(filename, fmt="double", overwrite=False, verbose=False)
                    stored = mne.read_annotations(filename)
                    reloaded = mne.io.read_raw_fif(
                        filename, preload=True, verbose=False
                    )
                    assert len(stored) == len(reloaded.annotations) == 1
                    assert np.array_equal(annotation.onset, reference.onset)
                    assert np.array_equal(annotation.duration, reference.duration)
                    assert np.array_equal(raw.get_data(), signal)
                    assert np.array_equal(reloaded.get_data(), signal)
                    assert raw.first_samp == reloaded.first_samp == offset
                    assert raw.info["meas_date"] == reloaded.info["meas_date"] == origin
                    assert list(stored.description) == list(attached.description)
                    # FIF writes float32 onset and end independently, even with fmt=double.
                    assert float(stored.onset[0]) == float(
                        np.float32(attached.onset[0])
                    )
                    expected_duration = float(
                        np.float32(attached.onset[0] + attached.duration[0])
                        - np.float32(attached.onset[0])
                    )
                    assert float(stored.duration[0]) == expected_duration
                    stages = {}
                    for name, value in [
                        ("attached", attached),
                        ("fif_stored", stored),
                        ("reopened", reloaded.annotations),
                    ]:
                        stages[name] = {
                            "onset_seconds": float(value.onset[0]),
                            "duration_seconds": float(value.duration[0]),
                        }
                    for name, value in [("attached", raw), ("reopened", reloaded)]:
                        default, event_id = mne.events_from_annotations(
                            value, verbose=False
                        )
                        rounded, _ = mne.events_from_annotations(
                            value, use_rounding=True, verbose=False
                        )
                        truncated, _ = mne.events_from_annotations(
                            value, use_rounding=False, verbose=False
                        )
                        assert np.array_equal(default, rounded)
                        assert int(default[0, 0]) == offset + sample
                        epoch = mne.Epochs(
                            value,
                            default,
                            event_id,
                            tmin=0,
                            tmax=3 / rate,
                            baseline=None,
                            preload=True,
                            proj=False,
                            reject_by_annotation=False,
                            verbose=False,
                        )
                        epoch_data = epoch.get_data(copy=True)
                        expected = signal[:, sample : sample + 4][None, :, :]
                        assert np.array_equal(epoch_data, expected)
                        assert len(epoch) == 1
                        stages[name].update(
                            default_event_sample=int(default[0, 0]),
                            truncating_event_sample=int(truncated[0, 0]),
                            epoch_matches_expected=True,
                            epoch_sha256=digest(epoch_data.tobytes()),
                        )
                        np.save(
                            directory / f"{name}-epoch.npy",
                            epoch_data,
                            allow_pickle=False,
                        )
                    np.save(directory / "signal.npy", signal, allow_pickle=False)
                    np.save(
                        directory / "reopened-signal.npy",
                        reloaded.get_data(),
                        allow_pickle=False,
                    )
                    results.append(
                        {
                            "input": {
                                "sfreq": rate,
                                "sample": sample,
                                "first_samp": offset,
                                "origin": origin_kind,
                            },
                            "reference_onset_seconds": reference_onset,
                            "expected_event_sample": offset + sample,
                            "reference_truncating_event_sample": reference_truncated,
                            "signal_sha256": digest(signal.tobytes()),
                            "stages": stages,
                            "artifacts": {
                                p.name: digest(p.read_bytes())
                                for p in directory.iterdir()
                            },
                        }
                    )
                    raw.close()
                    reloaded.close()
    report = {
        "mode": mode,
        "upstream_commit": revision,
        "annotations_sha256": digest(source.read_bytes()),
        "patch_sha256": profile["patch_sha256"],
        "host_sha256": host_hashes,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name) for name in ["mne", "numpy", "scipy"]
        },
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        * (1 if sys.platform == "darwin" else 1024),
        "cases": results,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")


def compare(args):
    started = time.monotonic()
    reports = {}
    for mode, checkout in [
        ("baseline", args.clean_checkout),
        ("patched", args.patched_checkout),
    ]:
        directory = args.output / mode
        with (args.output / f"{mode}.log").open("w") as log:
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--mode",
                    mode,
                    "--output",
                    str(directory),
                ],
                env={
                    **os.environ,
                    "PYTHONPATH": str(checkout.resolve()),
                    "OPENBLAS_NUM_THREADS": "1",
                    "OMP_NUM_THREADS": "1",
                },
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=90,
            )
        reports[mode] = json.loads((directory / "report.json").read_text())
    counts = {}
    verified_arrays = 0
    for mode, report in reports.items():
        counts[mode] = {
            "attachment_onset_changes": 0,
            "serialization_onset_changes": 0,
            "reopen_onset_changes": 0,
            "default_event_mismatches": 0,
            "truncating_event_mismatches": 0,
            "epoch_mismatches": 0,
            "reference_truncating_mismatches": 0,
            "attachment_truncating_changes": 0,
            "reopen_truncating_changes": 0,
        }
        for index, case in enumerate(report["cases"]):
            folder = args.output / mode / str(index)
            for name, checksum in case["artifacts"].items():
                assert digest((folder / name).read_bytes()) == checksum
            original = np.load(folder / "signal.npy", allow_pickle=False)
            loaded = np.load(folder / "reopened-signal.npy", allow_pickle=False)
            assert np.array_equal(original, loaded)
            assert digest(original.tobytes()) == case["signal_sha256"]
            verified_arrays += 2
            for stage in ["attached", "reopened"]:
                epoch = np.load(folder / f"{stage}-epoch.npy", allow_pickle=False)
                sample = case["input"]["sample"]
                assert np.array_equal(epoch, original[None, :, sample : sample + 4])
                assert digest(epoch.tobytes()) == case["stages"][stage]["epoch_sha256"]
                verified_arrays += 1
                counts[mode]["default_event_mismatches"] += (
                    case["stages"][stage]["default_event_sample"]
                    != case["expected_event_sample"]
                )
                counts[mode]["truncating_event_mismatches"] += (
                    case["stages"][stage]["truncating_event_sample"]
                    != case["expected_event_sample"]
                )
                counts[mode]["epoch_mismatches"] += not case["stages"][stage][
                    "epoch_matches_expected"
                ]
            stages = case["stages"]
            counts[mode]["reference_truncating_mismatches"] += (
                case["reference_truncating_event_sample"]
                != case["expected_event_sample"]
            )
            counts[mode]["attachment_truncating_changes"] += (
                stages["attached"]["truncating_event_sample"]
                != case["reference_truncating_event_sample"]
            )
            counts[mode]["reopen_truncating_changes"] += (
                stages["reopened"]["truncating_event_sample"]
                != stages["attached"]["truncating_event_sample"]
            )
            counts[mode]["attachment_onset_changes"] += (
                stages["attached"]["onset_seconds"] != case["reference_onset_seconds"]
            )
            counts[mode]["serialization_onset_changes"] += (
                stages["fif_stored"]["onset_seconds"]
                != stages["attached"]["onset_seconds"]
            )
            counts[mode]["reopen_onset_changes"] += (
                stages["reopened"]["onset_seconds"]
                != stages["fif_stored"]["onset_seconds"]
            )
    assert len(reports["baseline"]["cases"]) == len(reports["patched"]["cases"]) == 32
    for before, after in zip(reports["baseline"]["cases"], reports["patched"]["cases"]):
        assert before["input"] == after["input"]
        assert before["signal_sha256"] == after["signal_sha256"]
        assert before["reference_onset_seconds"] == after["reference_onset_seconds"]
        assert before["expected_event_sample"] == after["expected_event_sample"]
    assert counts["baseline"]["attachment_onset_changes"] > 0
    assert counts["patched"]["attachment_onset_changes"] == 0
    examples = [
        {mode: report["cases"][index] for mode, report in reports.items()}
        for index in [2, 11]
    ]
    artifact_bytes = sum(
        p.stat().st_size for p in args.output.rglob("*") if p.is_file()
    )
    assert artifact_bytes < 10_000_000
    assert all(report["peak_rss_bytes"] < 1_073_741_824 for report in reports.values())
    result = {
        "passed": True,
        "cases_per_revision": 32,
        "verified_arrays": verified_arrays,
        "counts": counts,
        "examples": examples,
        "source_and_environment": {
            mode: {k: v for k, v in report.items() if k != "cases"}
            for mode, report in reports.items()
        },
        "artifact_bytes": artifact_bytes,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "limits": "Constructed four-second ramps, four rates, two interior samples, zero/nonzero offsets and relative/UTC origins. Default events and four-sample epochs are checked. Exact FIF timestamps are not preserved; truncating lookup remains vulnerable. No clipping, long-recording, physical-clock or researcher-benefit validation.",
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["baseline", "patched"])
    parser.add_argument(
        "--clean-checkout", type=Path, default=Path(".external/mne-clean")
    )
    parser.add_argument(
        "--patched-checkout", type=Path, default=Path(".external/mne-patched")
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    if args.mode:
        run_mode(args.mode, args.output)
    else:
        compare(args)


if __name__ == "__main__":
    main()
