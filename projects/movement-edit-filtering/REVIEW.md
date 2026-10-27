# movement filtering contribution review package

Status: local technical verification complete; ready for maintainer design review, not a claim of merge readiness. The approved [public design question](https://github.com/neuroinformatics-unit/movement/issues/1027#issuecomment-6431299925) has been posted; no upstream fork, patch push, or PR has been created. The approved patch is unchanged. Publication requires its applicable full-diff and exact-commit approval.

## Task, baseline, and scope

[Issue #1027](https://github.com/neuroinformatics-unit/movement/issues/1027) requests separating manual-edit status from confidence and using it in filtering. Refreshed on 27 October 2026 UTC: it remains open; main is `39ee15e29706150d7d4f60ba617aa99d2027eed7`. PR searches for confidence/edit provenance found the existing edit, reset, save, and timeline work, with no matching filter implementation. Search cannot exclude unpublished or differently described work; refresh before submitting.

movement already generates `edited` flags in napari. The existing filter can retain all NaN-confidence points or drop all of them; it cannot distinguish explicit human corrections from other unscored predictions. This patch adds a keyword-only boolean `edited` input, preserves legacy filtering values when omitted, and rejects ambiguous labelled coordinates when supplied.

The patch addresses the filtering part of #1027. It does not preserve historical model scores, modify source loaders, redesign the GUI, or establish that human edits are biologically correct. Use `Related to #1027`, rather than closing the whole issue.

## Verified workflow

The [executable demonstration](verify_workflow.py) creates four frames, two keypoints, and two individuals. It loads a constructed native dataset through movement's actual Qt load button, changes a point through the connected napari data event, removes another point, invokes the real Qt saver, reloads through the loader, and reexports. Only the save-file picker and import-time log destination are patched; editing callbacks, conversion, IO, and filtering are real.

| Confidence policy | Corrected finite point, NaN score | Unedited finite point, NaN score |
| --- | --- | --- |
| Existing default | Retained | Retained |
| Existing policy with NaN retention disabled | Dropped | Dropped |
| Explicit edit mask, NaN retention disabled | Retained | Dropped |

Removed and originally missing positions stay missing in every relevant result. Corrected x/y values, physical time coordinates, and input datasets are checked. A moved point's flag survives loading the saved dataset, and filtering decisions survive a second GUI export. The verifier checks the pinned commit, imported source location, and exact approved patch before running, preventing accidental use of a different editable checkout.

Execution uses `ViewerModel` and real QWidget buttons/events with Qt's offscreen backend. No canvas is created. This verifies the plugin's programmatic data path, not mouse gestures, visual rendering, video synchronisation, or researcher usability.

## Observed upstream limitation

A deleted point is marked `edited=True` on the first GUI export but becomes `edited=False` on a second export after reload. Its position remains NaN, and the demonstrated filtering decisions remain equal. Moved finite points retain their edit flags.

This occurs in the unchanged [conversion code](https://github.com/neuroinformatics-unit/movement/blob/39ee15e29706150d7d4f60ba617aa99d2027eed7/movement/napari/convert.py): absent live rows get a false edit value, while removal detection compares against positions present at the start of the current session. A previously removed point was already missing when reloaded. The result records both flags explicitly rather than asserting full provenance preservation.

Do not broaden the filter patch to repair this lifecycle behaviour without a separate scope decision. Ask maintainers whether they want it tracked separately. The flag loss limits provenance auditing of deletions; the filter does not recreate removed coordinates.

## Reproduce from the pinned source

Use Python 3.13 and a local lab checkout containing these unpublished verification artifacts. The commands below use placeholders rather than a particular machine's paths. Cloning and package installation require network access; the verifier itself needs no research data download or service.

```sh
LAB_REPO=/path/to/scientific-software-lab
REPLAY_ROOT=/path/to/local-movement-replay
mkdir -p "$REPLAY_ROOT"
git clone --bare https://github.com/neuroinformatics-unit/movement.git "$REPLAY_ROOT/upstream.git"
git --git-dir="$REPLAY_ROOT/upstream.git" worktree add -b verification/edited-filter "$REPLAY_ROOT/source" 39ee15e29706150d7d4f60ba617aa99d2027eed7
git -C "$REPLAY_ROOT/source" apply "$LAB_REPO/projects/movement-edit-filtering/movement-pilot.patch"
python3.13 -m venv "$REPLAY_ROOT/env"
"$REPLAY_ROOT/env/bin/python" -m pip --isolated install --index-url https://pypi.org/simple -e "$REPLAY_ROOT/source[napari]" napari==0.9.2 PyQt6==6.11.0 PyQt6-Qt6==6.11.2
QT_QPA_PLATFORM=offscreen QT_API=pyqt6 "$REPLAY_ROOT/env/bin/python" "$LAB_REPO/projects/movement-edit-filtering/verify_workflow.py" --checkout "$REPLAY_ROOT/source" --output "$REPLAY_ROOT/workflow-result.json"
```

The [result](workflow-result.json) records the complete observed package inventory. These commands pin the host source and tested GUI stack; the full inventory is evidence, not a cross-platform lockfile. The fresh-worktree replay reused the existing isolated environment, selected the fresh source explicitly, and verified the patch bytes before imports. It did not repeat the entire dependency installation in a second environment.

napari writes its ordinary icon/theme cache even during offscreen use. A filesystem sandbox denying that cache produced a permission error; allowing those local cache writes resolved it. No source change or weakened assertion was needed. No interactive display, GPU context, recording, or model weights were used by the demonstration.

## Verification evidence and limits

- Existing approved result: 15 new acceptance cases and 82 synthetic filtering regressions passed; the exact patch is unchanged, so those checks were reused.
- Existing full pinned pre-commit pipeline passed for both upstream changed files, including mypy, formatting, manifest, and spelling checks.
- New fresh-worktree demonstration passed all 11 recorded invariants in 4.747 seconds, with 409,010,176 bytes peak RSS and 33,263 bytes of generated netCDF across three files. The measured local working set, including dependencies, hook caches, task source/worktrees, and napari cache, was 1.951 GiB, below the 5 GiB cap. See the result JSON for the process measurements and exact versions.
- The four existing synthetic pose-conversion round-trip cases were selected for checking the added GUI dependency environment; **4 passed, 41 deselected in 3.04 seconds**. These emitted 20 upstream Pydantic/pandas deprecation warnings; no failure was suppressed.
- New verifier lint, formatting, and spelling are checked against the host's conventions. No visual canvas or full host suite was run. Installing napari and Qt did not change the NumPy, xarray, or SciPy versions used by the earlier filtering run. The normal suite downloads research recordings at startup, outside this goal's constructed-data scope; the two recording-dependent filtering cases remain unrun.
- No maintainer or scientist has reviewed this proposal. No time-saving, adoption, scientific finding, clinical outcome, or user benefit has been measured.

The added conversion selection can be reproduced from the host worktree after installing pytest, pytest-qt, and pytest-mock in the same environment:

```sh
QT_QPA_PLATFORM=offscreen QT_API=pyqt6 python -m pytest --noconftest -o addopts= -p tests.fixtures.datasets tests/test_unit/test_napari_plugin/test_convert.py -k test_valid_poses_roundtrip_napari_layer_to_dataset -q
```

This bypasses the recording-download startup hook, not the selected conversion implementation or assertions. The normal user cache/log locations must be writable. Ruff 0.16.10 lint/format and codespell 2.4.3 passed for the verifier using the host's existing configuration.

## Upstream PR draft

**Title:** Use explicit edit flags during confidence filtering

After proofreading pose tracks in napari, callers may want to retain explicit corrections while dropping other predictions with missing confidence. Today `filter_by_confidence` can only keep or drop all NaN-confidence points. This adds an optional keyword-only `edited` array so the existing Dataset field can express that distinction.

Omitting the argument preserves the existing filtering policy and positional arguments. Supplying it requires boolean values and matching unique labelled coordinates; ambiguous alignment raises an error. Existing missing positions remain missing. A manual flag records provenance rather than biological correctness.

Related to #1027; this implements only its filtering portion. Source loaders, original model-score retention, and GUI editing are unchanged. A separate existing deletion-provenance issue was observed during two-session export and is described in the verification notes.

Validation: 97 targeted synthetic filtering cases previously passed, along with the pinned pre-commit pipeline. A fresh-worktree Qt-widget/model-event demonstration verifies loading, correction/removal, saving, reload, and the policy distinction without a canvas or external recordings. Full suite, visual interaction, and real-recording checks remain pending.

## Maintainer questions and next gate

1. Is `edited` the preferred optional argument name, matching the Dataset variable, and is always retaining explicitly edited coordinates the desired semantics?
2. Should masks with reordered but equivalent indexes be rejected as proposed, or explicitly realigned? Is the requirement for explicit unique labels appropriate for this API?
3. Is this bounded filtering contribution useful independently of loader provenance and historical-confidence changes in #1027?
4. Should loss of deleted-point flags on reexport be tracked separately, and which host CI/GUI checks would be required before merge?

Prepare external review only after the local diff/contribution record is approved. Do not submit, message maintainers, or merge under this autonomous goal. A reasonable next outcome is an upstream design review, not a new standalone tracking application.
