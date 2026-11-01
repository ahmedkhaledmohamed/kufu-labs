"""Verify installed wheel identity and guard pytest against source imports."""

import hashlib
import importlib.metadata
import json
import os
import socket
import sys
import zipfile
from pathlib import Path


def digest(value):
    return hashlib.sha256(value).hexdigest()


def no_network(*args, **kwargs):
    raise OSError("Network is disabled during installed-wheel science")


def validate_installed(record_path, mode):
    import nwbinspector

    project = Path(__file__).resolve().parent
    profile = json.loads((project / "released-profile.json").read_text())
    record = json.loads(Path(record_path).read_text())
    assert record["upstream_commit"] == profile["upstream_commit"]
    assert record["patch_sha256"] == profile["patch_sha256"]
    assert record["license_sha256"] == profile["license_sha256"]
    entry = record["builds"][mode]
    assert (
        entry["version"]
        == f"0.7.2+kufu.{'baseline1' if mode == 'baseline' else 'stream1'}"
    )
    assert Path(entry["filename"]).name == entry["filename"]
    wheel = Path(record_path).parent / "wheels" / entry["filename"]
    assert digest(wheel.read_bytes()) == entry["sha256"]
    package = Path(nwbinspector.__file__).resolve().parent
    assert package.is_relative_to(Path(sys.prefix).resolve())
    distribution = importlib.metadata.distribution("nwbinspector")
    assert distribution.version == nwbinspector.__version__ == entry["version"]
    direct = distribution.read_text("direct_url.json")
    assert direct and not json.loads(direct).get("dir_info", {}).get("editable")
    assert (
        Path(distribution.locate_file("nwbinspector/__init__.py")).resolve()
        == package / "__init__.py"
    )
    with zipfile.ZipFile(wheel) as archive:
        files = {
            name: digest(archive.read(name))
            for name in archive.namelist()
            if name.startswith("nwbinspector/") and name.endswith(".py")
        }
        assert files == entry["python_sha256"]
        packaged = {
            name: digest(archive.read(name))
            for name in archive.namelist()
            if name.startswith("nwbinspector/") and not name.endswith("/")
        }
        assert packaged == entry["package_sha256"]
        for name, sha in packaged.items():
            assert digest(distribution.locate_file(name).read_bytes()) == sha

        licences = [
            name
            for name in archive.namelist()
            if name == "nwbinspector/UPSTREAM-LICENSE"
        ]
        assert len(licences) == 1
        assert digest(archive.read(licences[0])) == profile["license_sha256"]
    assert (
        digest((package / "UPSTREAM-LICENSE").read_bytes()) == profile["license_sha256"]
    )
    provenance = json.loads((package / "kufu_build.json").read_text())
    assert provenance == {
        "upstream_commit": profile["upstream_commit"],
        "mode": mode,
        "patch_sha256": profile["patch_sha256"] if mode == "patched" else None,
        "experimental": True,
    }
    installed = {
        "nwbinspector/" + file.relative_to(package).as_posix(): digest(
            file.read_bytes()
        )
        for file in package.rglob("*.py")
    }
    assert installed == files
    for name, module in list(sys.modules.items()):
        if name == "nwbinspector" or name.startswith("nwbinspector."):
            file = getattr(module, "__file__", None)
            if file:
                assert Path(file).resolve().is_relative_to(package), name
            else:
                paths = list(getattr(module, "__path__", []))
                assert paths and all(
                    Path(path).resolve().is_relative_to(package) for path in paths
                ), name
    socket.socket.connect = no_network
    socket.create_connection = no_network
    return {
        "version": entry["version"],
        "wheel_sha256": entry["sha256"],
        "installed_python_files_verified": len(files),
        "installed_files_verified": len(packaged),
        "editable": False,
        "source_imports": False,
    }


def pytest_sessionstart(session):
    validate_installed(os.environ["KUFU_WHEEL_RECORD"], os.environ["KUFU_WHEEL_MODE"])


def pytest_sessionfinish(session, exitstatus):
    validate_installed(os.environ["KUFU_WHEEL_RECORD"], os.environ["KUFU_WHEEL_MODE"])
