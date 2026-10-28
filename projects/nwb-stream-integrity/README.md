# NWB stream integrity during inspection

Status: local patch and constructed-data replay. No upstream PR, researcher validation or real-recording evaluation. The [implementation and learning plan](../../research/opportunity-discovery/NEUROINFORMATICS-PLAN.md) explains the next milestones.

## Reported problem and beneficiary

[NWB Inspector #771](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771) reports that inspecting an in-memory NWB file before writing can consume buffered data. The subsequent writer saves without raising a write error, but part of the dataset becomes zeros. Researchers and engineers converting streamed neurophysiology recordings could therefore save altered data while performing an apparently observational step.

The report describes affected conversions; it does not measure how common the problem is. Our local baseline also returns Inspector ERROR messages while still allowing the damaged data to be saved. We do not describe this observed local path as inspection passing silently.

## Local before and after

The replay calls the actual Inspector, then writes and reads a real HDF5 or Zarr NWB file. It uses positive constructed int16 arrays with two channels at 100 Hz. These are software fixtures, not measured neural signals or a biological simulation. No recordings, subjects or model weights are involved.

| Input rows | Baseline rows replaced by zeros after inspection | Patched rows replaced by zeros after inspection |
| --- | --- | --- |
| 50 | 50 | 0 |
| 100 | 100 | 0 |
| 500 | 300 | 0 |

Each row above holds for both HDF5 and Zarr, using both `DataChunkIterator` and a constructed `GenericDataChunkIterator` subclass. There are 12 inspected cases per revision and 12 uninspected controls per revision. All controls preserve every value. The patched inspected cases preserve every value, with no Inspector ERROR messages. Non-error metadata recommendations can still appear.

The [baseline results](baseline.json) and [patched results](patched.json) retain full-array hashes, zero-row counts, dependency versions and runtime. Zarr emitted its warning that consolidated metadata is not yet part of the Zarr v3 specification; this is not a claim of compatibility with every Zarr implementation.

## Implementation and integration

Upstream baseline: [NWB Inspector e6d968a](https://github.com/NeurodataWithoutBorders/nwbinspector/tree/e6d968a1e0a62aa8f6611f45f242196d9ce75ea5), package version 0.7.3. The local [patch](non-consuming-shape.patch) modifies the existing shape helper and adds regression tests in that project. It reads declared shape metadata from HDMF chunk iterators and their `DataIO` wrappers without advancing them. Unknown single-pass iterators return an unknown shape; stored resizable datasets retain their actual current shape rather than their maximum capacity.

The supported integration is the existing `inspect_nwbfile_object` conversion workflow. No new application, plugin or monkey patch is required. [Issue #760](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/760) proposes reusing HDMF's helper; [HDMF PR #1606](https://github.com/hdmf-dev/hdmf/pull/1606) proposes a related wrapper fix and was open when checked. Those alternatives may supersede this patch and require comparison before an upstream proposal.

## Run the actual workflow

From the lab root, with Git and Python 3.13 available:

```sh
lab_root=$PWD
nwb_task_dir=$(mktemp -d)
git clone --bare --filter=blob:none https://github.com/NeurodataWithoutBorders/nwbinspector.git "$nwb_task_dir/source.git"
git -C "$nwb_task_dir/source.git" worktree add --detach "$nwb_task_dir/baseline" e6d968a1e0a62aa8f6611f45f242196d9ce75ea5
git -C "$nwb_task_dir/source.git" worktree add -b kufu-stream-preservation "$nwb_task_dir/patched" e6d968a1e0a62aa8f6611f45f242196d9ce75ea5
python3.13 -m venv "$nwb_task_dir/env"
"$nwb_task_dir/env/bin/python" -m pip install --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements.txt
"$nwb_task_dir/env/bin/python" -m pip install --index-url https://pypi.org/simple --no-deps -e "$nwb_task_dir/patched"
PYTHONPATH="$nwb_task_dir/baseline/src" "$nwb_task_dir/env/bin/python" projects/nwb-stream-integrity/verify.py --expect baseline --output "$nwb_task_dir/baseline.json"
git -C "$nwb_task_dir/patched" apply "$lab_root/projects/nwb-stream-integrity/non-consuming-shape.patch"
"$nwb_task_dir/env/bin/python" projects/nwb-stream-integrity/verify.py --expect patched --output "$nwb_task_dir/patched.json"
```

The [runner](verify.py) rejects a different upstream Git revision. It records the loaded utility source hash and the patch digest. Its assertions compare all array values, check the uninspected controls and require the patched inspection to avoid ERROR messages. Temporary NWB files are removed after each case. The JSON output remains in the chosen output location. The website displays retained results; it does not execute Python or process uploaded files.

## Verification and limits

The replay passed locally on Python 3.13.2 with PyNWB 4.2.0, HDMF 6.2.0, HDMF-Zarr 0.14.0, h5py 3.16.0, Zarr 3.4.2 and NumPy 2.5.4. The [requirements](requirements.txt) retain the public package versions from this environment; no local editable paths are included. The exact Inspector source is installed separately.

The focused upstream run passed 61 tests: the 13 new stream/shape cases and 48 existing time-series checks. Ruff and Black passed on the two changed upstream files. This includes checking that an existing resizable HDF5 dataset reports its current shape, and that existing time-series validation still detects its tested failures. Broader unit regression results and final patch reapplication are recorded in [verification](verification.json).

The initial scope does not cover real recordings, every NWB extension or iterator implementation, all dependency versions, performance at recording scale, upstream acceptance or researcher benefit. Shape metadata itself may be incorrect. Preserving values does not prove acquisition quality or scientific validity. The new NWB replay is not yet a required CI execution check in the lab pipeline; that is the next engineering milestone.

## Science to understand alongside this patch

A time series is a sequence of measurements indexed by time. Here a row holds two constructed channel values and 100 Hz means 100 samples per second. In a real recording, channel meaning and units depend on the measurement method: spikes, local field potentials and EEG are different representations and cannot be treated interchangeably.

NWB organises measurements and associated metadata so they can be stored and reused. Chunk iterators allow conversion without loading an entire recording into memory. Advancing a single-pass iterator changes what the next consumer receives. An inspection step should preserve the stream for the writer. That is the specific software invariant tested here, not a new neuroscience finding.

## Publication and licence

The patch is retained locally for review. The upstream [developer guide](https://github.com/NeurodataWithoutBorders/nwbinspector/blob/e6d968a1e0a62aa8f6611f45f242196d9ce75ea5/docs/developer_guide.rst) asks contributors not to open a PR before the issue is approved by its team. No approval, maintainer discussion, fork push or upstream PR is claimed. Outreach remains deferred.

Retain the [upstream licence](UPSTREAM-LICENSE), including its enhancement clause, with the patch. The lab's original replay and documentation use the repository default MIT terms. The next step is to compare dependency alternatives, complete review, and add a pinned CI replay before considering an upstream proposal.
