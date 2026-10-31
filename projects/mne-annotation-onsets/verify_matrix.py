"""Challenge the pinned MNE candidate with a deterministic supported-input matrix."""

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def inputs():
    """Fixed boundary/reference cases plus reproducible interior samples."""
    cases = []
    rates = [
        128,
        129,
        250,
        256,
        300,
        500,
        512,
        1000,
        1024,
        2000,
        2048,
        4096,
        8000,
        8191,
        8192,
    ]
    for rate in rates:
        for sample in [0, 1, rate, 2 * rate]:
            for origin in ["relative", "utc"]:
                cases.append({"sfreq": rate, "sample": sample, "origin": origin})
    generator = random.Random(20261030)
    for _ in range(40):
        rate = generator.randint(128, 8192)
        cases.append(
            {
                "sfreq": rate,
                "sample": generator.randint(0, 2 * rate),
                "origin": generator.choice(["relative", "utc"]),
            }
        )
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean-checkout", type=Path, default=Path(".external/mne-clean")
    )
    parser.add_argument(
        "--patched-checkout", type=Path, default=Path(".external/mne-patched")
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cases = inputs()
    (args.output / "inputs.json").write_text(json.dumps(cases, indent=2) + "\n")
    counts = dict.fromkeys(
        [
            "baseline_onset_changes",
            "patched_onset_changes",
            "patched_duration_changes",
            "control_failures",
            "verified_array_roles",
            "reference_floor_mismatches",
            "baseline_attachment_floor_changes",
            "patched_attachment_floor_changes",
            "baseline_floor_mismatches",
            "patched_floor_mismatches",
            "rounded_index_failures",
        ],
        0,
    )
    examples = []
    metadata = None
    started = time.monotonic()
    for offset in range(0, len(cases), 4):
        directory = args.output / str(offset // 4)
        directory.mkdir()
        plan = directory / "inputs.json"
        plan.write_text(json.dumps(cases[offset : offset + 4]))
        reports = {}
        for mode, checkout in [
            ("baseline", args.clean_checkout),
            ("patched", args.patched_checkout),
        ]:
            environment = {
                **os.environ,
                "PYTHONPATH": str(checkout.resolve()),
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
            }
            with (directory / f"{mode}.log").open("w") as log:
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).with_name("experiment.py")),
                        "--mode",
                        mode,
                        "--input",
                        str(plan),
                        "--output",
                        str(directory / mode),
                    ],
                    env=environment,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
            report = json.loads((directory / mode / "report.json").read_text())
            assert [case["input"] for case in report["cases"]] == cases[
                offset : offset + 4
            ]
            reports[mode] = report
            for case in report["cases"]:
                for role, hash_key in [
                    ("input", "input_sha256"),
                    ("after_attachment", "output_sha256"),
                ]:
                    array = np.load(
                        directory / mode / case["arrays"][role], allow_pickle=False
                    )
                    assert array.shape == (1, 4 * case["input"]["sfreq"])
                    assert array.dtype == np.dtype("float64")
                    assert hashlib.sha256(array.tobytes()).hexdigest() == case[hash_key]
                    counts["verified_array_roles"] += 1
                counts["control_failures"] += sum(
                    value is not True for value in case["controls"].values()
                )
                counts[f"{mode}_onset_changes"] += (
                    case["attached"]["onset_seconds"]
                    != case["reference"]["onset_seconds"]
                )
                if mode == "patched":
                    counts["patched_duration_changes"] += (
                        case["attached"]["duration_seconds"]
                        != case["reference"]["duration_seconds"]
                    )
        if metadata is None:
            metadata = {
                mode: {
                    key: report[key]
                    for key in [
                        "upstream_commit",
                        "annotations_sha256",
                        "patch_sha256",
                        "python",
                        "versions",
                    ]
                }
                for mode, report in reports.items()
            }
        for before, after in zip(
            reports["baseline"]["cases"], reports["patched"]["cases"]
        ):
            assert before["input"] == after["input"]
            assert before["input_sha256"] == after["input_sha256"]
            assert before["reference"] == after["reference"]
            target = before["input"]["sample"]
            reference = before["reference"]["floor_index"]
            baseline = before["attached"]["floor_index"]
            patched = after["attached"]["floor_index"]
            counts["reference_floor_mismatches"] += reference != target
            counts["baseline_attachment_floor_changes"] += baseline != reference
            counts["patched_attachment_floor_changes"] += patched != reference
            counts["baseline_floor_mismatches"] += baseline != target
            counts["patched_floor_mismatches"] += patched != target
            counts["rounded_index_failures"] += any(
                run["attached"]["rounded_index"] != target for run in [before, after]
            )
            if reference != target and len(examples) < 4:
                examples.append(
                    {
                        "input": before["input"],
                        "reference": before["reference"],
                        "baseline": before["attached"],
                        "patched": after["attached"],
                    }
                )
    passed = counts["baseline_onset_changes"] > 0 and all(
        counts[key] == 0
        for key in [
            "patched_onset_changes",
            "patched_duration_changes",
            "control_failures",
            "patched_attachment_floor_changes",
            "rounded_index_failures",
        ]
    )
    result = {
        "passed": passed,
        "cases": len(cases),
        "seed": 20261030,
        **counts,
        "source_and_environment": metadata,
        "reference_floor_examples": examples,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "limits": "Constructed ramps and supported inputs only. Onset preservation does not guarantee truncating lookup returns the requested sample. Rounded lookup is an existing workaround; no physical-clock, real-recording or researcher-benefit validation.",
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    assert passed, "Generated matrix failed; inspect retained reports and arrays"


if __name__ == "__main__":
    main()
