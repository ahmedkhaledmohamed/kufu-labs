"""Challenge the download verifier with real local/CI experiment artifacts."""

import copy
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

from verify_bundle import digest, verify


def fixture(recipe, root):
    reports = {
        mode: json.loads((root / f"parameterized-{mode}" / "report.json").read_text())
        for mode in ("baseline", "patched")
    }
    comparisons = json.loads(
        subprocess.check_output(
            [
                "node",
                "-e",
                (
                    "const {summarize}=require('./lab/contracts.cjs');"
                    "const r=JSON.parse(process.argv[1]);"
                    "console.log(JSON.stringify(summarize(r.baseline,r.patched,process.argv[2])))"
                ),
                json.dumps(reports),
                recipe,
            ],
            text=True,
        )
    )
    module_key = "annotations_sha256" if recipe == "mne" else "shape_module_sha256"
    result = {
        "recipe": recipe,
        "lab_source_commit": "local-verifier-fixture",
        "source_commit": "local-verifier-fixture",
        "upstream_commit": reports["patched"].get("upstream_commit", "fixture"),
        "patch_sha256": reports["patched"].get("patch_sha256", "fixture"),
        "experiment_sha256": "fixture",
        "requirements_sha256": "fixture",
        "cases": [case["input"] for case in reports["baseline"]["cases"]],
        "comparisons": comparisons,
        "environment": {
            "python": reports["patched"]["python"],
            **{mode: report["versions"] for mode, report in reports.items()},
            **{
                f"{mode}_module_sha256": report[module_key]
                for mode, report in reports.items()
            },
        },
    }
    files = {"manifest.json": json.dumps(result).encode()}
    for mode in reports:
        directory = root / f"parameterized-{mode}"
        for path in directory.rglob("*"):
            if path.is_file():
                files[f"{mode}/{path.relative_to(directory).as_posix()}"] = (
                    path.read_bytes()
                )
    return result, files


def check(result, files, expected_error=None):
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / "results.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for name, data in files.items():
                output.writestr(name, data)
        result = {**result, "bundle_sha256": digest(archive.read_bytes())}
        try:
            verified = verify(archive, result)
        except ValueError as error:
            if not expected_error or expected_error not in str(error):
                raise
        else:
            if expected_error:
                raise AssertionError(f"Corrupted evidence passed: {expected_error}")
            assert verified["array_evidence_verified"]


for recipe in ("nwb", "mne"):
    result, files = fixture(recipe, Path(f".runs/contracts/{recipe}"))
    check(result, files)
    damaged = dict(files)
    array_name = next(name for name in files if name.endswith("input.npy"))
    damaged[array_name] = files[array_name][:-1] + bytes([files[array_name][-1] ^ 1])
    check(result, damaged, "input hash mismatch")
    damaged = dict(files)
    # A well-formed but unsupported dtype must fail before hashing the payload.
    damaged[array_name] = files[array_name].replace(
        b"'<i2'" if recipe == "nwb" else b"'<f8'",
        b"'<u2'" if recipe == "nwb" else b"'<i8'",
        1,
    )
    check(result, damaged, "Unexpected array dtype")
    damaged = dict(files)
    manifest = json.loads(files["manifest.json"])
    manifest["lab_source_commit"] = "different-source"
    damaged["manifest.json"] = json.dumps(manifest).encode()
    check(result, damaged, "Bundle/API mismatch")
    if recipe == "nwb":
        # Make both reports and API agree on a false count: bytes must still win.
        wrong = copy.deepcopy(result)
        wrong["comparisons"][0]["baseline"]["changed_values"] += 1
        damaged = dict(files)
        report = json.loads(files["baseline/report.json"])
        report["cases"][0]["inspected"]["changed_values"] += 1
        damaged["baseline/report.json"] = json.dumps(report).encode()
        damaged["manifest.json"] = json.dumps(wrong).encode()
        check(wrong, damaged, "NWB comparison contradicts")
    else:
        wrong = copy.deepcopy(result)
        wrong["comparisons"][0]["controls"]["baseline"]["signal_unchanged"] = False
        damaged = dict(files)
        report = json.loads(files["baseline/report.json"])
        report["cases"][0]["controls"]["signal_unchanged"] = False
        damaged["baseline/report.json"] = json.dumps(report).encode()
        damaged["manifest.json"] = json.dumps(wrong).encode()
        check(wrong, damaged, "MNE unchanged-signal control contradicts")
    print(f"{recipe}: actual array evidence accepted; four corrupted bundles rejected")
