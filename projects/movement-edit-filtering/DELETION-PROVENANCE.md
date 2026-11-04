# Deleted-point edit provenance across repeated conversions

Status, 3 November 2026: devanshc777 has opened draft movement PR #1190. Independent local checks of its exact base/head confirm that its head passes all 15 existing Kufu cases, all 49 selected upstream conversion cases and the real Qt deletion/save/reopen replay. The PR is not merged or released. Our local candidate remains separate, and the filtering patch is unchanged. The original report is [movement #1174](https://github.com/neuroinformatics-unit/movement/issues/1174).

## Current implementation and evidence

People proofreading animal-pose data need to distinguish a deliberate deletion from a point the tracker never detected. Both have missing coordinates, but their provenance differs. The loss happens in the existing `napari_layers_to_ds` converter after a dataset is reopened: absent live rows have no current flags, and a deletion from an earlier session is already missing at load time.

The separate [repair](deletion-provenance.patch) preserves loaded flags only for points that remain missing from the live layer. Current live flags still take precedence for points present in the layer; new removals retain the existing inference. Coordinate trimming and the all-points-missing error are unchanged. This is a converter patch using existing metadata, without a new application or schema.

| Scenario after reopening and converting again | Unmodified main | Local candidate |
| --- | --- | --- |
| Deletion only | Entire `edited` variable disappears | Deleted-point flag remains true |
| Deletion plus moved point | Deleted-point flag becomes false | Deleted-point flag remains true |
| Never-detected, unedited point | No edit flag | No edit flag |

Both revisions use source `00e7a232c90ac451e27b1a72f41e7234878d0417`, current upstream main when checked. The [profile](deletion-profile.json) locks source, converter, test, patch and BSD licence hashes. [Baseline](deletion-baseline.json) has six failing deletion cases and nine passing controls. [Patched](deletion-patched.json) passes all 15. Native netCDF save/reopen cycles of 1, 2 and 4 compare every position, confidence and edit flag. Additional cases cover clearing a live flag, dropping entirely empty keypoints/individuals and rejecting an entirely missing dataset. These fixtures have four frames, two keypoints and two individuals at 30 Hz; they are not recordings.

All 45 existing conversion tests passed in the existing Linux arm64/Python 3.13.18 CPU-Mesa/Xvfb environment. This runs real napari/Qt fixtures, excluding the root startup hook that downloads recordings. The normal macOS viewer run crashed during startup; the pure four-case existing round trip passed there, and the new suite passed on Python 3.13.2. No failed assertion was hidden. Existing pandas deprecation warnings and read-only pytest-cache warnings remain visible in local logs. Full host suite, re-add UI, explicit reset-button interactions, real recordings, researcher benefit and upstream acceptance remain unverified. The rendered deletion follow-up below now covers the actual removal gesture and Save/reopen path. The live-flag test clears the converter input directly; it is not a reset-button demonstration.

## Rendered deletion workflow

The optional `--rendered` replay now uses the actual source-locked plugin in napari 0.9.2 and PyQt6 6.11.0. It loads four constructed frames, selects the intended nose point on frame 1 through a Qt canvas click, sends the real Delete key, and checks that exactly that point disappeared. The real Load and Save buttons write/reopen netCDF twice; only the file picker destination is replaced. No point-removal method or synthetic model event substitutes for the keyboard action.

| Actual host step | Unmodified source | Existing candidate |
| --- | --- | --- |
| First Save after deletion | Deleted-point flag true | Deleted-point flag true |
| Reopen, then second Save | Entire edit variable absent | Deleted-point flag true |
| Load the second file | Loaded flag false | Loaded flag true |

All positions, confidence values and time coordinates are equal across reexport; the deleted coordinate remains missing. Never-detected and unscored-but-present controls are not marked edited, and the original dataset stays unchanged. The difference is saved provenance, not a coordinate correction. These assertions accompany the existing six baseline failures and fifteen passing candidate regression cases.

Inspect the actual captures: [point before deletion](deletion-before.png), [after the Delete key](deletion-after-delete.png), [baseline after reexport/reload](deletion-baseline-reloaded.png), and [candidate after reexport/reload](deletion-patched-reloaded.png). Screenshots show the real interaction and missing point; the flag difference comes from the saved-file and loader metadata recorded in the JSON results and comparison table. Geometry remains the same in both revisions. The build verifies that all four capture hashes match their source reports.

