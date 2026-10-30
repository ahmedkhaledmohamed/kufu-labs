# Cross-domain validation batch

Reviewed 27 October 2026. Autonomous-goal working evidence: finish the NWB review package, compare concrete accessibility and metadata tasks, and implement only a surviving bounded improvement. Observed results, existing work and unanswered questions remain separate.

## Decision

Prepare the NWB package for review, retain the existing JupyterLab fixes instead of competing with them, and investigate a small source-discovered refine.bio omission: numeric age zero is dropped during harmonisation. A local component patch now preserves it. No new application is justified by this batch.

| Candidate | Source and current competing work | Local observation | Disposition |
| --- | --- | --- | --- |
| NWB streamed-data preservation | [Inspector #771](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771), existing helper proposal [#760](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/760), dependency [PR #1606](https://github.com/hdmf-dev/hdmf/pull/1606) | Real HDF5/Zarr round trips and required CI passed; the [review package](../../projects/nwb-stream-integrity/REVIEW.md) preserves mechanism, alternatives and limits. | Review locally. Reuse the preferred upstream work when agreed; no claim that Kufu originated the existing proposal. |
| Toolbar-menu keyboard focus | [JupyterLab #20190](https://github.com/jupyterlab/jupyterlab/issues/20190); [PR #20265](https://github.com/jupyterlab/jupyterlab/pull/20265) already proposes a fix | In JupyterLab 4.6.4 / Chrome 156, clicking the built-in console prompt-position menu leaves focus in the editor; ArrowDown does not activate a menu item. Empty constructed console; no kernel started. | Failure reproduced, but an implementation already exists. No competing patch. That PR was not independently built or tested here. |
| File-browser keyboard selection | [JupyterLab #15819](https://github.com/jupyterlab/jupyterlab/issues/15819) includes plain-Space and screen-reader/browser-specific observations | With two empty constructed text files in JupyterLab 4.6.4, plain Space retained the selected row and Ctrl+Space toggled it off. | Partial observation only. No screen reader or Firefox tested; do not describe keyboard access as wholly missing or the issue as resolved. |
| Generic BioSample enrichment | Older [refine.bio documentation](https://docs.refine.bio/en/latest/main_text.html#metadata) says BioSample metadata is not obtained | Source at `7b809b7cae8d8a16f635febda80ac0c7336de9d7` calls `gather_biosample_metadata` during run-metadata gathering and fetches the EBI BioSamples API. | Reject the generic missing-capability claim. Code contradicts the older documentation for this path; production availability is not established by source inspection. |
| Zero-valued age annotations | Source retention condition in that same harmoniser; no matching direct issue or PR found in the bounded age/zero and harmonisation searches | The actual component drops 16/16 constructed zero-age variants. The harmoniser patch retains all 16; positive/unknown/empty controls keep their expected behaviour. An additional zero-loss fallback was found and patched in the actual model metadata method, with five offline handoff cases and three model regression methods. | Implemented locally as a component defect. No public affected sample, workflow frequency or user benefit established. [Record and executable replay](../../projects/refinebio-zero-age/README.md). |

## Reproduction boundaries

JupyterLab was installed as published version 4.6.4 (release commit `384bff3af6598b3a6348df58fe34450914b49c41`) in an isolated environment. The application ran on localhost with a temporary root containing only empty constructed files and no additional extensions/settings. The browser used an isolated profile and blocked requests to other origins. Tests exercised the actual application; no patched frontend or assistive technology was tested.

The refine.bio replay imports the actual harmoniser with a minimal local Django configuration and blocked network connections. It is not an AST reconstruction or a reimplementation of its algorithm, but also not a complete database-backed service reproduction. The separate model replay imports the actual Sample class and reads an empty in-memory annotation table using unsaved model fixtures; cloud clients are inert and production readiness hooks are disabled. A follow-up now passes the selected save/reload/metadata path on PostgreSQL 16.2 with actual model-defined schema, private fixture databases and the existing Sample metadata-key regression. Production signals, official migrations, output-file generation and the full upstream suite remain untested. The source is BSD-3-Clause; the patch retains the licence. Individual annotations in the upstream example datasets were not copied into the lab.

The [retained browser observations](accessibility-observations.json) and [browser replay](verify_jupyter_accessibility.cjs) make the accessibility check inspectable. To repeat it, install JupyterLab 4.6.4 in an isolated environment, serve a temporary root containing empty `alpha.txt` and `beta.txt`, enable core mode and `LabApp.expose_app_in_browser`, and bind the fixture server to `127.0.0.1:8897`. The replay expects that localhost server and the lab's installed Playwright dependency; run `node research/opportunity-discovery/verify_jupyter_accessibility.cjs`. Set `CHROME_PATH` when using a local Chrome executable. Do not point it at personal notebooks. Its report defaults to `/tmp/kufu-jupyter-accessibility.json`.

The issue/PR searches are bounded discovery checks, not proof that no duplicate exists anywhere. All source states must be refreshed before an upstream submission. Neither an open issue nor a source defect establishes population prevalence.

## Why this selection fits Kufu

The next implementation changes an established tool's behaviour on a concrete input and has an observable preservation result. It does not turn a broad medical priority into an unsupported product claim. The engineering result is attributable, but the source-discovered defect should not be marketed as a user-validated need.

The three domains remain in comparison: neuroinformatics has a technically demonstrated contribution, accessibility has a reproduced failure with existing work, and bioinformatics has a newly reproduced component omission. We can stop a candidate because existing work covers it. Breadth of investigation does not require parallel speculative applications.

## Next steps

Review the NWB package and the zero-age component patch. Validate the latter in the complete upstream test environment before calling the integration complete. Keep the JupyterLab findings as comparisons and potential regression evidence. Continue the gradual [learning plan](NEUROINFORMATICS-PLAN.md) with the [first signals exercise](SIGNALS-EXERCISE.md), without turning coursework into the lab's main output. Outreach and publication retain their explicit gates.

## 30 October follow-up

The earlier NWB, refine.bio and movement work now has maintained host/CI evidence. The next comparison deliberately looked beyond pose software. This is a bounded refresh, not a new audit of every domain in the plan.

| Candidate | Fresh evidence and remaining work | Decision |
| --- | --- | --- |
| Jupyter toolbar focus | Existing [PR #20265](https://github.com/jupyterlab/jupyterlab/pull/20265) remains open at `78e8abdc543e9ddada3dce9658afd456b1c28ef7`. The earlier 4.6.4 reproduction is retained; this follow-up did not rebuild that PR. | Avoid a competing implementation. |
| File-browser focus after closing a menu | [#14153](https://github.com/jupyterlab/jupyterlab/issues/14153) remains open and has a recent proposed Lumino approach. No new host/screen-reader test was run in this follow-up. | Retain for accessibility comparison; no validated new implementation selected. |
| MNE annotation timestamp precision | [#12327](https://github.com/mne-tools/mne-python/issues/12327) reproduces in release 1.13.2 and current main. Constructed sample-1 onsets round through datetime even without clipping. Existing rounded lookup is a workaround. | A bounded candidate preserves unchanged interior onsets. Six baseline cases fail and all 12 selected candidate tests pass; the complete applicable upstream pre-commit run passes. [Source, patch and replay](../../projects/mne-annotation-onsets/README.md). |
| MNE annotation origin/first-sample usability | [#13890](https://github.com/mne-tools/mne-python/issues/13890) is a separate report about retrieving the intended span when first-sample offsets are present. | Not reproduced or claimed fixed by this candidate. |

The MNE fixtures contain only generated zeros, not recordings or a neural model. No clocks, acquisition setup, clinical use, research finding or researcher time saving was validated. Sampling intervals and float-to-sample indexing are the accompanying science concepts: a tiny rounding change can cross a floor-index boundary without representing an equally large physical time shift.

MNE's pinned contribution policy requires the human to personally review and understand AI-assisted work, prohibits fully automated submissions and asks the human to write any upstream issue/PR text. This is local Kufu evidence, with no upstream submission or outreach. The complete MNE suite and real recordings remain outside this pilot. Microplates, microscopy and other research hypotheses remain unselected; no unsupported product was added merely to increase breadth.
