# NWB stream integrity during inspection

Status: lab-published patch and constructed-data replay; [upstream review package](REVIEW.md) prepared locally. No upstream PR, researcher validation or real-recording evaluation. The [implementation and learning plan](../../research/opportunity-discovery/NEUROINFORMATICS-PLAN.md) explains the next milestones.

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

Upstream baseline: [NWB Inspector e6d968a](https://github.com/NeurodataWithoutBorders/nwbinspector/tree/e6d968a1e0a62aa8f6611f45f242196d9ce75ea5), package version 0.7.3. The local [patch](non-consuming-shape.patch) modifies the existing shape helper and adds regression tests in that project. It re-exports HDMF 6.2.0's existing `get_data_shape` helper instead of maintaining an Inspector-specific copy. That helper already supports the declared shape of the tested wrapped chunk iterators and the current shape of stored resizable datasets. It does not add a general policy for arbitrary single-pass iterators.

The supported integration is the existing `inspect_nwbfile_object` conversion workflow. No new application, plugin or monkey patch is required. [Issue #760](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/760) proposes reusing HDMF's helper; [HDMF PR #1606](https://github.com/hdmf-dev/hdmf/pull/1606) proposes a related wrapper fix and was open when checked. The existing-helper substitution and the pinned dependency PR each preserved all values across the 24-case constructed replay. The helper substitution also passed 330 existing unit tests, with 5 skipped, before this source patch was prepared. We selected reuse of the released helper for the smaller maintenance surface; upstream may prefer a different design.

## Run the actual workflow

From a fresh lab worktree, with Git and Python 3.13 available, use the [source preparation script](prepare.py). It verifies the revision and patch digest and refuses to overwrite existing NWB checkouts:

```sh
python3 projects/nwb-stream-integrity/prepare.py
python3.13 -m venv .external/nwb-env
.external/nwb-env/bin/python -m pip install --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements.txt
.external/nwb-env/bin/python -m pip install --index-url https://pypi.org/simple --no-deps -e .external/nwb-patched
PYTHONPATH=.external/nwb-clean/src .external/nwb-env/bin/python projects/nwb-stream-integrity/verify.py --expect baseline --output .runs/nwb/baseline.json
PYTHONPATH=.external/nwb-patched/src .external/nwb-env/bin/python projects/nwb-stream-integrity/verify.py --expect patched --output .runs/nwb/patched.json
```

The [runner](verify.py) rejects a different upstream Git revision. It records the loaded utility source hash and the patch digest. Its assertions compare all array values, check the uninspected controls and require the patched inspection to avoid ERROR messages. Temporary NWB files are removed after each case. The JSON output remains in the chosen output location. The investigation pages display retained results; the separate execution lab submits explicitly requested experiments.

## Released-version comparison

On 29 October 2026, the same replay also passed against the public [0.7.2 release](https://github.com/NeurodataWithoutBorders/nwbinspector/releases/tag/v0.7.2), commit `36f3a47302f37b0c53e4e60ae1de19ebeceb1d2d`. Issue #771 reports Inspector 0.7.2, PyNWB 4.2.0, HDMF 6.2.0 and Python 3.12. This profile uses those three library versions and selects Python 3.12.12 for reproducibility; it does not reconstruct every package from the reporter's environment.

The release-context [patch](released-0.7.2-shape.patch) makes the same existing-helper substitution and carries the same 11 regression cases. The version helpers surrounding the function differ from the development revision, so the original patch does not apply unchanged. The [profile](released-profile.json) locks the release commit, baseline/patched utility hashes, patch digest and upstream licence hash.

[Released baseline results](released-baseline.json) lose values in all 12 inspected cases; [released patched results](released-patched.json) preserve all values in all 12, without Inspector ERROR messages. All 24 uninspected controls across both revisions preserve every value. The loss pattern is the same 50, 100 or 300 rows shown above. The replay took 3.028 seconds before the patch and 3.061 seconds after it on the local macOS arm64 runtime; these small fixtures do not establish recording-scale performance.

The released unit suite has three pre-existing failures with this dependency stack: an external ImageSeries fixture omits `num_samples`, and two DynamicTableRegion fixtures construct out-of-range indices that current dependencies reject. The unchanged release has 278 passing tests, 3 failures and 5 skips; the patched release has 289 passing tests, the same 3 failures and 5 skips. See the [comparison](released-unit-comparison.json). This is not a fully passing release suite. The [unit comparison runner](verify_release_units.py) gates the exact known failure names, total test counts and skip counts; any different failure, collection error or missing regression fails the check. Full logs and JUnit reports remain CI artifacts.

From a fresh lab worktree with Python 3.12.12:

```sh
python3 projects/nwb-stream-integrity/prepare.py --released
python3.12 -m venv .external/nwb-release-env
.external/nwb-release-env/bin/python -m pip install --isolated --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements.txt
.external/nwb-release-env/bin/python -m pip install --isolated --index-url https://pypi.org/simple --no-deps -e .external/nwb-release-clean
PYTHONPATH=.external/nwb-release-clean/src .external/nwb-release-env/bin/python projects/nwb-stream-integrity/verify.py --released --expect baseline --output .runs/nwb-release/baseline.json
PYTHONPATH=.external/nwb-release-patched/src .external/nwb-release-env/bin/python projects/nwb-stream-integrity/verify.py --released --expect patched --output .runs/nwb-release/patched.json
.external/nwb-release-env/bin/python projects/nwb-stream-integrity/verify_release_units.py --output .runs/nwb-release
```

Source preparation and patch application passed again in a fresh temporary directory. Ruff and Black passed for the changed upstream module and regression file; the existing development-profile replay also passed again unchanged. The required scientific CI job now includes this isolated released profile, and the web build copies its newly generated results. A cloud result for this addition is pending publication. The hosted execution lab continues to run its documented development pin; it does not yet offer release selection.

## Parameterized execution lab

[Execution lab](../../lab.html) uses [experiment.py](experiment.py) to generate synthetic signals with editable rows, channels, buffer size, seed, pattern, file backend and iterator type. A boundary batch generates cases below, at and above the buffer size, plus a larger case. Generating the input plan is local; pressing Run submits scientific execution to Vercel.

Vercel Functions validate requests and publish to Vercel Queues. The worker starts a non-persistent, one-vCPU Vercel Sandbox, prepares the pinned upstream revision and patch, installs complete CPython 3.13.9 using uv 0.9.5 and the pinned requirements, then disables network access. Each revision gets fresh inspected and uninspected objects, iterators and files. Every value, shape and dtype is compared. Private Blob storage retains reports, logs and an archive of actual NumPy arrays and file round trips after the Sandbox stops. The lab accepts parameters, not recordings or arbitrary code.

On 28 October 2026, a direct SDK run of the local implementation in a real Vercel Sandbox completed in 16.301 seconds and stopped its VM. A 500-row, two-channel HDF5 ramp changed 300 baseline rows and zero patched rows. A seeded random 51-row, three-channel Zarr input with a generic iterator changed 51 baseline rows and zero patched rows. All four uninspected controls preserved every value. The initial hosted runtime lacked `_bz2`; installing complete pinned CPython resolved that failure without disabling Zarr. This direct SDK result does not establish that the deployed queue/API/storage flow has passed.

Local parameterized verification also covers one row, three channels with Zarr, the maximum 2,000 × 8 shape and seed boundary, and alternating-sign values. CI repeats those real round trips. API checks cover validation, cross-site rejection, duplicate delivery, failed execution and result classification. Browser checks use local API doubles and real scientific reports; they launch no Sandbox. The deployment gate separately submits real HDF5 and Zarr jobs to the protected Vercel preview, waits for the actual Queue/Sandbox worker, verifies saved comparisons and checks the private download hash before production promotion. The deployed gate passed before promotion in merged-main [run 40877666335](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40877666335).

The execution page also displays timestamped progress reported by the worker: queue wait, environment setup, baseline/patched runs, output packaging, compute shutdown and saving the result bundle. Running snapshots are private; completed and failed results retain the final history. Elapsed time is calculated from those timestamps, with no estimated completion percentage. Reloading reads the same run, and interrupted or unavailable status is displayed explicitly. Hosted progress also passed on merged main. Production run `9ebc0340-6763-4a6f-b05f-973270fde296` retained all 13 stages; an independent audit verified its private archive hash, stopped Sandbox and protected API.

Bounds are four cases per submission, 2,000 rows × 8 channels per case, four minutes per Sandbox, one concurrent queued worker and ten ordinary submissions per UTC day shared by preview and production; authenticated delivery CI uses a separate twenty-submission pool. Reusing a request ID and a claimed queue message prevents duplicate VM launches. Interrupted workers become an explicit interrupted status. Completed runs remain in private storage; no automatic retention cleanup is installed. The existing Hobby project uses the private `kufu-experiments` store in deployed previews and production. Main CI promoted the tested artifact to the protected production URL. No paid plan upgrade or new provider account was created.

## Verification and limits

The replay passed locally on Python 3.13.2 with PyNWB 4.2.0, HDMF 6.2.0, HDMF-Zarr 0.14.0, h5py 3.16.0, Zarr 3.4.2 and NumPy 2.5.4. The [requirements](requirements.txt) retain the public package versions from this environment; no local editable paths are included. The exact Inspector source is installed separately.

The broader local unit run passed 341 tests, including 11 new stream/shape cases, with 5 skipped. Ruff and Black passed on the two changed upstream files. This includes checking that an existing resizable HDF5 dataset reports its current shape, and that existing time-series validation still detects its tested failures. Broader unit regression results and final patch reapplication are recorded in [verification](verification.json).

The initial scope does not cover real recordings, every NWB extension or iterator implementation, all dependency versions, performance at recording scale, upstream acceptance or researcher benefit. Shape metadata itself may be incorrect. Preserving values does not prove acquisition quality or scientific validity. The follow-up workflow runs this replay and the unit regressions inside the existing required scientific-contract check, using an isolated environment. The web build consumes that run's JSON results. The required check and deployment passed on merged main in [run 40613968067](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40613968067); packaged and production results were independently verified.

## Science to understand alongside this patch

A time series is a sequence of measurements indexed by time. Here a row holds two constructed channel values and 100 Hz means 100 samples per second. In a real recording, channel meaning and units depend on the measurement method: spikes, local field potentials and EEG are different representations and cannot be treated interchangeably.

NWB organises measurements and associated metadata so they can be stored and reused. Chunk iterators allow conversion without loading an entire recording into memory. Advancing a single-pass iterator changes what the next consumer receives. An inspection step should preserve the stream for the writer. That is the specific software invariant tested here, not a new neuroscience finding.

## Publication and licence

The patch is published in the lab, with a separate local upstream-review package. The upstream [developer guide](https://github.com/NeurodataWithoutBorders/nwbinspector/blob/e6d968a1e0a62aa8f6611f45f242196d9ce75ea5/docs/developer_guide.rst) asks contributors not to open a PR before the issue is approved by its team. No approval, maintainer discussion, fork push or upstream PR is claimed. Outreach remains deferred.

Retain the [upstream licence](UPSTREAM-LICENSE), including its enhancement clause, with the patch. The lab's original replay and documentation use the repository default MIT terms. The next step is review of the mechanism, integration limits and existing upstream alternatives before any authorised upstream discussion.

## Installable experimental wheels

The [wheel builder](build_wheels.py) now packages the pinned 0.7.2 release as two pure-Python distributions: `0.7.2+kufu.baseline1` reproduces the unchanged source, and `0.7.2+kufu.stream1` includes the existing released-profile shape repair. These are experimental Kufu builds, without upstream endorsement or acceptance. The baseline build is for comparison and reproduces data loss.

The scientific patch is unchanged. Packaging changes give each build a distinct local version, embed a source/patch provenance JSON file, and explicitly include the complete upstream licence as `nwbinspector/UPSTREAM-LICENSE`. The initial build check rejected a wheel without that notice; no such build is offered for download. Every package file is checked against the pinned source before building; all installed Python/configuration files, licence, wheel hash and package import origins are verified. No source package is copied into the fresh test environments, no editable install is permitted, and the selected tests use importlib collection with a package-origin guard before and after execution.

The [retained build result](wheel-result.json) identifies both wheels, hashes, exact builder versions, installed-package verification and scientific results. Each fresh Python 3.12.12 environment installs the locked dependencies and its wheel offline from a prepared local wheelhouse, followed by `pip check`. The real Inspector runs before HDF5/Zarr writing and reopening in the existing 24-case replay: two backends, two iterator types, three lengths and inspected/uninspected cases. Runtime network connections are blocked. The entire selected released unit suite and the candidate's 11 regressions run against the installed packages, retaining the same three named dependency-related failures and five skips rather than calling the suite fully passing.

| Installed build | Inspected cases preserving every value | Uninspected controls | Selected release unit suite |
| --- | --- | --- | --- |
| Baseline | 0/12 | 12/12 | 278 passed, 3 known failures, 5 skipped |
| Experimental repair | 12/12 | 12/12 | 289 passed, same 3 failures, 5 skipped |

The complete local two-build run took 71.126 seconds, including fresh offline installs, 48 native round trips and both selected unit suites. Each wheel is below 100 KB. Negative probes verify that a source-checkout import and altered wheel bytes are rejected.

The local macOS setup initially copied the standalone Python executable into a new environment, which broke its relative dynamic-library lookup. Fresh environments now use interpreter symlinks, as the normal venv command does on this platform. A first unit-collection attempt also exposed that the upstream streaming probe handles normal OS network errors, while the harness raised a different exception; the blocker now raises `OSError`, without making a connection. The same five existing network-dependent skips remain enforced. These harness changes do not alter Inspector or its expected failures.

From a fresh lab worktree, prepare the source using the earlier released-profile command, then use Python 3.12.12:

```sh
python3 projects/nwb-stream-integrity/prepare.py --released
python3.12 -m venv .external/nwb-wheel-builder
.external/nwb-wheel-builder/bin/python -m pip install --isolated --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements-build.txt
.external/nwb-wheel-builder/bin/python -m pip download --isolated --index-url https://pypi.org/simple --only-binary=:all: -r projects/nwb-stream-integrity/requirements.txt -d .external/nwb-wheelhouse
.external/nwb-wheel-builder/bin/python projects/nwb-stream-integrity/build_wheels.py --runtime-root .external/nwb-wheel-runtimes --wheelhouse .external/nwb-wheelhouse --output .runs/nwb-wheels
```

The output and runtime locations must be new; existing environments are preserved. Output contains both wheels, a complete package-file manifest, installed replay JSON, logs and JUnit reports. Dependencies and environments remain outside the published artifacts. Build tools are pinned in [requirements-build.txt](requirements-build.txt); wheel timestamps use a fixed source-date epoch for stable packaging. Cross-platform byte reproducibility is not claimed. The builder verifies source files, never modifies the pinned source worktrees, and preserves the upstream licence and attribution.

Scientific CI now builds and tests the wheels and supplies its fresh results/downloads to the site. The site packager accepts only the two expected wheel names, hashes and size bounds. Generated wheels are ignored by Git; source and result manifests are reviewed. A source-only site build without generated wheels displays reproduction instructions instead of broken download links. Scientific CI passed in [PR #31 run 41314310305](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41314310305). Independent checks verified both Linux wheel archives and all package-file hashes; they match the local wheel bytes. The protected preview gate then timed out on native browser downloading: the request omits Playwright context authentication headers. The verifier now requests Vercel’s documented automation bypass cookie in its existing authenticated browser context. A local HTTP probe verifies the cookie-authenticated download and exact bytes without a custom download header. This correction passed protected preview and production verification after PR #32 in [main run 41352041534](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41352041534). Deployment Protection remains enabled.

After downloading the repaired wheel from the problem page into a lab checkout, install it separately:

```sh
python3.12 -m venv .venv-nwb-experiment
.venv-nwb-experiment/bin/python -m pip install --isolated --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements.txt ./nwbinspector-0.7.2+kufu.stream1-py3-none-any.whl
.venv-nwb-experiment/bin/python -c "import nwbinspector; print(nwbinspector.__version__)"
```

Compare the download's SHA-256 with the build result or problem page before installation. Use the existing `inspect_nwbfile_object` API in that environment; no wrapper API or runtime monkey patch is introduced. These checks establish the tested installation and data-preservation behavior, not recording-scale safety, recovery of already damaged files, arbitrary dependency compatibility, scientific validity or researcher benefit. No package-registry publication, upstream PR or outreach is included.

## Electrode recording conversion example

A converter must preserve which electrode each column represents, how acquisition counts become volts and when each sample occurred, as well as the values themselves. The runnable [ElectricalSeries example](ecephys.py) follows the [existing PyNWB workflow](https://pynwb.readthedocs.io/en/stable/tutorials/domain/ecephys.html) and uses the installed experimental wheels. It does not introduce a new converter or change the scientific patch.

The source generates signed integer patterns for 16 constructed channels, including legitimate zeros. Each column references an electrode-table row in deliberately reversed order. The file stores a fictional calibration of 0.1 microvolt per count, separate channel factors, a 20,000 Hz sampling rate (50 microseconds between samples) and a 0.25-second start time. These values and electrode identities are software fixtures, not recordings or a biological simulation.

The script generates 4,096 rows per buffer, calls the real Inspector, writes HDF5 NWB and reopens it. Readback compares every value in blocks and independently checks electrode IDs and labels, column links, voltage conversion, channel factors, offset, start time and rate. PyNWB schema validation is an additional structural check: both baseline and repair files pass it, even though the baseline values differ from the input.

The [retained result](ecephys-result.json) contains 12 separate-process conversions: baseline and repaired wheels, inspected and uninspected controls, at 0.5, 16 and 128 MiB of generated sample data. All repaired conversions and all uninspected controls preserve every value. Inspection consumes three baseline buffers before writing, changing 12,288 rows at every tested size. In the small case, the first channel's first count should be 12,514; the baseline saves zero and the repair saves 12,514. A zero alone is not evidence of corruption because zeros also occur in the source.

Electrode links, voltage scale and timing remain correct on both revisions. Baseline inspection produces three ERROR messages; repaired inspection produces none, although other metadata recommendations remain. Shape and schema validity alone would therefore miss this value loss. No claim about acquisition quality, biological validity, real-recording safety or researcher benefit follows from these checks.

After installing the repaired wheel as described above, run from the lab checkout:

```sh
.venv-nwb-experiment/bin/python projects/nwb-stream-integrity/ecephys.py --expect patched --retain --output .runs/ecephys-example
```

The output directory must be new. It contains `constructed_ecephys.nwb` and `result.json`. The same script can run in an existing notebook whose kernel uses this environment; open the native file with PyNWB or an NWB-compatible viewer. `--rows`, `--channels` and `--buffer` permit bounded variations; `--skip-inspection` runs the control. Use `--expect baseline` only in the separate baseline wheel environment. Without `--wheel-record`, the example verifies the installed version, package origin, shape-helper hash and reported PyNWB/HDMF versions. The complete comparison additionally verifies all installed package files against the wheel manifest.

After the earlier wheel-build command, run the complete installed-wheel comparison:

```sh
python3 projects/nwb-stream-integrity/verify_ecephys.py --runtime-root .external/nwb-wheel-runtimes --wheel-record .runs/nwb-wheels/wheel-manifest.json --output .runs/ecephys-comparison
```

The comparison times out each case after 120 seconds and rejects results at or above 512 MiB peak process RSS or a 160 MiB generated file. Those resource checks occur after generation; they are acceptance bounds, not operating-system memory limits. Generation and readback use bounded blocks, but total process memory includes dependencies and HDF5 caches and rose with input size. The retained local run completed in 14.258 seconds with a maximum process RSS of 197.0 MiB; this does not establish constant-memory behavior or recording-scale performance.

The runner removes larger files after validation and retains four small native files in a hash-checked `ecephys-example.zip` with comparison results. Scientific CI repeats the 12 conversions using its installed wheel environments and supplies fresh JSON and this generated download to the problem page. The archive is ignored by Git, explicitly size/hash checked by the site packager and verified through an actual browser download. A source-only site build offers reproduction instructions instead of a broken archive link.

The problem page displays retained local/CI evidence. This full electrode example runs in Python; the existing hosted Execution lab still runs its separate generic stream recipe. No hosted recipe, recording upload or new compute allocation is introduced.
