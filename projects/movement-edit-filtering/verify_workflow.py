"""Exercise real movement Qt widgets and callbacks on constructed poses.

Run in the pilot environment with movement's napari extra installed.
Default mode uses model events without a canvas. Optional --rendered mode
requires a real CPU software-rendered canvas. No video, research dataset
or network request is needed.
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import resource
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest.mock import patch


def main():
    """Load, edit, save, reload, and compare provenance-aware filtering."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--rendered",
        action="store_true",
        help="Use the actual napari canvas and a Qt mouse drag (CPU Mesa/Xvfb).",
    )
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    record_dir = Path(__file__).resolve().parent
    baseline = json.loads((record_dir / "movement-pilot-environment.json").read_text())[
        "source_revision"
    ]
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != baseline:
        parser.error("Use the recorded baseline checkout with the approved patch.")
    expected_patch = (record_dir / "movement-pilot.patch").read_bytes()
    actual_patch = subprocess.check_output(
        [
            "git",
            "diff",
            "--no-ext-diff",
            "--no-color",
            "HEAD",
            "--",
            "movement/filtering.py",
        ],
        cwd=checkout,
    )
    new_test = subprocess.run(
        [
            "git",
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--no-index",
            "--",
            "/dev/null",
            "tests/test_unit/test_filtering_edited.py",
        ],
        cwd=checkout,
        capture_output=True,
        check=False,
    )
    if new_test.returncode != 1 or actual_patch + new_test.stdout != expected_patch:
        parser.error("Checkout must contain exactly the approved pilot patch.")
    modified = subprocess.check_output(
        ["git", "diff", "HEAD", "--name-only"], cwd=checkout, text=True
    ).splitlines()
    if modified != ["movement/filtering.py"]:
        parser.error("Other tracked host changes would confound this check.")
    sys.path.insert(0, str(checkout))
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_API", "pyqt6")
    start = perf_counter()

    with TemporaryDirectory(prefix="movement-workflow-") as folder:
        scratch = Path(folder)
        # Redirect only movement's import-time log, not filtering or IO.
        with patch.object(Path, "home", return_value=scratch):
            import movement

        import numpy as np
        import xarray as xr
        from movement.filtering import filter_by_confidence
        from movement.io import load_poses, save_dataset
        from movement.napari.loader_widgets import DataLoader
        from movement.napari.save_widget import DataSaver
        from napari.components import ViewerModel
        from qtpy import QtCore, QtGui, QtTest
        from qtpy.QtWidgets import QApplication, QFileDialog

        assert Path(movement.__file__).resolve().is_relative_to(checkout)
        app = QApplication.instance() or QApplication([])
        assert app.platformName() == ("xcb" if args.rendered else "offscreen")
        positions = np.arange(32, dtype=float).reshape(4, 2, 2, 2)
        if args.rendered:
            for frame in range(4):
                for keypoint in range(2):
                    for individual in range(2):
                        positions[frame, :, keypoint, individual] = [
                            40 + frame * 3 + individual * 100 - keypoint * 10,
                            45 + frame * 2 + individual * 20 + keypoint * 30,
                        ]
        confidence = np.full((4, 2, 2), 0.9)
        confidence[1, 0, 0] = 0.1  # A prediction subsequently corrected.
        confidence[1, 1, 1] = np.nan  # An unscored, unedited prediction.
        positions[3, :, 1, 0] = np.nan  # Originally missing, never edited.
        confidence[3, 1, 0] = np.nan
        original = load_poses.from_numpy(
            positions,
            confidence,
            individual_names=["mouse_0", "mouse_1"],
            keypoint_names=["nose", "tail"],
            fps=30,
            source_software="constructed",
        )
        original_snapshot = original.copy(deep=True)
        original_file = scratch / "original.nc"
        save_dataset(original, original_file)
        widgets = []
        viewers = []
        render_evidence = {}
        captures = args.output.parent / "canvas"
        if args.rendered:
            captures.mkdir(parents=True, exist_ok=True)

        def load_widget(path):
            if args.rendered:
                from napari import Viewer

                viewer = Viewer(title="Constructed movement editing workflow")
                viewer.theme = "light"
                viewers.append(viewer)
                viewer.window.resize(1100, 750)
            else:
                viewer = ViewerModel()
            widget = DataLoader(viewer)
            widgets.append(widget)
            if args.rendered:
                viewer.window.add_dock_widget(widget, area="right", name="Load poses")
            widget.source_software_combo.setCurrentText("movement (netCDF)")
            widget.file_path_edit.setText(str(path))
            if args.rendered:
                QtTest.QTest.mouseClick(widget.load_button, QtCore.Qt.LeftButton)
            else:
                widget.load_button.click()
            app.processEvents()
            assert hasattr(widget, "points_layer"), "Qt loader failed"
            return viewer, widget

        def find_row(points, frame, keypoint, individual):
            props = points.properties
            rows = np.flatnonzero(
                (points.data[:, 0] == frame)
                & (props["keypoint"] == keypoint)
                & (props["individual"] == individual)
            )
            assert len(rows) == 1
            return int(rows[0])

        def save_widget(viewer, path):
            saver = DataSaver(viewer)
            widgets.append(saver)
            if args.rendered:
                viewer.window.add_dock_widget(saver, area="right", name="Save poses")
            assert saver.save_button.isEnabled()
            # Replace the file picker only. Conversion and writing stay real.
            with patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(path), "")
            ):
                if args.rendered:
                    QtTest.QTest.mouseClick(saver.save_button, QtCore.Qt.LeftButton)
                else:
                    saver.save_button.click()
                app.processEvents()
            assert path.exists(), "Qt saver failed"
            with xr.open_dataset(path) as stored:
                return stored.load()

        viewer, loader = load_widget(original_file)
        points = loader.points_layer
        row = find_row(points, 1, "nose", "mouse_0")
        if args.rendered:
            from OpenGL.GL import GL_RENDERER, glGetString

            viewer.dims.set_point(0, 1)
            viewer.scene.camera.center = (0, 120, 100)
            viewer.scene.camera.zoom = 2
            points.mode = "select"
            QtTest.QTest.qWait(800)
            assert row in points._view_indices
            assert len(points._view_indices) == 4
            canvas = viewer.window._qt_viewer.canvas
            canvas._scene_canvas.set_current()
            renderer = glGetString(GL_RENDERER).decode()
            assert any(name in renderer.lower() for name in ("llvmpipe", "softpipe"))
            render_evidence["renderer"] = renderer
            viewer.screenshot(
                path=str(captures / "before.png"), canvas_only=False, flash=False
            )
            transform = canvas.view.transform * canvas.view.scene.transform

            def screen_point(yx):
                xy = transform.map(list(yx[::-1]))[:2]
                return QtCore.QPoint(round(float(xy[0])), round(float(xy[1])))

            start_point = screen_point(points.data[row, 1:])
            end_point = screen_point(np.array([200.0, 100.0]))
            native = canvas._scene_canvas.native
            assert native.rect().contains(start_point) and native.rect().contains(
                end_point
            )
            QtTest.QTest.mouseMove(native, start_point)
            QtTest.QTest.mouseClick(native, QtCore.Qt.LeftButton, pos=start_point)
            app.processEvents()
            assert row in points.selected_data, "Canvas click missed the intended point"
            QtTest.QTest.mousePress(native, QtCore.Qt.LeftButton, pos=start_point)
            for step in range(1, 11):
                destination = start_point + (end_point - start_point) * (step / 10)
                # QTest.mouseMove does not reliably retain held buttons under
                # Xvfb. Send a complete Qt pointer event through the real canvas.
                event = QtGui.QMouseEvent(
                    QtCore.QEvent.MouseMove,
                    QtCore.QPointF(destination),
                    QtCore.QPointF(native.mapToGlobal(destination)),
                    QtCore.Qt.NoButton,
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.NoModifier,
                )
                app.sendEvent(native, event)
                QtTest.QTest.qWait(30)
            QtTest.QTest.mouseRelease(native, QtCore.Qt.LeftButton, pos=end_point)
            QtTest.QTest.qWait(300)
            np.testing.assert_allclose(points.data[row, 1:], [200, 100], atol=1)
            expected_xy = points.data[row, 1:][::-1].copy()
            render_evidence["mouse_drag_xy"] = expected_xy.tolist()
            render_evidence["real_canvas_mouse_drag"] = True
            viewer.screenshot(
                path=str(captures / "after-drag.png"), canvas_only=False, flash=False
            )
        else:
            points.data[row, 1:] = [200.0, 100.0]  # napari uses y, x.
            points.events.data(action="changed", data_indices=(row,))
            expected_xy = [100, 200]
        assert points.properties["edited"][row]
        assert np.isnan(points.properties["confidence"][row])
        row = find_row(points, 2, "nose", "mouse_1")
        points.remove([row])
        edited_file = scratch / "edited.nc"
        corrected = save_widget(viewer, edited_file)
        edit = {"time": 1 / 30, "keypoint": "nose", "individual": "mouse_0"}
        unknown = {"time": 1 / 30, "keypoint": "tail", "individual": "mouse_1"}
        removed = {"time": 2 / 30, "keypoint": "nose", "individual": "mouse_1"}
        missing = {"time": 3 / 30, "keypoint": "tail", "individual": "mouse_0"}
        np.testing.assert_array_equal(
            corrected.position.sel(edit).sel(space=["x", "y"]), expected_xy
        )
        assert bool(corrected.edited.sel(edit))
        assert bool(corrected.edited.sel(removed))
        assert not bool(corrected.edited.sel(unknown))
        assert not bool(corrected.edited.sel(missing))
        assert bool(corrected.position.sel(removed).isnull().all())
        assert bool(corrected.position.sel(missing).isnull().all())
        xr.testing.assert_equal(corrected.time, original.time)
        xr.testing.assert_identical(original, original_snapshot)

        second_viewer, second_loader = load_widget(edited_file)
        row = find_row(second_loader.points_layer, 1, "nose", "mouse_0")
        assert second_loader.points_layer.properties["edited"][row]
        second_file = scratch / "reexported.nc"
        reexported = save_widget(second_viewer, second_file)
        corrected_snapshot = corrected.copy(deep=True)
        explicit = filter_by_confidence(
            corrected.position,
            corrected.confidence,
            keep_points_with_nan_confidence=False,
            edited=corrected.edited,
        )
        legacy_keep = filter_by_confidence(corrected.position, corrected.confidence)
        legacy_drop = filter_by_confidence(
            corrected.position,
            corrected.confidence,
            keep_points_with_nan_confidence=False,
        )
        assert bool(explicit.sel(edit).notnull().all())
        assert bool(explicit.sel(unknown).isnull().all())
        assert bool(explicit.sel(removed).isnull().all())
        assert bool(explicit.sel(missing).isnull().all())
        assert bool(legacy_keep.sel(edit).notnull().all())
        assert bool(legacy_keep.sel(unknown).notnull().all())
        assert bool(legacy_drop.sel(edit).isnull().all())
        assert bool(legacy_drop.sel(unknown).isnull().all())
        xr.testing.assert_identical(corrected, corrected_snapshot)
        repeated = filter_by_confidence(
            reexported.position,
            reexported.confidence,
            keep_points_with_nan_confidence=False,
            edited=reexported.edited,
        )
        xr.testing.assert_equal(explicit, repeated)
        if args.rendered:
            filtered_file = scratch / "filtered.nc"
            filtered = corrected.copy(deep=True)
            filtered["position"] = explicit
            save_dataset(filtered, filtered_file)
            filtered_viewer, filtered_loader = load_widget(filtered_file)
            filtered_points = filtered_loader.points_layer
            corrected_row = find_row(filtered_points, 1, "nose", "mouse_0")
            np.testing.assert_array_equal(
                filtered_points.data[corrected_row, 1:][::-1], expected_xy
            )
            unknown_rows = (
                (filtered_points.data[:, 0] == 1)
                & (filtered_points.properties["keypoint"] == "tail")
                & (filtered_points.properties["individual"] == "mouse_1")
            )
            assert not unknown_rows.any()
            filtered_viewer.dims.set_point(0, 1)
            filtered_viewer.scene.camera.center = (0, 120, 100)
            filtered_viewer.scene.camera.zoom = 2
            QtTest.QTest.qWait(500)
            assert corrected_row in filtered_points._view_indices
            assert len(filtered_points._view_indices) == 3
            filtered_viewer.screenshot(
                path=str(captures / "after-filter-reload.png"),
                canvas_only=False,
                flash=False,
            )
            render_evidence["rendered_filter_reload"] = True
        for widget in reversed(widgets):
            widget.close()
        for viewer in reversed(viewers):
            viewer.close()
        app.processEvents()
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_bytes = peak if sys.platform == "darwin" else peak * 1024
        assert peak_bytes < 4 * 1024**3, "Peak RSS exceeded the pilot cap"
        sizes = {p.name: p.stat().st_size for p in scratch.glob("*.nc")}
        assert sum(sizes.values()) < 1_000_000
        report = {
            "source_revision": revision,
            "approved_patch_sha256": hashlib.sha256(
                (record_dir / "movement-pilot.patch").read_bytes()
            ).hexdigest(),
            "scope": (
                "real rendered napari canvas, Qt mouse drag and save/reload/filter"
                if args.rendered
                else "real Qt widgets and napari model events; no rendered canvas"
            ),
            **({"rendered": render_evidence} if args.rendered else {}),
            "checks": {
                "implementation_matches_approved_patch": True,
                "real_loader_and_saver_buttons": True,
                "move_callback_creates_edit_flag_and_nan_confidence": True,
                "removal_stays_missing": True,
                "originally_missing_point_stays_missing": True,
                "corrected_xy_and_time_coordinates_preserved": True,
                "reload_restores_moved_point_edit_flag": True,
                "explicit_policy_keeps_correction_drops_unknown": True,
                "legacy_policies_cannot_distinguish_two_nan_scores": True,
                "input_dataset_not_mutated": True,
                "filtering_decisions_survive_second_gui_export": True,
            },
            "deleted_point_edit_flag_after_first_export": bool(
                corrected.edited.sel(removed)
            ),
            "deleted_point_edit_flag_after_second_export": bool(
                reexported.edited.sel(removed)
            ),
            "netcdf_bytes": sizes,
            "elapsed_seconds": round(perf_counter() - start, 3),
            "peak_rss_bytes": peak_bytes,
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "dependencies": {
                d.metadata["Name"]: d.version
                for d in sorted(
                    importlib.metadata.distributions(),
                    key=lambda d: d.metadata["Name"].lower(),
                )
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "dependencies"}))


if __name__ == "__main__":
    main()
