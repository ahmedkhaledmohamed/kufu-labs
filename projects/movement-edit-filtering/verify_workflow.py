"""Exercise real movement Qt widgets and callbacks on constructed poses.

Run in the pilot environment with movement's napari extra installed.
No canvas, video, research dataset, or network request is needed.
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
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    record_dir = Path(__file__).resolve().parent
    baseline = json.loads(
        (record_dir / "movement-pilot-environment.json").read_text()
    )["source_revision"]
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != baseline:
        parser.error(
            "Use the recorded baseline checkout with the approved patch."
        )
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
    if (
        new_test.returncode != 1
        or actual_patch + new_test.stdout != expected_patch
    ):
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
        from qtpy.QtWidgets import QApplication, QFileDialog

        assert Path(movement.__file__).resolve().is_relative_to(checkout)
        app = QApplication.instance() or QApplication([])
        assert app.platformName() == "offscreen", (
            "Use offscreen Qt for this pilot"
        )
        positions = np.arange(32, dtype=float).reshape(4, 2, 2, 2)
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

        def load_widget(path):
            viewer = ViewerModel()
            widget = DataLoader(viewer)
            widgets.append(widget)
            widget.source_software_combo.setCurrentText("movement (netCDF)")
            widget.file_path_edit.setText(str(path))
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
            assert saver.save_button.isEnabled()
            # Replace the file picker only. Conversion and writing stay real.
            with patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(path), "")
            ):
                saver.save_button.click()
                app.processEvents()
            assert path.exists(), "Qt saver failed"
            with xr.open_dataset(path) as stored:
                return stored.load()

        viewer, loader = load_widget(original_file)
        points = loader.points_layer
        row = find_row(points, 1, "nose", "mouse_0")
        points.data[row, 1:] = [200.0, 100.0]  # napari uses y, x.
        points.events.data(action="changed", data_indices=(row,))
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
            corrected.position.sel(edit).sel(space=["x", "y"]), [100, 200]
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
        legacy_keep = filter_by_confidence(
            corrected.position, corrected.confidence
        )
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
        for widget in reversed(widgets):
            widget.close()
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
                "real Qt widgets and napari model events; no rendered canvas"
            ),
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
        print(
            json.dumps(
                {k: v for k, v in report.items() if k != "dependencies"}
            )
        )


if __name__ == "__main__":
    main()
