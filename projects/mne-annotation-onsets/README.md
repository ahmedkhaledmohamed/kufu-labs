# Preserve interior annotation onset precision

Status: local MNE-Python candidate for a bounded part of [issue #12327](https://github.com/mne-tools/mne-python/issues/12327). No upstream submission or researcher validation; no MNE changelog fragment or submission text is prepared. This is about software timestamps, not a physical clock or the biological validity of EEG data.

## Problem and beneficiary

An EEG/MEG researcher can create an annotation at a sample's exact time, then attach it to a Raw object. The crop operation used internally converts that time through Python datetime, whose microsecond precision can round the onset even when no cropping was necessary. The report demonstrates an onset at sample 1 becoming a value that the default floor-based lookup maps to sample 0.

This was reproduced in published MNE 1.13.2 and current main `0265fc9a575f125d95c5c92f672fd0bb85cfab2d`. The fixtures are one channel of zeros for four seconds, not recordings or a simulated brain. At 512 Hz the sample interval is 0.001953125 seconds; the rounded onset is 0.001953 seconds. That 125-nanosecond difference is enough to cross the floor-index boundary. It does not mean the recording clock moved by an entire sample.

The existing `use_rounding=True` lookup maps this tested case to sample 1 on both revisions. It is a useful existing workaround, but does not restore the annotation's original float value. This candidate targets that unnecessary mutation rather than claiming MNE cannot already locate the event correctly.

## Bounded repair and integration

The [patch](preserve-interior-onsets.patch) changes the existing `Annotations.crop` method. If an annotation was not clipped on either side and its original float span is wholly within the datetime-resolved crop limits, retain the original onset. Otherwise retain the existing clipping path. The duration, channel metadata, descriptions and extras follow the existing implementation. No API, parameter, dependency, sample-based time model or global datetime replacement is added.

The supported integration is the existing `Annotations.crop` and `Raw.set_annotations` path. No application or plugin is required. This does not resolve every precision issue in #12327: clipped annotations still use datetime-resolved boundaries. Nonzero `first_samp`, arbitrary absolute clocks, serialization, HED-specific behavior and other callers need further evaluation. The separate origin/first-sample usability report [#13890](https://github.com/mne-tools/mne-python/issues/13890) is not claimed fixed.

## Before and after

[Baseline](baseline.json) and [candidate](patched.json) retain the actual source hash, input values and lookup outputs. The [released-version observation](released.json) separately identifies the installed 1.13.2 wheel.

| Sampling rate | Baseline index after attachment | Candidate index after attachment | Existing rounded lookup, both |
| --- | --- | --- | --- |
| 300 Hz | 0 | 1 | 1 |
| 512 Hz | 0 | 1 | 1 |
| 1000 Hz | 1 | 1 | 1 |
| 2048 Hz | 0 | 1 | 1 |

The existing crop test was extended across four sampling rates and dated/undated origins. Six cases fail on the unchanged source and pass with the candidate. Four additional existing tests cover negative dates, omitted limits, ignored origins and NaN durations. All 12 selected cases pass after the patch. Existing left/right clipping, out-of-bounds omission, warning/error checks and an added microsecond-boundary clipping control remain enforced. This is a selected regression run, not the full MNE suite or real-recording evaluation.

The runner retains elapsed time and the largest generated signal array size (65,536 bytes), not peak-process memory or a recording-scale benchmark. It imports and verifies the chosen source before pytest collection and uses importlib mode. This matters because otherwise tests inside the candidate package can inadvertently import the candidate during the baseline run. No test errors or skips are accepted. Network connections are blocked during the scientific test run; the root dataset-fetching conftest is not loaded.

## Reproduction

Use a fresh Kufu worktree with Git and Python 3.13. The preparation script downloads source only and excludes recording fixtures, verifies source and licence pins, applies the recorded patch and refuses to overwrite existing checkouts.

```sh
python3 projects/mne-annotation-onsets/prepare.py
python3.13 -m venv .external/mne-env
.external/mne-env/bin/python -m pip install --isolated --index-url https://pypi.org/simple -r projects/mne-annotation-onsets/requirements.txt
.external/mne-env/bin/python projects/mne-annotation-onsets/verify.py --checkout .external/mne-clean --expect baseline --output .runs/mne/baseline.json
.external/mne-env/bin/python projects/mne-annotation-onsets/verify.py --checkout .external/mne-patched --expect patched --output .runs/mne/patched.json
```

The [requirements](requirements.txt) lock the runtime, including the released MNE wheel for package metadata/resources. The imported implementation is independently locked to the source commit in [profile.json](profile.json); a package version alone does not identify that source. Complete array preservation or biological correctness is not inferred from a timestamp test. The problem page shows saved results; the separate Execution lab submits jobs only when Run is pressed.

## Parameterized execution lab

The local extension adds this case to the existing [Execution lab](../../lab.html?recipe=mne). Users can select 128–8192 Hz, an annotation sample from zero through twice the rate, and a relative or constructed UTC origin. A batch generates 300/512/1000/2048 Hz at sample 1. The signal is a deterministic four-second, one-channel linear ramp, the annotation lasts 100 ms, and `first_samp` remains zero. It is a software fixture, not a neural recording or biological simulation.

[experiment.py](experiment.py) runs the real `Raw.set_annotations` path and retains the original/attached onset, duration, floor and rounded indexes. Controls compare every signal value and the original annotation, and require rounded lookup to match the chosen sample. If the original float already maps to another sample under floor lookup, the UI shows that explicitly. Preserving an onset does not solve every float-to-index ambiguity.

The existing Vercel worker selects one of two fixed, embedded payloads; requests contain parameters only. It installs the pinned source/runtime, disables networking before science runs, compares both revisions, packages actual NumPy arrays and JSON/logs, and stops the Sandbox. Private results and timestamped progress use the existing storage/queue path. The shared limits stay at four cases, one worker, four minutes per Sandbox and ten submissions per UTC day across both experiments. No new service, account, paid plan or environment secret is added.

Local actual-software checks cover four reference cases and four boundary cases, including 128/8192 Hz, sample zero, sample limits and both origins. A maximum four-case 8192 Hz run produced a 1,707,234-byte scientific ZIP before worker metadata/logs, within the unchanged three-MB bundle cap. Reports map both input/output roles to one array file when values and dtype are exactly equal; changed outputs get a separate file. Reopening the exported arrays verified every role's recorded hash. Signal/input controls and patched timestamps are preserved. Contract checks cover recipe validation, cross-recipe ID conflicts, legacy NWB requests, failures and cleanup; browser checks use local API doubles with those real reports. They launch no hosted compute. The deployment gate now submits an actual MNE failure case and an unchanged control, verifies progress, private download hash and stopped compute alongside the existing NWB gate. Hosted MNE verification passed in PR #25 preview run [41083618486](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41083618486): the 512 Hz relative-origin case showed baseline floor index 0 versus patched 1, while the 1000 Hz UTC control remained unchanged. Both signal/input controls passed, downloads were hash-verified and the Sandbox stopped. Production status is recorded in [WORKSPACE.md](../../WORKSPACE.md).

To run custom inputs locally after the source/runtime setup above:

```sh
# Write a JSON array with 1–4 objects: {"sfreq":512,"sample":1,"origin":"relative"}.
PYTHONPATH=.external/mne-clean .external/mne-env/bin/python projects/mne-annotation-onsets/experiment.py --mode baseline --input inputs.json --output .runs/mne-custom/baseline
PYTHONPATH=.external/mne-patched .external/mne-env/bin/python projects/mne-annotation-onsets/experiment.py --mode patched --input inputs.json --output .runs/mne-custom/patched
```

## Verification and contribution boundary

The selected baseline/candidate tests and existing crop checks pass locally with the expectations above. The full applicable upstream pre-commit checks passed on both changed files: Ruff lint/preview/format, ty, codespell and static-doc consistency. Hooks for unrelated file types reported no applicable files. No hook was disabled. The lab's pinned replay and fresh-result packaging passed cloud CI for PRs #24 and #25. Full MNE suite, doc builds, real recordings, user benefit and upstream acceptance are unverified.

MNE's [contribution policy](https://github.com/mne-tools/mne-python/blob/0265fc9a575f125d95c5c92f672fd0bb85cfab2d/CONTRIBUTING.md) prohibits fully automated submissions and requires the human contributor to personally review, understand and test AI-assisted changes. It also asks that issue/PR text be written by the human. This is an agent-assisted local Kufu experiment, not an MNE contribution submission or an upstream PR draft. No outreach is authorised. A later submission would require Ahmed's own review and compliance with that policy.

Retain the [MNE BSD licence](UPSTREAM-LICENSE) with the patch. Kufu's original replay scripts and documentation use the lab's MIT licence. Recheck current upstream and related work before investing further; bounded searches found no matching open precision PR, which is not proof that no overlapping work exists.


## Generated input matrix

The local [matrix runner](verify_matrix.py) exercises 160 supported cases using the actual pinned baseline and candidate: fifteen selected rates, zero/first/one-second/two-second sample positions, both origins, and forty seeded interior cases. Every comparison uses the same reference and input hash; all 640 exported input/output array roles are reopened and hash-checked. The [retained result](matrix-result.json) identifies source hashes, runtime versions, seed and resource time. No hosted quota is consumed by this local/CI check.

The baseline changed 60 onsets and displaced 40 truncating indexes relative to the pre-attachment reference. The candidate preserved all onsets, durations and reference indexes; all unchanged-input and rounded-index controls passed. Two references already truncated to the preceding sample before attachment. At 807 Hz, sample 51 has onset `0.06319702602230483`; truncating lookup returns 50 even for that original float, while rounded lookup returns 51. The candidate preserves that onset and therefore preserves the original truncating result too. Onset preservation does not guarantee that truncation recovers the intended sample, and the existing rounded-lookup workaround remains relevant.

Run after source preparation and dependency installation:

```sh
.external/mne-env/bin/python projects/mne-annotation-onsets/verify_matrix.py --output .runs/contracts/mne/generated-matrix
```

The output directory must be new. The maintained CI addition runs this matrix inside the existing scientific gate and copies its fresh summary into the tested site. The local result passed; this new CI integration is pending publication. Coverage is constructed four-second ramps with zero first-sample offset and a 100 ms annotation, within the existing parameter bounds. It does not validate clipped/serialized annotations, physical clocks, real recordings or researcher benefit.
