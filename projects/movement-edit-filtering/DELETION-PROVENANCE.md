# Deleted-point edit provenance across repeated conversions

Status, 30 October 2026: a separate local repair and 15-case regression suite now pass; nothing new has been submitted upstream. The existing filtering patch remains unchanged. The original report is [movement #1174](https://github.com/neuroinformatics-unit/movement/issues/1174).

## Current implementation and evidence

People proofreading animal-pose data need to distinguish a deliberate deletion from a point the tracker never detected. Both have missing coordinates, but their provenance differs. The loss happens in the existing `napari_layers_to_ds` converter after a dataset is reopened: absent live rows have no current flags, and a deletion from an earlier session is already missing at load time.

The separate [repair](deletion-provenance.patch) preserves loaded flags only for points that remain missing from the live layer. Current live flags still take precedence for points present in the layer; new removals retain the existing inference. Coordinate trimming and the all-points-missing error are unchanged. This is a converter patch using existing metadata, without a new application or schema.

| Scenario after reopening and converting again | Unmodified main | Local candidate |
| --- | --- | --- |
| Deletion only | Entire `edited` variable disappears | Deleted-point flag remains true |
| Deletion plus moved point | Deleted-point flag becomes false | Deleted-point flag remains true |
| Never-detected, unedited point | No edit flag | No edit flag |

Both revisions use source `00e7a232c90ac451e27b1a72f41e7234878d0417`, current upstream main when checked. The [profile](deletion-profile.json) locks source, converter, test, patch and BSD licence hashes. [Baseline](deletion-baseline.json) has six failing deletion cases and nine passing controls. [Patched](deletion-patched.json) passes all 15. Native netCDF save/reopen cycles of 1, 2 and 4 compare every position, confidence and edit flag. Additional cases cover clearing a live flag, dropping entirely empty keypoints/individuals and rejecting an entirely missing dataset. These fixtures have four frames, two keypoints and two individuals at 30 Hz; they are not recordings.

All 45 existing conversion tests passed in the existing Linux arm64/Python 3.13.18 CPU-Mesa/Xvfb environment. This runs real napari/Qt fixtures, excluding the root startup hook that downloads recordings. The normal macOS viewer run crashed during startup; the pure four-case existing round trip passed there, and the new suite passed on Python 3.13.2. No failed assertion was hidden. Existing pandas deprecation warnings and read-only pytest-cache warnings remain visible in local logs. Full host suite, rendered deletion gestures, re-add UI, explicit reset-button interactions, real recordings, researcher benefit and upstream acceptance remain unverified. The live-flag test clears the converter input directly; it is not a reset-button demonstration.

## Existing upstream work

On 29 October, [another contributor reported the same missing-point preservation approach](https://github.com/neuroinformatics-unit/movement/issues/1174#issuecomment-6501514560), with their own regression. That report precedes this local repair. No linked implementation was available in the comment and no matching open PR was found in bounded searches on 30 October. Their code has not been assessed here. Do not present the approach as a novel Kufu design or open a competing upstream PR. The useful next step is to retain independent regression evidence and recheck the existing contribution before any separately authorised discussion.

## Reproduce the local candidate

Use a fresh Kufu worktree and Python 3.13. The preparation command refuses to overwrite existing task checkouts. Public package installation uses the existing host constraints; no recordings or models are requested.

```sh
python3 site/prepare_movement.py --deletion
python3.13 -m venv .external/movement-deletion-env
.external/movement-deletion-env/bin/python -m pip install --isolated --index-url https://pypi.org/simple -c site/requirements-ci.txt -e '.external/movement-deletion-patched[napari]' pytest pytest-qt pytest-mock
.external/movement-deletion-env/bin/python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-clean --expect baseline --output .runs/deletion/baseline.json
.external/movement-deletion-env/bin/python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-patched --expect patched --output .runs/deletion/patched.json
```

The [runner](verify_deletion.py) checks the imported source path and hashes before execution, asserts the exact baseline failure cases, rejects skipped or errored tests, and requires the patched suite to pass. JSON is sanitised summary evidence; detailed logs and JUnit reports stay in `.runs`. The required CI addition runs both revisions and all 45 existing conversion cases, retaining results for the site. Cloud execution of this addition is pending publication. The problem page shows retained output; it does not start Qt or a Vercel experiment.

Keep the [upstream BSD licence](UPSTREAM-LICENSE) with this patch. No source loader, filter API or biological interpretation changes are included.

## Original diagnostic

The draft below was verified using a clean, unmodified upstream worktree at the pinned revision. Its standalone snippet ran and printed the observed loss. A [three-scenario diagnostic](reproduce_deleted_flags.py) and [result](deletion-result.json) additionally cover a mixed move/delete case and an originally missing control. The diagnostic's successful exit confirms reproduction of the bug, not a repair.

## Original upstream report

**Title:** Deleted-point edit flags are lost after reopening and reexporting pose data

## Summary

A deleted point's `edited=True` provenance is lost when an exported pose dataset is loaded and converted back again without further edits. With only deletions, the second conversion drops the entire `edited` variable. With a deletion plus a moved finite point, the variable remains but the deleted point becomes `edited=False`.

This appears related to #1047 and #1057: the first export correctly distinguishes a deliberate deletion from a never-detected point, but a later session loses that distinction. The loaded-baseline policy described in #1137 also suggests saved edits should remain intact.

## Environment

Reproduced on an unmodified checkout of main at `39ee15e29706150d7d4f60ba617aa99d2027eed7`, with Python 3.13.2, NumPy 2.5.4, pandas 3.1.0, and xarray 2026.9.0. This reproducer does not use Qt, a canvas, recordings, or a filtering modification.

## Minimal reproduction

```python
import numpy as np
import pandas as pd
from movement.napari.convert import ds_to_napari_layers, napari_layers_to_ds

# Two originally present points; frame 0 was deliberately removed.
original_properties = pd.DataFrame({
    "time": [0.0, 1.0],
    "keypoint": ["nose", "nose"],
    "individual": ["mouse_0", "mouse_0"],
    "confidence": [0.9, 0.9],
    "position_is_nan": [False, False],
})
first = napari_layers_to_ds(
    np.array([[1.0, 3.0, 2.0]]),  # frame, y, x: only frame 1 remains
    original_properties.iloc[[1]].copy(),
    original_properties,
    attrs={"fps": 1, "ds_type": "poses"},
)
assert first.edited.isel(time=0).item() is True

# Reopen the exported dataset, drop NaN rows as the loader does, reexport.
tracks, _, loaded_properties = ds_to_napari_layers(first)
present = ~np.isnan(tracks[:, 2:]).any(axis=1)
loaded_properties["position_is_nan"] = ~present
second = napari_layers_to_ds(
    tracks[present, 1:],
    loaded_properties.loc[present].copy(),
    loaded_properties,
    attrs=first.attrs,
)
print("First export has edited:", "edited" in first)
print("Second export has edited:", "edited" in second)
assert "edited" not in second  # Observed loss, not the desired behaviour.
```

Output:

```text
First export has edited: True
Second export has edited: False
```

## Expected and observed behaviour

A previously deleted point should remain distinguishable from a point that was never detected, unless the edit is explicitly reset or its coordinate is deliberately removed from the dataset. Both frames and the keypoint/individual remain present in this example.

The first conversion sets the missing point's flag to true. After reloading, that point is absent from the live layer, so its live flag is filled with false; it was already missing at load time, so the new-removal inference does not restore it. If no other flags remain true, `edited` is dropped entirely.

Positions and confidence values remain unchanged in the reproduced second conversion. The issue is loss of manual-edit provenance; this report does not claim numerical tracking corruption or a scientific outcome.

## Scope

A separate three-scenario check confirms deletion-only loss, deletion-plus-move loss, and the control case where a never-detected point correctly has no edit flag. No fix is included. Would preserving loaded edit flags for missing points fit the intended saved-edit semantics, and should this be tracked as a follow-up to #1047?

## Follow-up boundary

Keep this candidate separate from the filtering patch. Recheck #1174 and the existing contributor's work before any upstream submission; no new issue, comment, fork push or PR is authorised by this local implementation. Preserve never-detected controls and live-flag semantics when assessing any alternative.
