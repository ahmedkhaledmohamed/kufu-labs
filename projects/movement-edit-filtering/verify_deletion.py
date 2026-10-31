"""Verify saved deletion provenance against exact movement source and patch."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rendered_replay(output, expectation):
    """Delete through Qt, then save/reopen twice using unchanged host widgets."""
    import resource

    import numpy as np
    import xarray as xr
    from movement.io import load_poses, save_dataset
    from movement.napari.loader_widgets import POINTS_PROPERTIES_KEY, DataLoader
    from movement.napari.save_widget import DataSaver
    from napari import Viewer
    from OpenGL.GL import GL_RENDERER, glGetString
    from qtpy import QtCore, QtTest
    from qtpy.QtWidgets import QApplication, QFileDialog

    started = time.monotonic()
    directory = output.parent / f"rendered-{expectation}"
    directory.mkdir(exist_ok=False)
    captures = directory / "canvas"
    captures.mkdir()
    app = QApplication.instance() or QApplication([])
    assert app.platformName() == "xcb", "Use CPU Mesa rendering under Xvfb"
    positions = np.empty((4, 2, 2, 2), dtype=float)
    for frame in range(4):
        for keypoint in range(2):
            for individual in range(2):
                positions[frame, :, keypoint, individual] = [
                    40 + frame * 3 + individual * 100 - keypoint * 10,
                    45 + frame * 2 + individual * 20 + keypoint * 30,
                ]
    confidence = np.full((4, 2, 2), 0.9)
    positions[3, :, 1, 1] = np.nan
    confidence[3, 1, 1] = np.nan
    confidence[1, 1, 1] = np.nan  # Present but unscored, not a manual edit.
    original = load_poses.from_numpy(
        positions,
        confidence,
        individual_names=["mouse_0", "mouse_1"],
        keypoint_names=["nose", "tail"],
        fps=30,
        source_software="constructed",
    )
    snapshot = original.copy(deep=True)
    original_file = directory / "original.nc"
    save_dataset(original, original_file)
    viewers, widgets = [], []
    target = {"time": 1 / 30, "keypoint": "nose", "individual": "mouse_0"}
    missing = {"time": 3 / 30, "keypoint": "tail", "individual": "mouse_1"}
    unscored = {"time": 1 / 30, "keypoint": "tail", "individual": "mouse_1"}

    def load(path):
        viewer = Viewer(title=f"Constructed deletion replay: {expectation}")
        viewers.append(viewer)
        viewer.theme = "light"
        viewer.window.resize(1100, 750)
        loader = DataLoader(viewer)
        widgets.append(loader)
        viewer.window.add_dock_widget(loader, area="right", name="Load poses")
        loader.source_software_combo.setCurrentText("movement (netCDF)")
        loader.file_path_edit.setText(str(path))
        QtTest.QTest.mouseClick(loader.load_button, QtCore.Qt.LeftButton)
        app.processEvents()
        assert hasattr(loader, "points_layer"), "Qt loader failed"
        viewer.dims.set_point(0, 1)
        viewer.scene.camera.center = (0, 120, 100)
        viewer.scene.camera.zoom = 2
        loader.points_layer.mode = "select"
        QtTest.QTest.qWait(600)
        return viewer, loader.points_layer

    def save(viewer, path):
        saver = DataSaver(viewer)
        widgets.append(saver)
        viewer.window.add_dock_widget(saver, area="right", name="Save poses")
        assert saver.save_button.isEnabled()
        with patch.object(QFileDialog, "getSaveFileName", return_value=(str(path), "")):
            QtTest.QTest.mouseClick(saver.save_button, QtCore.Qt.LeftButton)
            app.processEvents()
        assert path.exists(), "Qt saver failed"
        with xr.open_dataset(path) as stored:
            return stored.load()

    def flag(ds, selection):
        return bool(ds.edited.sel(selection).item()) if "edited" in ds else None

    try:
        viewer, points = load(original_file)
        rows = np.flatnonzero(
            (points.data[:, 0] == 1)
            & (points.properties["keypoint"] == "nose")
            & (points.properties["individual"] == "mouse_0")
        )
        assert len(rows) == 1
        row = int(rows[0])
        assert row in points._view_indices and len(points._view_indices) == 4
        canvas = viewer.window._qt_viewer.canvas
        canvas._scene_canvas.set_current()
        renderer = glGetString(GL_RENDERER).decode()
        assert any(name in renderer.lower() for name in ["llvmpipe", "softpipe"])
        transform = canvas.view.transform * canvas.view.scene.transform
        xy = transform.map(list(points.data[row, 1:][::-1]))[:2]
        position = QtCore.QPoint(round(float(xy[0])), round(float(xy[1])))
        native = canvas._scene_canvas.native
        assert native.rect().contains(position)
        QtTest.QTest.mouseMove(native, position)
        QtTest.QTest.mouseClick(native, QtCore.Qt.LeftButton, pos=position)
        app.processEvents()
        assert points.selected_data == {row}, "Canvas click missed the intended point"
        QtTest.QTest.qWait(50)
        viewer.screenshot(
            path=str(captures / "before-delete.png"), canvas_only=False, flash=False
        )
        count = len(points.data)
        QtTest.QTest.keyClick(native, QtCore.Qt.Key_Delete)
        QtTest.QTest.qWait(250)
        assert len(points.data) == count - 1, (
            "The actual Delete key did not remove a point"
        )
        assert len(points._view_indices) == 3
        viewer.screenshot(
            path=str(captures / "after-delete.png"), canvas_only=False, flash=False
        )
        first_file = directory / "first-save.nc"
        first = save(viewer, first_file)
        expected = original.copy(deep=True)
        expected.position.loc[target] = np.nan
        expected.confidence.loc[target] = np.nan
        xr.testing.assert_equal(first.position, expected.position)
        xr.testing.assert_equal(first.confidence, expected.confidence)
        assert flag(first, target) is True
        assert flag(first, missing) is False and flag(first, unscored) is False
        second_viewer, second_points = load(first_file)
        assert len(second_points._view_indices) == 3
        second_file = directory / "second-save.nc"
        second = save(second_viewer, second_file)
        xr.testing.assert_equal(first.position, second.position)
        xr.testing.assert_equal(first.confidence, second.confidence)
        xr.testing.assert_equal(first.time, second.time)
        assert flag(second, target) is (True if expectation == "patched" else None)
        for selection in [missing, unscored]:
            assert flag(second, selection) in [None, False]
        final_viewer, final_points = load(second_file)
        assert len(final_points._view_indices) == 3
        full = final_points.metadata[POINTS_PROPERTIES_KEY]
        saved = full[
            (full["time"] == target["time"])
            & (full["keypoint"] == target["keypoint"])
            & (full["individual"] == target["individual"])
        ]
        assert len(saved) == 1 and bool(saved["position_is_nan"].iloc[0])
        loaded_flag = bool(saved["edited"].iloc[0]) if "edited" in saved else False
        assert loaded_flag is (expectation == "patched")
        final_viewer.screenshot(
            path=str(captures / "after-reexport-reload.png"),
            canvas_only=False,
            flash=False,
        )
        xr.testing.assert_identical(original, snapshot)
        sizes = {path.name: path.stat().st_size for path in directory.glob("*.nc")}
        assert sum(sizes.values()) < 1_000_000
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        assert peak < 4 * 1024**3
        return {
            "real_canvas_click_and_delete_key": True,
            "real_load_and_save_buttons": True,
            "renderer": renderer,
            "flag_after_first_save": flag(first, target),
            "flag_after_second_save": flag(second, target),
            "flag_in_final_loader": loaded_flag,
            "positions_confidence_and_time_preserved_after_reexport": True,
            "never_detected_and_unscored_controls_not_marked_edited": True,
            "original_dataset_unchanged": True,
            "netcdf_bytes": sizes,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "peak_rss_bytes": peak,
            "captures": {path.name: digest(path) for path in captures.glob("*.png")},
            "versions": {
                name: importlib.metadata.version(name)
                for name in ["napari", "PyQt6", "qtpy", "PyOpenGL"]
            },
        }
    finally:
        for viewer in reversed(viewers):
            viewer.close()
        app.processEvents()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--rendered",
        action="store_true",
        help="Use real CPU-rendered Qt canvas deletion and Save buttons",
    )
    args = parser.parse_args()
    if args.rendered:
        os.environ.setdefault("QT_API", "pyqt6")
    checkout = args.checkout.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = json.loads((PROJECT / "deletion-profile.json").read_text())
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    assert revision == profile["source_revision"]
    assert digest(checkout / "LICENSE") == profile["license_sha256"]
    module = checkout / "movement/napari/convert.py"
    assert digest(module) == profile[f"{args.expect}_convert_sha256"]
    patch_path = PROJECT / "deletion-provenance.patch"
    assert digest(patch_path) == profile["patch_sha256"]
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=checkout)
    if args.expect == "baseline":
        assert not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=checkout
        ).strip(), "Baseline must remain unmodified"
    else:
        assert diff == patch_path.read_bytes(), "Apply only the recorded deletion patch"
    tests = (
        ROOT / ".external/movement-deletion-patched/tests/test_deletion_provenance.py"
    )
    assert digest(tests) == profile["tests_sha256"]
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    sys.path.insert(0, str(checkout))
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="kufu-deletion-") as temporary:
        with patch.object(Path, "home", return_value=Path(temporary)):
            import movement
        from movement.napari import convert

        assert Path(movement.__file__).resolve().is_relative_to(checkout)
        assert Path(convert.__file__).resolve() == module
        import pytest

        xml = output.with_suffix(".xml")
        with (
            output.with_suffix(".log").open("w") as log,
            contextlib.redirect_stdout(log),
            contextlib.redirect_stderr(log),
        ):
            result = pytest.main(
                [
                    "--noconftest",
                    "-o",
                    "addopts=",
                    str(tests),
                    "-q",
                    f"--junitxml={xml}",
                ]
            )
        assert result == (1 if args.expect == "baseline" else 0)
        cases = list(ET.parse(xml).getroot().iter("testcase"))
        assert len(cases) == profile["constructed_cases"]
        assert not any(
            c.find("error") is not None or c.find("skipped") is not None for c in cases
        )
        failures = sorted(
            c.attrib["name"] for c in cases if c.find("failure") is not None
        )
        assert failures == (
            sorted(profile["baseline_failures"]) if args.expect == "baseline" else []
        )

        spec = importlib.util.spec_from_file_location("deletion_cases", tests)
        helpers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helpers)
        observations = {}
        for name, delete, move in [
            ("deletion_only", True, False),
            ("deletion_and_move", True, True),
            ("never_detected", False, False),
        ]:
            first = helpers.convert(helpers.dataset(), delete=delete, move=move)
            second = helpers.convert(first)
            target = {"time": 1 / 30, "keypoint": "nose", "individual": "mouse_0"}

            if name == "never_detected":
                target = {"time": 3 / 30, "keypoint": "tail", "individual": "mouse_1"}

            def flag(ds, target=target):
                return bool(ds.edited.sel(target).item()) if "edited" in ds else None

            observations[name] = {
                "flag_first": flag(first),
                "flag_second": flag(second),
            }
    report = {
        "source_revision": revision,
        "expectation": args.expect,
        "patch_sha256": profile["patch_sha256"] if args.expect == "patched" else None,
        "convert_sha256": digest(module),
        "input_kind": "Constructed poses: 4 frames, 2 keypoints, 2 individuals at 30 Hz; no recordings",
        "tests": len(cases),
        "passed": len(cases) - len(failures),
        "failed": failures,
        "native_reopen_cycles": [1, 2, 4],
        "observations": observations,
        "qt_or_canvas_created": args.rendered,
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["numpy", "pandas", "xarray", "pytest"]
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    if args.rendered:
        report["rendered"] = rendered_replay(output, args.expect)
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
