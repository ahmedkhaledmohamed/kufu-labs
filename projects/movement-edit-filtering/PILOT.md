# Pilot proposal: use manual-edit provenance in movement filtering

Prepared 26 October 2026. Status: local implementation approved and technical pilot completed; publication and external review remain pending. Evidence and rejected alternatives are in the [comparative audit](../../research/opportunity-discovery/AUDIT.md).

## Beneficiary and task

A behavioural researcher has proofread pose tracks in movement's napari interface and wants to discard unscored predictions while retaining explicitly corrected coordinates. movement already records `edited` flags, but its confidence filter cannot consume them. [Issue #1027](https://github.com/neuroinformatics-unit/movement/issues/1027) requests this separation; the existing NaN-confidence policy was introduced as a partial solution in [PR #1037](https://github.com/neuroinformatics-unit/movement/pull/1037).

The contribution would be an optional provenance input to the existing Python filter. The present workaround is a caller-written mask or keeping all missing-confidence points. There is no claim that all researchers encounter this problem, that manual edits are correct, or that maintainers have accepted this design.

## Baseline and smallest change

Use movement main revision `39ee15e29706150d7d4f60ba617aa99d2027eed7` as the inspected baseline, then refresh upstream status before implementation. Record any newer baseline and repeat the source comparison if it changes.

At this revision, `filter_by_confidence` keeps points meeting a numeric threshold and optionally keeps every point with NaN confidence. Existing napari editing supplies a separate boolean `edited` array but also replaces a moved point's confidence with NaN. This proposal consumes the flag; it does not redesign editing, restore a previous model confidence, or change what the current confidence value means after a correction.

Proposed API direction: add an optional keyword-only edit-provenance argument to `filter_by_confidence`, using the Dataset's existing `edited` field. Naming and exact validation should follow upstream review. With a supplied mask, explicitly edited points may survive the confidence criterion even when NaN-confidence retention is disabled. Without it, outputs and defaults stay identical to the baseline. A missing score alone never becomes an edit flag.

The minimal distinguishing example uses two finite positions with NaN scores: one explicitly edited, one unedited. Current settings retain both or drop both. The proposed explicit policy retains the edited position and drops the unedited one. That distinguishing behaviour was reproduced in the approved pilot described below.

## Integration and data contract

The host remains movement in a Python script or Jupyter notebook. Researchers can proofread using the existing napari plugin, save native netCDF, reload the Dataset, and pass its position, confidence, and edit arrays to the filter. No extra GUI, hosted backend, model, or editor extension is required.

Use one constructed pose Dataset with time/space/keypoint/individual coordinates, including two individuals and at least two keypoints. Confidence and edit flags share the non-space dimensions. Input masks must be boolean with matching named coordinates; reject missing, duplicate, or incompatible coordinates rather than silently aligning the wrong animal or frame. Support for reordered but otherwise identical coordinates is a design choice to resolve explicitly; rejecting them is acceptable for this pilot. Do not interpret NaN or absent edit flags as proof of manual review.

Filtering returns the same kind of DataArray as today and changes only which values become missing. It must not mutate confidence, position, timestamps, or edit provenance in the inputs. Keeping an edited point must not recreate a deliberately removed position. This is confidence filtering only: a manual flag does not exempt a point from future kinematic or biological checks.

Constructed data require no external recording download or licence clearance. Any fixture contributed upstream should follow movement's BSD-3-Clause conventions. Use its native netCDF path for the round-trip check. Do not assume that DLC, SLEAP, NWB, or every export format preserves this field; that interoperability is outside this proposal.

## Acceptance criteria

| Case | Required observation |
| --- | --- |
| No edit argument | Existing tests and defaults retain baseline behaviour |
| Edited and unedited finite positions both have NaN confidence; NaN retention disabled | Edited position retained; unedited position dropped |
| Edited finite position has a below-threshold numeric confidence | Explicit manual policy retains it |
| Unedited numeric scores | Threshold behaviour unchanged, including the boundary |
| Edited position is already missing | Remains missing; filtering never reconstructs it |
| Multiple frames, keypoints, and individuals | Changes occur only at the intended labelled coordinates |
| Incompatible or non-boolean edit mask | Clear error; no silent coordinate reassignment |
| Native save/reload followed by filtering | Supported positions and edit flags yield the same filtering decisions |
| Input integrity | Position, confidence, coordinates, and edit mask unchanged in source arrays |

All acceptance cases must pass. Preserve existing regression tests, add targeted cases that distinguish the policies, and follow the host's required checks. Record the exact command, dependency versions, baseline revision, and output. Synthetic correctness is the first outcome measure; researcher time saved, adoption, and downstream scientific accuracy remain unmeasured and must not be invented.

## Approved bounded execution plan

1. Refresh #1027, relevant PRs, and main. Read the selected repository instructions; use a separate implementation worktree. Stop if equivalent work has landed or is already being implemented.
2. Reproduce the two-point baseline and inspect current validation/decorator conventions. Use a supported Python 3.12+ environment and ordinary public package sources. Confirm installation/resource feasibility before changing the library.
3. Implement only the optional filter input, required validation, targeted tests, and a short usage example in the host's existing documentation. Avoid loaders, new GUI controls, and dataset-schema expansion.
4. Run targeted tests and required formatting/type checks. Check native netCDF round-trip without downloading recording data. Record measured resource use and any environment limitations.
5. Prepare a small reviewable diff and an evidence-based result. Maintainer feedback requires separately authorised outreach; an upstream PR follows the applicable identity, thinking-trail, full-diff approval, and publication rules.

