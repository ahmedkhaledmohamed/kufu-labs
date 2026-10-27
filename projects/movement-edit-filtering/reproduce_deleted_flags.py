"""Isolate deletion-provenance loss in unmodified movement conversion code.

This diagnostic uses constructed arrays, no filtering, no Qt, and no files
containing recordings. A successful run records the observed bug, not a fix.
"""

import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


def main():
    """Compare two consecutive conversions for three small scenarios."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    baseline = json.loads(
        (Path(__file__).parent / "movement-pilot-environment.json").read_text()
    )["source_revision"]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
    ).strip()
    if (
        revision != baseline
        or subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=checkout
        ).strip()
    ):
        parser.error(
            "Use a clean, unmodified checkout of the recorded revision."
        )
    sys.path.insert(0, str(checkout))
    with TemporaryDirectory(prefix="movement-deletion-log-") as scratch:
        with patch.object(Path, "home", return_value=Path(scratch)):
            import movement

        import numpy as np
        import xarray as xr
        from movement.napari import convert

        assert Path(convert.__file__).resolve().is_relative_to(checkout)
        assert Path(movement.__file__).resolve().is_relative_to(checkout)

        def dataset(missing=False):
            positions = np.arange(4, dtype=float).reshape(2, 2, 1, 1)
            confidence = np.full((2, 1, 1), 0.9)
            if missing:
                positions[0] = np.nan
                confidence[0] = np.nan
            return xr.Dataset(
                {
                    "position": (
                        ("time", "space", "keypoint", "individual"),
                        positions,
                    ),
                    "confidence": (
                        ("time", "keypoint", "individual"),
                        confidence,
                    ),
                },
                coords={
                    "time": [0.0, 1.0],
                    "space": ["x", "y"],
                    "keypoint": ["nose"],
                    "individual": ["mouse_0"],
                },
                attrs={"ds_type": "poses", "fps": 1},
            )

        def conversion(ds, delete=False, move=False):
            tracks, _, full_properties = convert.ds_to_napari_layers(ds)
            present = ~np.isnan(tracks[:, 2:]).any(axis=1)
            full_properties["position_is_nan"] = ~present
            points = tracks[present, 1:].copy()
            live = full_properties.loc[present].copy()
            if delete:
                keep = points[:, 0] != 0
                points = points[keep]
                live = live.loc[keep].copy()
            if move:
                points[:, 1:] = [200.0, 100.0]
                live["edited"] = True
                live["confidence"] = np.nan
            return convert.napari_layers_to_ds(
                points, live, full_properties, attrs=ds.attrs
            )

        def flag(ds, frame):
            if "edited" not in ds:
                return None
            return bool(ds.edited.isel(time=frame, keypoint=0, individual=0))

        observations = {}
        for name in ["deletion_only", "deletion_and_move", "never_detected"]:
            first = conversion(
                dataset(missing=name == "never_detected"),
                delete=name != "never_detected",
                move=name == "deletion_and_move",
            )
            second = conversion(first)
            xr.testing.assert_equal(first.position, second.position)
            xr.testing.assert_equal(first.confidence, second.confidence)
            assert bool(second.position.isel(time=0).isnull().all())
            observations[name] = {
                "missing_point_flag_first": flag(first, 0),
                "missing_point_flag_second": flag(second, 0),
                "edited_variable_present_first": "edited" in first,
                "edited_variable_present_second": "edited" in second,
                "finite_point_flag_first": flag(first, 1),
                "finite_point_flag_second": flag(second, 1),
                "positions_and_confidence_unchanged": True,
            }
        assert (
            observations["deletion_only"]["missing_point_flag_first"] is True
        )
        assert (
            observations["deletion_only"]["missing_point_flag_second"] is None
        )
        assert (
            observations["deletion_and_move"]["missing_point_flag_second"]
            is False
        )
        assert (
            observations["deletion_and_move"]["finite_point_flag_second"]
            is True
        )
        assert (
            observations["never_detected"]["edited_variable_present_second"]
            is False
        )
        report = {
            "source_revision": revision,
            "source_worktree_clean": True,
            "filtering_patch_applied": False,
            "qt_or_canvas_created": False,
            "interpretation": "Bug reproduced; no fix implemented.",
            "python": sys.version.split()[0],
            "versions": {
                name: importlib.metadata.version(name)
                for name in ["numpy", "pandas", "xarray"]
            },
            "observations": observations,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report))


if __name__ == "__main__":
    main()