Both local runs used the existing Linux arm64 CPU-Mesa image with networking disabled, two CPUs, a three-GiB memory cap, read-only source and generated-data/temp writes only. Each measured replay took about 8–9 seconds, with peak Python RSS below 850 MiB; the JSON records retain exact total/rendered timings and peak RSS. Its three netCDF files total less than 34 KB. The first container launch stalled in Xvfb before Python started; the retained successful runs use an init process. No recordings, model weights or GPU were used.

After the documented source/dependency setup and Linux GUI libraries, run:

```sh
QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1400x1000x24' python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-clean --expect baseline --output .runs/deletion-gui/baseline.json --rendered
QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1400x1000x24' python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-patched --expect patched --output .runs/deletion-gui/patched.json --rendered
```

Use a new output location: native files and captures are retained under `rendered-baseline` and `rendered-patched`. The maintained CI addition runs both inside the existing scientific job and copies its fresh results/captures into the tested site. Local replay and site checks are the publication gate; the new rendered CI integration remains pending reviewed publication. The webpage displays retained results and starts no Qt application or hosted experiment. Reset/re-add gestures, the full host suite, real recordings and researcher benefit remain unverified.

## Existing upstream work

On 29 October, [devanshc777 independently reproduced the bug and reported a small fix with a regression test](https://github.com/neuroinformatics-unit/movement/issues/1174#issuecomment-6501514560). Their reported missing-point preservation approach precedes this local repair. Kufu's contribution is the original reproducible issue report and independent converter/rendered regression evidence; the repair approach is not a novel Kufu design.

On 3 November, [maintainer anna-teruel acknowledged that the existing round-trip test covers moved points but misses removed ones](https://github.com/neuroinformatics-unit/movement/issues/1174#issuecomment-6611020419), and invited that contributor to open a PR. This supports the reported bug and confirms maintainer interest in a fix. It is not acceptance or release of our local candidate, and no researcher outcome has been measured.

The maintainer also clarified that adding points is not supported yet and belongs to [movement #1060](https://github.com/neuroinformatics-unit/movement/issues/1060). Adding a deleted point back should therefore stay outside this deletion-preservation fix rather than become a prerequisite for it.

The contributor subsequently opened [draft PR #1190](https://github.com/neuroinformatics-unit/movement/pull/1190). Its base is `96733f808885300cc3d86b11e2c5189997671b65`; the assessed head is `78e41a2c726ddd4733f9ca46a78034a5a23c8d47`. The diff adds missing-point preservation in the converter and four parameterized regression cases. The base converter hash is identical to our earlier baseline. No Kufu patch was applied to either revision.

## Independent validation of draft PR #1190

The [profile](upstream-1190-profile.json) locks the base/head source, converter, PR test file, reused Kufu test source and BSD licence hashes. The [comparison runner](verify_upstream_1190.py) checks clean source/import origins and extracts the exact existing 15-case Kufu suite without applying the local implementation. It runs the head's selected upstream conversion module against both source revisions, loading only the required constructed-data and Qt fixtures. The upstream root startup hook that downloads recordings is excluded; unexpected failures, errors or skips reject the run.

| Check | PR base | Draft head |
| --- | --- | --- |
| Existing Kufu deletion/control cases | 9 pass, 6 expected deletion failures | 15 pass |
| Selected upstream conversion module, including four PR regressions | 45 pass, 4 expected new-test failures | 49 pass |
| Deleted-point flag after second real Qt Save | Entire edit variable absent | true |
| Deleted-point flag after final real Qt Load | false | true |

The existing independent cases cover deletion-only and mixed move/delete edits through one, two and four native netCDF reopen cycles, never-detected controls, live-flag clearing and empty coordinates. The rendered replay selects the target through an actual canvas click, sends Delete, and uses the real Save/Load buttons twice. All positions, confidence values and time coordinates remain correct across reexport, the original dataset stays unchanged, and never-detected/unscored controls remain unedited. The head preserves the deleted-point flag through final loading. These are provenance checks, not changes to tracking coordinates or a biological finding.

The retained [base result](upstream-1190-base.json) and [head result](upstream-1190-head.json) identify Python 3.13.18, NumPy 2.5.4, pandas 3.1.0, xarray 2026.9.0, pytest 9.2.0, napari 0.9.2 and PyQt6 6.11.0. The cached Linux arm64 CPU-Mesa image is locked by digest in the profile. Both containers had networking disabled, read-only source, two CPUs, a three-GiB memory cap and temporary/output writes only. Base/head runs took 25.590/25.326 seconds; rendered process peak RSS was approximately 895/893 MiB. The three small native files and rendered captures remain local run artifacts with hashes in the reports.

Two harness setup attempts were rejected before a valid comparison: one omitted the Qt fixture plugins, and another requested an unused plugin absent from the cached image. Explicitly loading only required plugins resolved collection without enabling the recording hook. A subsequent log-stream lifetime issue did not change assertions; the runner now keeps logs open through rendering. Both final runs were repeated cleanly after that correction. Existing dependency warnings remain in logs.

### Reproduce the pinned comparison

Prepare new source-only directories; preserve any existing checkout. From the lab root, run the following once for each mode using the corresponding revision in the profile:

```sh
git clone --filter=blob:none --sparse --no-checkout https://github.com/neuroinformatics-unit/movement.git .external/movement-1190-base
git -C .external/movement-1190-base sparse-checkout set movement tests/test_unit/test_napari_plugin tests/fixtures
git -C .external/movement-1190-base checkout --detach 96733f808885300cc3d86b11e2c5189997671b65
git clone --filter=blob:none --sparse --no-checkout https://github.com/neuroinformatics-unit/movement.git .external/movement-1190-head
git -C .external/movement-1190-head sparse-checkout set movement tests/test_unit/test_napari_plugin tests/fixtures
git -C .external/movement-1190-head fetch origin refs/pull/1190/head
git -C .external/movement-1190-head checkout --detach 78e41a2c726ddd4733f9ca46a78034a5a23c8d47
```

In the recorded Linux environment with those dependencies and CPU Mesa/Xvfb available:

```sh
QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1400x1000x24' python projects/movement-edit-filtering/verify_upstream_1190.py --expect base --rendered --output .runs/upstream-1190/base
QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1400x1000x24' python projects/movement-edit-filtering/verify_upstream_1190.py --expect head --rendered --output .runs/upstream-1190/head
```

Output directories must be new. For the cached local image, use its immutable digest with the same network-disabled, read-only, two-CPU/three-GiB settings recorded above, mount the lab at `/lab` and only `.runs/upstream-1190` writable. This comparison is retained local evidence, not a new hosted experiment or an automatically repeated CI scientific job. The webpage verifies source/report hashes before displaying the result.

The contributor reports a broader napari suite run in their PR; our independent assessment covers the 49 selected conversion tests and 15 Kufu cases above. Full-suite compatibility, reset/re-add UI, recordings, researcher benefit, upstream review, merge and release remain unverified here. Follow the draft's changes and rerun against any updated head before relying on these results for that version. No upstream reply or competing PR is authorised by this validation.

## Reproduce the local candidate

Use a fresh Kufu worktree and Python 3.13. The preparation command refuses to overwrite existing task checkouts. Public package installation uses the existing host constraints; no recordings or models are requested.

```sh
python3 site/prepare_movement.py --deletion
python3.13 -m venv .external/movement-deletion-env
.external/movement-deletion-env/bin/python -m pip install --isolated --index-url https://pypi.org/simple -c site/requirements-ci.txt -e '.external/movement-deletion-patched[napari]' pytest pytest-qt pytest-mock
.external/movement-deletion-env/bin/python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-clean --expect baseline --output .runs/deletion/baseline.json
.external/movement-deletion-env/bin/python projects/movement-edit-filtering/verify_deletion.py --checkout .external/movement-deletion-patched --expect patched --output .runs/deletion/patched.json
```

The [runner](verify_deletion.py) checks the imported source path and hashes before execution, asserts the exact baseline failure cases, rejects skipped or errored tests, and requires the patched suite to pass. JSON is sanitised summary evidence; detailed logs and JUnit reports stay in `.runs`. The required CI addition runs both revisions and all 45 existing conversion cases, retaining results for the site. The problem page shows retained output; it does not start Qt or a Vercel experiment.

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
