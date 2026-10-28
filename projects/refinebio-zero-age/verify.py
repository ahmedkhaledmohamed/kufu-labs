"""Replay zero-age harmonisation using actual refine.bio source and synthetic metadata."""

import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    assert revision == "7b809b7cae8d8a16f635febda80ac0c7336de9d7"
    sys.path[:0] = [str(checkout / "common"), str(checkout / "foreman")]
    from django.conf import settings

    settings.configure(RUNNING_IN_CLOUD=False, SENTRY_DSN=None)
    started = time.monotonic()
    with patch(
        "socket.socket.connect",
        side_effect=RuntimeError("Network access disabled for replay"),
    ):
        from data_refinery_foreman.surveyor import harmony

        harmonizer = harmony.Harmonizer()
        cases = []
        for key in ["age", "Age", "age (years)", "characteristics_age"]:
            for value in [0, 0.0, "0", "0.0", "2", "", "unknown"]:
                sample = {"title": "constructed sample", "sex": "female", key: value}
                original = copy.deepcopy(sample)
                result = harmonizer.harmonize_sample(sample)
                assert sample == original, "Input metadata changed"
                assert result["title"] == sample["title"] and result["sex"] == "female"
                is_zero = value in [0, 0.0, "0", "0.0"]
                expected = (
                    0.0
                    if is_zero and args.expect == "patched"
                    else 2.0
                    if value == "2"
                    else None
                )
                assert result.get("age") == expected, (key, value, result.get("age"))
                if expected is None:
                    assert "age" not in result
                cases.append(
                    {
                        "field": key,
                        "input": value,
                        "age_present": "age" in result,
                        "age": result.get("age"),
                    }
                )
        unit_tests = None
        if args.expect == "patched":
            test_path = checkout / "foreman/tests/surveyor/test_harmony_zero_age.py"
            spec = importlib.util.spec_from_file_location(
                "zero_age_regressions", test_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = unittest.TextTestRunner().run(
                unittest.defaultTestLoader.loadTestsFromModule(module)
            )
            assert result.wasSuccessful(), "Regression tests failed"
            unit_tests = result.testsRun
    report = {
        "input_kind": "Constructed metadata only; no repository samples, subjects or recordings",
        "upstream_commit": revision,
        "harmony_source_sha256": hashlib.sha256(
            Path(harmony.__file__).read_bytes()
        ).hexdigest(),
        "expectation": args.expect,
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["Django", "daiquiri", "requests", "retrying"]
        },
        "cases": cases,
        "zero_age_cases_retained": sum(
            c["age_present"] and c["age"] == 0 for c in cases
        ),
        "unit_tests_passed": unit_tests,
        "network_connections": "Blocked by replay",
        "scope": "Actual upstream harmonizer in a minimal Django configuration; no database, ingestion service or production deployment",
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
