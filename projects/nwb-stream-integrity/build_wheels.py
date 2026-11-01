"""Build labelled release wheels and verify clean installs against real NWB workflows."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import venv
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def command(args, log, **kwargs):
    with log.open("w") as file:
        subprocess.run(
            list(map(str, args)),
            stdout=file,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=600,
            **kwargs,
        )


def build(mode, source, output, profile):
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source, text=True
        ).strip()
        == profile["upstream_commit"]
    )
    assert digest((source / "license.txt").read_bytes()) == profile["license_sha256"]
    assert (
        digest((source / "src/nwbinspector/utils/_utils.py").read_bytes())
        == profile[f"{mode}_shape_sha256"]
    )
    directory = output / f"build-{mode}"
    directory.mkdir()
    for name in ["README.md", "pyproject.toml", "license.txt"]:
        original = subprocess.check_output(
            ["git", "show", f"{profile['upstream_commit']}:{name}"], cwd=source
        )
        assert original == (source / name).read_bytes()
        (directory / name).write_bytes(original)
    files = subprocess.check_output(
        ["git", "ls-files", "src/nwbinspector"], cwd=source, text=True
    ).splitlines()
    expected = {}
    for name in files:
        file = source / name
        assert not file.is_symlink() and file.is_file()
        if name != "src/nwbinspector/utils/_utils.py":
            assert file.read_bytes() == subprocess.check_output(
                ["git", "show", f"{profile['upstream_commit']}:{name}"], cwd=source
            )
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        expected[name.removeprefix("src/")] = digest(file.read_bytes())
    version = f"0.7.2+kufu.{'baseline1' if mode == 'baseline' else 'stream1'}"
    config = directory / "pyproject.toml"
    text = config.read_text()
    assert text.count('version = "0.7.2"') == 1
    config.write_text(
        text.replace('version = "0.7.2"', f'version = "{version}"')
        + '\n[tool.hatch.build.targets.wheel.force-include]\n"license.txt" = "nwbinspector/UPSTREAM-LICENSE"\n'
    )
    provenance = {
        "upstream_commit": profile["upstream_commit"],
        "mode": mode,
        "patch_sha256": profile["patch_sha256"] if mode == "patched" else None,
        "experimental": True,
    }
    (directory / "src/nwbinspector/kufu_build.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    expected["nwbinspector/UPSTREAM-LICENSE"] = profile["license_sha256"]
    expected["nwbinspector/kufu_build.json"] = digest(
        (directory / "src/nwbinspector/kufu_build.json").read_bytes()
    )
    command(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-index",
            "--no-build-isolation",
            "--no-deps",
            "--wheel-dir",
            output / "wheels",
            directory,
        ],
        output / f"{mode}-build.log",
        env={**os.environ, "SOURCE_DATE_EPOCH": "1767225600", "PIP_NO_INDEX": "1"},
    )
    wheels = list((output / "wheels").glob(f"nwbinspector-{version}-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]
    assert wheel.stat().st_size < 1_000_000
    with zipfile.ZipFile(wheel) as archive:
        actual = {
            name: digest(archive.read(name))
            for name in archive.namelist()
            if name.startswith("nwbinspector/") and not name.endswith("/")
        }
        assert actual == expected
        assert json.loads(archive.read("nwbinspector/kufu_build.json")) == provenance
        licences = [
            name
            for name in archive.namelist()
            if name == "nwbinspector/UPSTREAM-LICENSE"
        ]
        assert (
            len(licences) == 1
            and digest(archive.read(licences[0])) == profile["license_sha256"]
        )
    shutil.rmtree(directory)
    return {
        "filename": wheel.name,
        "version": version,
        "sha256": digest(wheel.read_bytes()),
        "bytes": wheel.stat().st_size,
        "package_sha256": expected,
        "python_sha256": {
            name: sha for name, sha in expected.items() if name.endswith(".py")
        },
    }


def verify(mode, source, output, runtime, wheelhouse, profile, manifest):
    assert not runtime.exists(), (
        "Preserve existing environments; choose a new runtime root"
    )
    venv.EnvBuilder(with_pip=True, system_site_packages=False, symlinks=True).create(
        runtime
    )
    python = runtime / "bin/python"
    entry = manifest["builds"][mode]
    clean_env = {
        key: value
        for key, value in os.environ.items()
        if key not in ["PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"]
        and not key.startswith("PIP_")
    }
    clean_env.update(
        PYTHONNOUSERSITE="1", PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1"
    )
    command(
        [
            python,
            "-m",
            "pip",
            "--isolated",
            "install",
            "--no-index",
            "--find-links",
            wheelhouse,
            "-r",
            PROJECT / "requirements.txt",
            output / "wheels" / entry["filename"],
        ],
        output / f"{mode}-install.log",
        env=clean_env,
    )
    command(
        [python, "-m", "pip", "check"], output / f"{mode}-pip-check.log", env=clean_env
    )
    command(
        [
            python,
            PROJECT / "verify.py",
            "--released",
            "--expect",
            mode,
            "--wheel-record",
            output / "wheel-manifest.json",
            "--output",
            output / f"{mode}.json",
        ],
        output / f"{mode}-workflow.log",
        env=clean_env,
        cwd=output,
    )
    xml = output / f"{mode}-unit-tests.xml"
    tests = [source / "tests/unit_tests"]
    if mode == "patched":
        tests.append(source / "tests/test_stream_shape.py")
    environment = {
        **clean_env,
        "PYTHONPATH": str(PROJECT),
        "NWBI_SKIP_NETWORK_TESTS": "1",
        "KUFU_WHEEL_RECORD": str(output / "wheel-manifest.json"),
        "KUFU_WHEEL_MODE": mode,
    }
    with (output / f"{mode}-unit-tests.log").open("w") as file:
        run = subprocess.run(
            [
                str(python),
                "-m",
                "pytest",
                "-p",
                "verify_wheel",
                "--import-mode=importlib",
                *map(str, tests),
                "-q",
                f"--junitxml={xml}",
            ],
            cwd=output,
            env=environment,
            stdout=file,
            stderr=subprocess.STDOUT,
            timeout=180,
            check=False,
        )
    assert run.returncode == 1, "Expected only the recorded release failures"
    cases = list(ET.parse(xml).getroot().iter("testcase"))
    assert len(cases) == (286 if mode == "baseline" else 297)
    assert not any(case.find("error") is not None for case in cases)
    failures = sorted(
        case.attrib["name"] for case in cases if case.find("failure") is not None
    )
    assert failures == sorted(profile["known_unit_failures"])
    skipped = sum(case.find("skipped") is not None for case in cases)
    assert skipped == 5
    report = json.loads((output / f"{mode}.json").read_text())
    assert report["controls_preserved"] == 12
    assert report["inspected_preserved"] == (0 if mode == "baseline" else 12)
    return {
        "installed_build": report["installed_build"],
        "controls_preserved": report["controls_preserved"],
        "inspected_preserved": report["inspected_preserved"],
        "unit_tests": {
            "passed": len(cases) - len(failures) - skipped,
            "failed": failures,
            "skipped": skipped,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean-checkout", type=Path, default=ROOT / ".external/nwb-release-clean"
    )
    parser.add_argument(
        "--patched-checkout", type=Path, default=ROOT / ".external/nwb-release-patched"
    )
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert platform.python_version() == "3.12.12"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "wheels").mkdir()
    profile = json.loads((PROJECT / "released-profile.json").read_text())
    assert (
        digest((PROJECT / "released-0.7.2-shape.patch").read_bytes())
        == profile["patch_sha256"]
    )
    started = time.monotonic()
    manifest = {
        key: profile[key]
        for key in ["upstream_commit", "patch_sha256", "license_sha256"]
    }
    manifest["builder_versions"] = {
        name: importlib.metadata.version(name)
        for name in [
            line.split("==")[0]
            for line in (PROJECT / "requirements-build.txt").read_text().splitlines()
            if line
        ]
    }
    manifest["builds"] = {
        mode: build(mode, source.resolve(), output, profile)
        for mode, source in [
            ("baseline", args.clean_checkout),
            ("patched", args.patched_checkout),
        ]
    }
    (output / "wheel-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    results = {
        mode: verify(
            mode,
            source.resolve(),
            output,
            (args.runtime_root / mode).resolve(),
            args.wheelhouse.resolve(),
            profile,
            manifest,
        )
        for mode, source in [
            ("baseline", args.clean_checkout),
            ("patched", args.patched_checkout),
        ]
    }
    result = {
        "passed": True,
        "python": platform.python_version(),
        "manifest": manifest,
        "results": results,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "limits": "Constructed data and selected release regressions. Three known baseline unit failures and five skips remain on both builds. Experimental distribution; no upstream acceptance, real-recording or researcher-benefit validation.",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps({key: value for key, value in result.items() if key != "manifest"})
    )


if __name__ == "__main__":
    main()
