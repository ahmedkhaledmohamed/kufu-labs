# Native SLEAP pairwise overlap inspector

An experimental, read-only **Analyze → Inspect Pairwise Overlap…** action for SLEAP 1.6.6. It reads the current project's actual instances, skeleton ordering, coordinates and prediction confidence fields. It displays box IoU and both directions of OKS using unchanged released upstream functions. It does not run a prediction model, remove poses or recommend an optimal threshold.

## Problem, source and expected value

[SLEAP #2816](https://github.com/talmolab/sleap/issues/2816) requests a GUI display of IoU/OKS between selected instances because choosing overlap-filter settings requires guessing their similarity. The affected workflow is proofreading overlapping animal-pose predictions. Researchers could use a measurement beside the actual poses to understand a setting before applying it. Time saved, better decisions and biological validity are unmeasured.

The pinned baseline's Analyze menu contains Instance Size Distribution and Label QC, with no pair-inspection action. Source review found the existing canvas-selection and analysis-dialog conventions but no general-purpose plugin registration API for this capability. This implementation is therefore a **small experimental source patch**, not a supported SLEAP plugin or an accepted upstream feature.

## Before, after and recorded demonstration

- [Baseline Analyze menu](before-menu.png): existing analysis actions.
- [Patched Analyze menu](after-menu.png): additional pair-inspection action.
- [Actual host and inspector capture](host-inspector.png): unequal-scale poses with directional OKS.
- [Recorded Qt walkthrough](host-walkthrough.mp4): near duplicate, unequal scale, then disjoint coordinate-bearing nodes.

The recording captures real Qt widgets during automated host interactions, rendered offscreen and composed side by side at 10 frames per second. It is not a recording of a research session. Background images and coordinates are constructed fixtures, not animals, acquired recordings or biological ground truth. The filtering algorithm is unchanged on both sides of the menu comparison.

## Metric scope and science

An instance is a set of body-part coordinates associated with a skeleton. IoU compares their coordinate-derived boxes. OKS compares corresponding node positions with a scale-dependent distance penalty. The released NumPy Labels filter uses **the first instance's box area** and κ = 0.1. Thus OKS(A → B) can differ from OKS(B → A): the unequal-scale fixture measures approximately **0.7335 versus 0.4335**.

This adapter calls the actual [sleap-nn 0.3.4 NumPy implementation](https://github.com/talmolab/sleap-nn/blob/v0.3.4/sleap_nn/inference/ops/filters.py), used by the released legacy Labels filtering route. It does not claim to represent every inference path. The separate browser demonstration uses another pinned tensor revision and can have different direction semantics. Check the backend of the intended inference workflow before interpreting either tool's scores.

Skeleton identity must match; this prevents silently comparing reordered body parts. Missing coordinates remain missing. All-missing and zero-area inputs are identified, rather than interpreting zero similarity as proof of different animals. Manual annotations receive no invented prediction confidence. Stored node confidences are displayed but do not weight these upstream overlap functions. A pair score alone does not determine a full frame's greedy suppression result.

## Install and run locally

Verified on macOS arm64, Python 3.13.2, SLEAP 1.6.6 at `d24a98fbc2f69d84c6c080bab4e826c4992ac76f`, sleap-io 0.9.3, sleap-nn 0.3.4 and PySide6 6.12.0. Prerequisites are Git, Python 3.13 and uv; the verification used uv 0.13.6. The [environment snapshot](requirements-macos-arm64.txt) records resolved versions for this platform; it is not a cross-platform lock.

From the Kufu repository root:

```sh
python3 projects/overlap-inspector/sleap-adapter/prepare_host.py
uv venv --python 3.13 .external/sleap-env
uv pip install --python .external/sleap-env/bin/python --index-url https://pypi.org/simple -r projects/overlap-inspector/sleap-adapter/requirements-macos-arm64.txt
uv pip install --python .external/sleap-env/bin/python --index-url https://pypi.org/simple --no-deps -e .external/sleap-host/patched
uv run --no-project --python .external/sleap-env/bin/python python projects/overlap-inspector/sleap-adapter/verify_host.py --output .runs/sleap-host
uv run --no-project --python .external/sleap-env/bin/python sleap-label --no-usage-data .runs/sleap-host/constructed.pkg.slp
```

The preparation script refuses existing destinations and verifies adapter hashes from [source-lock.json](source-lock.json). Sparse source checkouts exclude upstream test recordings and model assets. Installing the full upstream dependency set is substantial: the verified environment occupied about 3.1 GiB. No weights are fetched or models executed by these commands.

Open Analyze → Inspect Pairwise Overlap. Select A/B from the frame's stored instances, or select a pose on the host canvas and press **Use canvas selection as A/B**. The dialog follows navigation and coordinate changes; hidden instances can still be selected from its complete stored-instance list. Closing it stops its refresh timer. To compare the untouched host, set `PYTHONPATH=.external/sleap-host/baseline` on the verification command and add `--baseline`, using a separate output directory.

The inspector executes in your local SLEAP process. Opening Kufu's website, viewing the recording or running the existing Vercel NWB experiment does not launch this Qt application.

## Verification and remaining limits

[Baseline results](baseline-results.json) and [patched host results](host-results.json) record the actual host revision, dependency versions, observed menus and assertions. The harness opens a generated embedded `.slp` through MainWindow's project-loading path. It exercises the native action, canvas-selection buttons, frame navigation, directional OKS, missing/zero-area inputs, incompatible/reordered skeleton rejection, manual annotation labeling and stale-result clearing. Eighteen full native Labels-filter calls check equality and adjacent representable suppression boundaries. Coordinates, visibility/completion/confidence fields, skeleton/provenance identities, source-file bytes and the unsaved-change flag remain unchanged.

The harness redirects only preferences to its output directory and disables usage reporting. Host widgets, pose I/O and numerical functions are real. Source preparation was repeated in a fresh checkout and that prepared host passed the same checks. Ruff checks pass for the adapter, preparation/harness scripts and changed upstream Python. The broad upstream test suite was not run because its recordings/model fixtures are outside this experiment's scope. Native on-screen interaction, other operating systems, other backend versions, large-project performance, researcher decisions and upstream acceptance remain unverified. This native replay is not yet a required cloud CI job.

The fresh-checkout host replay took 9.396 seconds after imports and reported a 648,478,720-byte peak resident set for its process on macOS (about 618 MiB). This includes widget recording; it is not a large-project performance benchmark.

The adapter loads the verified pure NumPy module directly from the installed distribution, avoiding inference package initializers; it neither rewrites package namespaces nor ports the numerical functions. Its helpers are private APIs, so version 0.3.4 and the exact source hash are mandatory. Different or modified backends fail closed with an unavailable message.

Next: review the local demonstration and exact implementation diff. Additional backend support needs its own source and numerical checks. No outreach is planned; exact-diff approval is required before publishing a Kufu PR, and merging requires a separate instruction.

## Licensing

Adapter/harness/preparation source is GPL-3.0-only; retain [COPYING](../COPYING). The upstream SLEAP patch context retains the [Clear BSD licence](UPSTREAM-SLEAP-LICENSE). The installed sleap-nn 0.3.4 metadata says BSD-3-Clause, while its distributed LICENSE contains GPLv3; this experiment preserves the GPL terms rather than relying on the metadata label. No upstream source implementation, recordings, model weights or environment directories are redistributed here.