Proposed effort cap: three focused sessions, about 12 hours total. Proposed local limits: no paid services, no GPU, no model downloads, synthetic artifacts below 1 MB, environment and working files below 5 GB, and peak process memory below 4 GB. These are stop limits rather than claims about measured requirements. If the supported host environment or required checks exceed them, report the constraint before expanding the pilot. No local hardware capability has been benchmarked.

## Review, maintenance, and stop conditions

A movement maintainer should assess the API, coordinate rules, compatibility, and whether this addresses a useful part of #1027. A behavioural researcher is needed before claiming workflow benefit or downstream scientific value. No reviewer has agreed to participate. The first artifact can be a technical proposal and reproducible synthetic comparison without claiming user validation.

An upstream function option avoids maintaining a separate plugin distribution. The expected maintenance is a small public API, mask validation, a usage example, and regression coverage. This is still an obligation; it is justified only if the project wants the behaviour.

Stop or revise if the gap is already covered, the actual baseline supports the distinction, maintainers prefer an existing caller-side idiom, explicit edit provenance is unavailable in the intended workflow, coordinate semantics cannot be made unambiguous, or the work expands into source-format migration. The fallback is a documented negative result or minimal recipe if upstream considers that sufficient, not a standalone application.

## Technical pilot result: 26 October 2026

The approved local pilot is complete on branch `feat/explicit-edit-filtering`, using the same baseline revision as the audit. The [full implementation patch](movement-pilot.patch) contains only `movement/filtering.py` and a new synthetic test module. No fork, commit, push, upstream PR, or maintainer message has been created.

- Reproduced baseline: two finite positions with NaN confidence are both retained with the legacy default and both dropped when NaN retention is disabled.
- Confirmed the new distinguishing tests fail on baseline because the `edited` argument is absent, then pass after implementation.
- Implemented an optional keyword-only `edited` argument, exact labelled-coordinate validation, and a usage example in the existing function docstring. Confidence values, edit provenance, and input coordinates are unchanged.
- All 15 new acceptance cases and 82 existing synthetic filtering cases passed: **97 passed, 2 deselected in 20.55 seconds**. The deselected tests use an external SLEAP recording. The full repository suite and napari GUI interactions were not run.
- Ruff lint/formatting and codespell checks passed using the repository-pinned versions, Ruff 0.16.10 and codespell 2.4.3. Targeted mypy 2.4.0 reported no issues. The full pinned upstream pre-commit pipeline subsequently passed on both changed files, including manifest validation, mypy, spelling, and formatting. Checks without matching files were skipped normally.
- Native movement save → xarray reload → filtering preserved the constructed Dataset and decisions. The file was 11,362 bytes.
- A separate synthetic filter/round-trip process took 2.392 seconds and reached 268,320,768 bytes peak RSS on macOS with Python 3.13.2. This measures that process, not the whole test run or a real recording. The isolated environment occupied approximately 1 GB. All measured values were within the proposed caps.

The [environment record](movement-pilot-environment.json) records package versions and the small-process measurements. It is an inventory of the tested environment, not a portable dependency lock or performance claim for other machines.

To reproduce the targeted test selection from the implementation checkout, activate an environment containing movement's declared dependencies plus pytest, pytest-cov, pytest-mock, Ruff, mypy, pandas-stubs, and scipy-stubs. Then run:

```python
from pathlib import Path
from tempfile import gettempdir
from unittest.mock import patch

# Keep movement's import-time log in a disposable directory.
with patch.object(Path, "home", return_value=Path(gettempdir()) / "movement-pilot-state"):
    import movement

import pytest

raise SystemExit(pytest.main([
    "--noconftest", "-o", "addopts=",
    "-p", "tests.fixtures.datasets", "-p", "tests.fixtures.helpers",
    "tests/test_unit/test_filtering.py",
    "tests/test_unit/test_filtering_edited.py",
    "-k", "not proofread_data", "-q", "--tb=short",
]))
```

`--noconftest` deliberately excludes the upstream startup hook that downloads all sample recordings. The existing synthetic fixture modules are explicitly registered instead. No filtering or IO functions are mocked. NWB dependencies may create their ordinary local cache on first import.

Checks from the implementation checkout:

```sh
ruff check movement/filtering.py tests/test_unit/test_filtering_edited.py
ruff format --check movement/filtering.py tests/test_unit/test_filtering_edited.py
mypy movement/filtering.py --follow-imports=silent
codespell movement/filtering.py tests/test_unit/test_filtering_edited.py
git diff --check
```

## Subsequent widget-workflow verification

The unchanged patch has now been replayed in a fresh pinned worktree through real Qt loader/saver buttons and napari data callbacks, without a canvas. All 11 demonstration invariants passed, and four existing synthetic conversion cases passed. The [review package](REVIEW.md), [verifier](verify_workflow.py), and [result](workflow-result.json) record commands, versions, measured resource use, and remaining limits.

A deleted point's edit flag changes from true to false after loading the first saved file and exporting again through the unchanged upstream conversion code. Its position stays missing and filtering decisions remain equal. Moved finite-point provenance survives. This is a separate lifecycle limitation, not a reason to claim complete provenance preservation or expand the filtering patch silently.

## Next decision

Review the complete local change before any commit or publication. If accepted, prepare the contribution record and exact-commit approval required by the personal Git workflow, then arrange separately authorised upstream review. Maintainer acceptance, real-workflow benefit, full host CI, and GUI verification remain unestablished. This pilot supports a small technical contribution; it does not establish a scientific finding.
