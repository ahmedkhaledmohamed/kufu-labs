"""Compare the released suite while retaining its known dependency failures."""

import argparse
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    profile = json.loads((PROJECT / "released-profile.json").read_text())
    results = {}
    for mode, checkout, expected_tests in [
        ("baseline", "nwb-release-clean", 286),
        ("patched", "nwb-release-patched", 297),
    ]:
        source = ROOT / ".external" / checkout
        xml = output / f"{mode}-unit-tests.xml"
        command = [sys.executable, "-m", "pytest", "tests/unit_tests"]
        if mode == "patched":
            command.append("tests/test_stream_shape.py")
        command += ["-q", f"--junitxml={xml}"]
        with (output / f"{mode}-unit-tests.log").open("w") as log:
            run = subprocess.run(
                command,
                cwd=source,
                env={
                    **os.environ,
                    "PYTHONPATH": str(source / "src"),
                    "NWBI_SKIP_NETWORK_TESTS": "1",
                },
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        assert run.returncode == 1, "Expected only the recorded test failures"
        cases = list(ET.parse(xml).getroot().iter("testcase"))
        assert len(cases) == expected_tests, "Released suite collection changed"
        assert not any(c.find("error") is not None for c in cases)
        failures = sorted(
            c.attrib["name"] for c in cases if c.find("failure") is not None
        )
        assert failures == sorted(profile["known_unit_failures"]), (
            "Failures differ from the recorded unchanged-release failures"
        )
        skipped = sum(c.find("skipped") is not None for c in cases)
        assert skipped == 5, "Released suite skips changed"
        results[mode] = {
            "passed": len(cases) - len(failures) - skipped,
            "skipped": skipped,
            "failed": failures,
        }
    (output / "unit-comparison.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
