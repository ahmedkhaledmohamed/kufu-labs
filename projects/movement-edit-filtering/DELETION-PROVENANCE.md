# Deleted-point edit provenance across repeated conversions

Local diagnostic only. No fix, upstream issue, additional comment, or new publication has been made. The existing filtering patch is unchanged.

The draft below was verified using a clean, unmodified upstream worktree at the pinned revision. Its standalone snippet ran and printed the observed loss. A [three-scenario diagnostic](reproduce_deleted_flags.py) and [result](deletion-result.json) additionally cover a mixed move/delete case and an originally missing control. The diagnostic's successful exit confirms reproduction of the bug, not a repair.

## Proposed upstream issue

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

## Local follow-up boundaries

Read the current issue/PR discussion before publishing; bounded searches found the original closed request and implementation but no specific repeated-conversion fix. That is not proof that no overlapping work exists.

Potential repair direction, not implemented: use loaded edit metadata for points missing from the live layer while preserving current live flags and detecting new removals. Check explicit reset behaviour carefully; blindly OR-ing every loaded flag could reintroduce flags a live operation intentionally clears. Keep originally missing, unedited points false and retain existing coordinate-drop behaviour.

Run the independent diagnostic in the pilot environment with an unmodified source worktree:

```sh
python projects/movement-edit-filtering/reproduce_deleted_flags.py --checkout /path/to/clean-pinned-movement --output /path/to/deletion-result.json
```

Only explicit approval of the exact upstream issue text authorises filing it. Any repair implementation is a separate scope decision. Do not change the approved filtering patch or add unsolicited follow-ups to the pending API question.
