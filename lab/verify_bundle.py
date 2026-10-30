"""Check downloaded execution evidence without scientific packages or extraction."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def array(archive, name, dtype, shape):
    """Read only the two bounded, C-order numeric NPY formats these recipes write."""
    data = archive.read(name)
    require(data[:8] == b"\x93NUMPY\x01\x00", f"Unsupported NPY format: {name}")
    end = 10 + struct.unpack("<H", data[8:10])[0]
    header = ast.literal_eval(data[10:end].decode("latin1"))
    require(
        header == {"descr": dtype, "fortran_order": False, "shape": shape},
        f"Unexpected array dtype, shape or order: {name}",
    )
    payload = data[end:]
    require(
        len(payload) == math.prod(shape) * int(dtype[2:]),
        f"Incorrect array byte count: {name}",
    )
    return payload


def verify(archive_path, result):
    require(
        digest(archive_path.read_bytes()) == result["bundle_sha256"],
        "Bundle hash differs from the completed run",
    )
    require(
        result["source_commit"] == result["lab_source_commit"],
        "API/worker source identity differs",
    )
    recipe = result["recipe"]
    require(recipe in ("nwb", "mne"), "Unsupported recipe")
    require(
        1 <= len(result["cases"]) <= 4
        and len(result["comparisons"]) == len(result["cases"]),
        "Invalid comparison case count",
    )
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP entries")
        require(
            sum(item.file_size for item in archive.infolist()) <= 30_000_000,
            "Expanded evidence exceeds the verification limit",
        )
        manifest = json.loads(archive.read("manifest.json"))
        for key in (
            "recipe",
            "lab_source_commit",
            "upstream_commit",
            "patch_sha256",
            "experiment_sha256",
            "requirements_sha256",
            "cases",
            "comparisons",
            "environment",
        ):
            require(manifest[key] == result[key], f"Bundle/API mismatch: {key}")
        inputs = []
        for mode in ("baseline", "patched"):
            report = json.loads(archive.read(f"{mode}/report.json"))
            require(report["mode"] == mode, "Incorrect report mode")
            require(
                [case["input"] for case in report["cases"]] == result["cases"],
                "Report inputs differ from the submitted plan",
            )
            module_key = (
                "annotations_sha256" if recipe == "mne" else "shape_module_sha256"
            )
            require(
                report[module_key] == result["environment"][f"{mode}_module_sha256"],
                "Report module identity differs",
            )
            require(
                report["versions"] == result["environment"][mode], "Version mismatch"
            )
            require(
                report["python"] == result["environment"]["python"],
                "Python version mismatch",
            )
            if recipe == "mne":
                require(
                    report["upstream_commit"] == result["upstream_commit"],
                    "MNE revision mismatch",
                )
                require(
                    report["patch_sha256"]
                    == (result["patch_sha256"] if mode == "patched" else None),
                    "MNE patch identity mismatch",
                )
            mode_inputs = []
            for index, case in enumerate(report["cases"]):
                comparison = result["comparisons"][index]
                config = case["input"]
                if recipe == "mne":
                    shape = (1, 4 * config["sfreq"])
                    before = array(
                        archive, f"{mode}/{case['arrays']['input']}", "<f8", shape
                    )
                    after = array(
                        archive,
                        f"{mode}/{case['arrays']['after_attachment']}",
                        "<f8",
                        shape,
                    )
                    require(
                        digest(before) == case["input_sha256"],
                        "MNE input hash mismatch",
                    )
                    require(
                        digest(after) == case["output_sha256"],
                        "MNE output hash mismatch",
                    )
                    require(
                        case["controls"]["signal_unchanged"] == (before == after),
                        "MNE unchanged-signal control contradicts exported arrays",
                    )
                    require(
                        case["reference"] == comparison["reference"],
                        "MNE reference mismatch",
                    )
                    require(
                        case["attached"] == comparison[mode],
                        "MNE attached-output mismatch",
                    )
                    require(
                        case["controls"] == comparison["controls"][mode],
                        "MNE controls mismatch",
                    )
                    mode_inputs.append(before)
                else:
                    shape = (config["rows"], config["channels"])
                    case_inputs = []
                    for role in ("control", "inspected"):
                        prefix = f"{mode}/{index}/{role}"
                        before = array(archive, f"{prefix}/input.npy", "<i2", shape)
                        after = array(archive, f"{prefix}/output.npy", "<i2", shape)
                        run = case[role]
                        require(
                            digest(before) == run["input_sha256"],
                            "NWB input hash mismatch",
                        )
                        require(
                            digest(after) == run["output_sha256"],
                            "NWB output hash mismatch",
                        )
                        changes = [
                            a != b
                            for a, b in zip(
                                struct.iter_unpack("<h", before),
                                struct.iter_unpack("<h", after),
                            )
                        ]
                        changed_rows = sum(
                            any(changes[start : start + shape[1]])
                            for start in range(0, len(changes), shape[1])
                        )
                        require(
                            run["changed_values"] == sum(changes)
                            and run["changed_rows"] == changed_rows
                            and run["values_equal"] == (before == after)
                            and run["shape_equal"]
                            and run["dtype_equal"]
                            and run["expected_shape"]
                            == run["actual_shape"]
                            == list(shape)
                            and run["dtype"] == "int16",
                            "NWB comparison contradicts exported arrays",
                        )
                        expected = (
                            comparison["controls"][mode]
                            if role == "control"
                            else comparison[mode]
                        )
                        require(run == expected, "NWB report/API comparison mismatch")
                        case_inputs.append(before)
                    require(
                        case_inputs[0] == case_inputs[1],
                        "NWB control/inspected inputs differ",
                    )
                    mode_inputs.append(case_inputs[0])
            inputs.append(mode_inputs)
        require(inputs[0] == inputs[1], "Baseline/patched input arrays differ")
    return {
        "recipe": recipe,
        "cases": len(result["cases"]),
        "array_evidence_verified": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, json.loads(args.result.read_text()))))


if __name__ == "__main__":
    main()
