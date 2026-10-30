# movement edit-aware filtering

Use movement's existing boolean `edited` provenance to retain explicitly corrected pose points during confidence filtering, while allowing other unscored predictions to be dropped.

- [Current review package and upstream draft](REVIEW.md)
- [Independent deletion-provenance diagnostic and issue draft](DELETION-PROVENANCE.md) (local; no fix or new issue submitted)
- [Executable widget-workflow demonstration](verify_workflow.py) and [observed result](workflow-result.json)
- [Rendered canvas result](rendered-result.json): [before editing](canvas-before.png), [after the mouse drag](canvas-after-drag.png), and [filtered data reloaded](canvas-after-filter.png)
- [Scope, implementation result, and reproduction commands](PILOT.md)
- [Complete implementation patch](movement-pilot.patch)
- [Environment and resource measurements](movement-pilot-environment.json)
- [Evidence and rejected alternatives](../../research/opportunity-discovery/AUDIT.md)
- [Upstream BSD-3-Clause licence](UPSTREAM-LICENSE)

## Source and result

Upstream: [neuroinformatics-unit/movement](https://github.com/neuroinformatics-unit/movement), revision `39ee15e29706150d7d4f60ba617aa99d2027eed7`. The patch changes only `movement/filtering.py` and adds `tests/test_unit/test_filtering_edited.py`. Implementation branch: `feat/explicit-edit-filtering`, maintained in a separate upstream worktree.

97 targeted tests passed: 15 new acceptance cases and 82 existing synthetic filtering cases. Native save/reload, lint, formatting, spelling, and targeted type checks passed. The real Qt loader/saver and napari edit callbacks pass a constructed-data demonstration in a fresh pinned worktree; four existing synthetic conversion cases also pass. The full pinned pre-commit pipeline has also passed on both changed files, including manifest validation. A rendered napari canvas replay now verifies an actual Qt pointer drag and the saved, filtered and reloaded result. The two SLEAP recording-dependent cases, full repository suite and researcher validation remain unrun.

## Rendered host workflow

The [rendered result](rendered-result.json) comes from the actual pinned movement plugin in napari 0.9.2, PyQt6 6.11.0 and CPU Mesa rendering (`llvmpipe`). It uses four constructed frames, two individuals and two keypoints at 30 frames per second. The points are software fixtures, not measured animal movements or a biologically plausible correction.

The harness selects the intended nose point on the canvas and sends a Qt drag from `(43, 47)` to `(100, 200)` in x/y coordinates. Movement's unchanged callback marks that correction as edited and sets its confidence to NaN. The actual Save button writes a netCDF file; only its file picker is replaced with a deterministic destination. Reloading preserves the correction. The unchanged approved filtering patch is then called through Python and its result is saved and opened again in the real host. Assertions check that the intended frame is visible, the corrected point is rendered, and the unscored, unedited point is absent. The view uses napari's native light theme for readable captures.

NaN marks an unavailable confidence value; by itself it cannot distinguish a manual correction from an unscored prediction.

| Point with NaN confidence | Existing keep-NaN policy | Existing drop-NaN policy | Explicit edit-aware policy |
| --- | --- | --- | --- |
| Manually corrected nose | Retained | Removed | Retained |
| Unedited, unscored prediction | Retained | Removed | Removed |

The local rendered replay passed all 11 existing workflow invariants plus actual canvas selection/movement and visible reload checks. It took 8.192 seconds with a Python-process peak RSS of 888,881,152 bytes (about 848 MiB) on Linux arm64/Python 3.13.18. The run had no network access, no GPU, a three-GiB container memory limit and two CPUs. Its four netCDF files total less than 50 KB; the runner also enforces the original one-MB fixture and four-GiB process caps. These are constructed-run measurements, not recording-scale benchmarks.

The deletion case still uses napari’s existing model removal method; only the correction is dragged through the canvas. The known deletion-provenance counterexample remains: a deleted point's edit flag is true after the first export and false after the second. A [separate local repair and regression comparison](DELETION-PROVENANCE.md) now address that defect on current upstream; they are not applied in this filtering-only replay. Positions remain missing and the tested filtering decisions remain equal. This replay does not fix that defect, implement the whole dedicated-array request in #1027, add a GUI filtering button, or establish researcher benefit. The website serves retained results and captures; the Qt application runs in a local or CI environment.

### Reproduce on Linux

Use a fresh Kufu checkout and a Python 3.13 environment. Source preparation refuses existing checkouts and excludes upstream recordings. Install movement's declared napari dependencies using the lab's numerical/GUI constraints and public PyPI:

```sh
python site/prepare_movement.py
python -m pip install --index-url https://pypi.org/simple -c site/requirements-ci.txt -e '.external/movement-patched[napari]'
sudo apt-get update -qq
sudo apt-get install -y xvfb xauth libegl1 libopengl0 libgl1-mesa-dri libglx-mesa0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1400x1000x24' python projects/movement-edit-filtering/verify_workflow.py --checkout .external/movement-patched --output .runs/rendered/result.json --rendered
```

Three actual host screenshots are written under `.runs/rendered/canvas/`. A non-software renderer, missed click, unchanged point, unexpected visible frame, lost correction or retained unknown prediction fails the replay. The pointer-move event explicitly carries the held left button because `QTest.mouseMove` did not reliably preserve it under Xvfb; no movement model event or coordinate mutation substitutes for the rendered drag.

The replay now runs in the existing required scientific-contract job, which retains its captures/results and packages those fresh CI outputs into the site. [Merged-main run 40990877466](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40990877466) passed all four jobs and promoted the tested site to protected production. Independent authenticated reads matched the manifest and seven sampled movement/page assets; the deployment gate also completed its actual queued NWB experiment with compute stopped. Tests that require recordings or model weights remain outside this replay.

## Continue locally

Apply the patch to the pinned upstream revision in an isolated feature worktree; follow the upstream contribution instructions and the pilot's environment/setup commands. Do not execute a fresh remote main in place of the recorded baseline without refreshing the comparison.

Keep the upstream source tree, virtual environment, caches, and generated data outside this repository. The lab stores the contribution and its evidence, not a separately maintained fork of the whole toolbox. Retain the upstream licence with this artifact.

The unchanged implementation diff was approved for continuation. The local review package documents a separate upstream limitation: deleted-point flags are lost on a second GUI export, although positions remain missing and filtering decisions are unchanged. The explicitly approved [design question](https://github.com/neuroinformatics-unit/movement/issues/1027#issuecomment-6431299925) has now been posted. No public fork, patch push, or upstream PR has been created. Further publication follows the full-diff, contribution-record, and exact-commit approval process; inspect maintainer feedback before expanding the implementation.
