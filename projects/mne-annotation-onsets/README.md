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

The [requirements](requirements.txt) lock the runtime, including the released MNE wheel for package metadata/resources. The imported implementation is independently locked to the source commit in [profile.json](profile.json); a package version alone does not identify that source. Complete array preservation or biological correctness is not inferred from a timestamp test. The webpage shows saved results and starts no Python, kernel or Vercel job.

## Verification and contribution boundary

The selected baseline/candidate tests and existing crop checks pass locally with the expectations above. The full applicable upstream pre-commit checks passed on both changed files: Ruff lint/preview/format, ty, codespell and static-doc consistency. Hooks for unrelated file types reported no applicable files. No hook was disabled. The lab's CI addition will run this replay and package fresh results; its cloud result remains pending publication. Full MNE suite, doc builds, real recordings, user benefit and upstream acceptance are unverified.

MNE's [contribution policy](https://github.com/mne-tools/mne-python/blob/0265fc9a575f125d95c5c92f672fd0bb85cfab2d/CONTRIBUTING.md) prohibits fully automated submissions and requires the human contributor to personally review, understand and test AI-assisted changes. It also asks that issue/PR text be written by the human. This is an agent-assisted local Kufu experiment, not an MNE contribution submission or an upstream PR draft. No outreach is authorised. A later submission would require Ahmed's own review and compliance with that policy.

Retain the [MNE BSD licence](UPSTREAM-LICENSE) with the patch. Kufu's original replay scripts and documentation use the lab's MIT licence. Recheck current upstream and related work before investing further; bounded searches found no matching open precision PR, which is not proof that no overlapping work exists.
