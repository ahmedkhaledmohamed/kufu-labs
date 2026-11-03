"""Compare installed wheels on bounded, generated electrophysiology conversions."""

import argparse
import hashlib
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime-root", type=Path, default=ROOT / ".external/nwb-wheel-runtimes"
    )
    parser.add_argument(
        "--wheel-record",
        type=Path,
        default=ROOT / ".runs/contracts/nwb-release/installable/wheel-manifest.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cases = []
    for rows in [16384, 524288, 4194304]:
        for mode in ["baseline", "patched"]:
            for inspected in [False, True]:
                directory = (
                    args.output
                    / f"{mode}-{rows}-{'inspected' if inspected else 'control'}"
                )
                command = [
                    str(args.runtime_root.resolve() / mode / "bin/python"),
                    str(PROJECT / "ecephys.py"),
                    "--expect",
                    mode,
                    "--rows",
                    str(rows),
                    "--channels",
                    "16",
                    "--buffer",
                    "4096",
                    "--wheel-record",
                    str(args.wheel_record.resolve()),
                    "--output",
                    str(directory.resolve()),
                ]
                if not inspected:
                    command.append("--skip-inspection")
                if rows == 16384:
                    command.append("--retain")
                with (args.output / f"{directory.name}.log").open("w") as log:
                    subprocess.run(
                        command,
                        env={
                            key: value
                            for key, value in os.environ.items()
                            if key not in ["PYTHONPATH", "PYTHONHOME"]
                        },
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        check=True,
                        timeout=120,
                    )
                result = json.loads((directory / "result.json").read_text())
                assert result["input"] == {
                    "rows": rows,
                    "channels": 16,
                    "buffer_rows": 4096,
                }
                assert (
                    result["expectation"] == mode and result["inspected"] is inspected
                )
                assert (
                    result["metadata"]["preserved"]
                    and result["schema_validation_errors"] == 0
                )
                assert result["installed_build"]["source_imports"] is False
                assert result["installed_build"]["editable"] is False
                if mode == "patched" or not inspected:
                    assert result["values_preserved"] and result["changed_rows"] == 0
                else:
                    assert result["changed_rows"] == 12288
                    assert result["iterator_buffers_requested"]["inspection"] == 3
                if rows == 16384:
                    file = directory / "constructed_ecephys.nwb"
                    assert file.stat().st_size == result["file_bytes"]
                    result["retained_file"] = (
                        f"{directory.name}/constructed_ecephys.nwb"
                    )
                    result["retained_file_sha256"] = hashlib.sha256(
                        file.read_bytes()
                    ).hexdigest()
                else:
                    assert not (directory / "constructed_ecephys.nwb").exists()
                cases.append(result)
    for offset in range(0, len(cases), 4):
        batch = cases[offset : offset + 4]
        assert len({case["expected_sha256"] for case in batch}) == 1
        assert all(case["metadata"] == batch[0]["metadata"] for case in batch)
        assert all(case["legitimate_zero_values"] > 0 for case in batch)
    summary = {
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "passed": True,
        "cases": cases,
        "sizes_bytes": [16384 * 32, 524288 * 32, 4194304 * 32],
        "verification": "Every saved value compared in bounded blocks; electrode links, voltage scale, timing and schema checked separately.",
        "retained_small_files": 4,
        "peak_rss_bytes": max(case["peak_rss_bytes"] for case in cases),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "limits": "Generated 16-channel patterns, HDF5, fixed 20 kHz sampling and 4096-row buffers, pinned installed wheels and dependencies. Larger files are removed after validation; small files are retained. No recordings, neural model, recording-scale guarantee or researcher-benefit validation.",
    }
    archive = args.output / "ecephys-example.zip"
    names = {}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for case in cases:
            if case["file_retained"]:
                name = f"{case['expectation']}-{'inspected' if case['inspected'] else 'control'}.nwb"
                bundle.write(args.output / case["retained_file"], name)
                names[name] = case["retained_file_sha256"]
        bundle.writestr(
            "README.txt",
            "Constructed electrode patterns, not neural recordings or a biological simulation.\nBaseline inspected data differs from the generated input. See results.json for value, metadata, schema and resource checks.\n",
        )
        bundle.writestr(
            "results.json",
            json.dumps([case for case in cases if case["file_retained"]], indent=2)
            + "\n",
        )
    assert archive.stat().st_size < 4_000_000
    with zipfile.ZipFile(archive) as bundle:
        for name, sha in names.items():
            assert hashlib.sha256(bundle.read(name)).hexdigest() == sha
    summary["small_archive"] = {
        "filename": archive.name,
        "bytes": archive.stat().st_size,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "nwb_files": names,
    }
    (args.output / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}))


if __name__ == "__main__":
    main()
