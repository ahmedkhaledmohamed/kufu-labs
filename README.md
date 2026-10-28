# Kufu Labs

**Kufu** (工夫, *kufū*) is Japanese for devising better ways to do something: practical ingenuity. [Dictionary source](https://www.kanjipedia.jp/kotoba/0002126000).

An open-source lab for building and testing small tools around reported research-workflow problems. Each exploration connects an original problem report to an intended user, an implementation and evidence of what has actually improved.

## Research scope and candidate problems

Kufu investigates scientific software gaps across domains. The current research includes microscopy, neuroscience, biomedical evidence, bioinformatics, accessibility and research methods. Pose tracking is the first implemented exploration; it does not define the lab's scope or determine the next project.

The [problem board](problems.html) contains 25 candidate tasks, including hypotheses and deferred ideas. The [source directory](sources.html) links 15 boards and directories where needs, priorities and challenges are reported. These are curated research snapshots, not an exhaustive list of unsolved problems or confirmation that each proposed tool is needed.

| Area and intended beneficiaries | Candidate task and possible value | Evidence and existing work | Next validation and integration route |
| --- | --- | --- | --- |
| Microscopy researchers | Determine when predicted fluorescence or image-analysis settings change a measurement | [Light My Cells](https://lightmycells.grand-challenge.org/); existing BiaPy and napari tools | Define one measurement and compare acquisition groups or settings in the existing Python/napari workflow. A missing capability is not established. |
| Biomedical researchers | Check whether retrieved passages actually support a claim | [NLM SPARK task](https://www.nlm.nih.gov/pubs/techbull/so26/so26_spark_challenge.html); existing PaperQA | Reproduce a citation-support failure against an existing baseline; consider a library/notebook contribution. No new assistant is justified yet. |
| Scientists and students facing accessibility barriers | Complete one scientific task independently | [Notebook accessibility study](https://arxiv.org/abs/2308.03241); Olli, Data Navigator and Jupyter improvements | Reproduce a current keyboard or screen-reader barrier in the host tool. Historical findings do not establish a remaining defect. |
| Researchers reusing biological datasets | Recover sample annotations with traceable source evidence | [GEO completeness study](https://link.springer.com/article/10.1186/s13059-025-03725-0); refine.bio and MetaHQ | Test one field that existing harmonisation misses; use a dataset-specific adapter. Unpublished facts cannot be inferred reliably. |
| Neuroscience researchers | Inspect missing EEG markers or timing discrepancies | [LSL synchronisation](https://labstreaminglayer.readthedocs.io/info/time_synchronization.html) and MNE realignment | Establish a reference clock and reproduce one failure; integrate through MNE annotations or a report. No missing tool has been demonstrated. |
| Researchers analysing nested data or biomedical ML | Make experimental units and evaluation leakage explicit | [SuperPlots](https://rupress.org/jcb/article/219/6/e202001064/151717/SuperPlots-Communicating-reproducibility-and), scikit-learn guidance and DataSAIL | Compare existing tools on a declared grouping error in a notebook or pipeline. Avoid claiming automatic validation of arbitrary analyses. |
| Researchers proofreading tracked movement | Inspect overlapping poses and preserve manual corrections during filtering | [SLEAP #2816](https://github.com/talmolab/sleap/issues/2816), [movement #1027](https://github.com/neuroinformatics-unit/movement/issues/1027) and pinned local investigations | Existing technical pilots are described below. Host integration and real-workflow benefit remain separate validation steps. |

These are candidate contributions, not demonstrated unmet needs of equal strength. Sources and comparisons were reviewed on 26–27 October 2026; current status must be rechecked before selecting new work. The [research record](research/opportunity-discovery/README.md) retains further candidates, alternatives and limitations.

## Implemented work and remaining proof

- **[Pairwise overlap inspector](projects/overlap-inspector/README.md):** a browser inspector of seven constructed examples for people proofreading overlapping pose predictions. It shows unchanged filter output and its explanation. It could reduce trial-and-error when choosing settings, but does not accept users' own poses or integrate into SLEAP. Prevalence, time saved and better decisions are unmeasured.
- **[movement edit-aware filtering](projects/movement-edit-filtering/README.md):** a local patch preserves an explicit correction while dropping an unscored prediction in the tested workflow. Reproducible Qt/model-event checks cover that subproblem. The broader upstream request, rendered user interaction and practical user benefit remain unvalidated.

These pilots provide technical evidence for specific tasks. They do not establish that pose tracking deserves priority over the other areas. No end-to-end user problem is claimed resolved.

## Explore and run

Live site: [kufu-labs.vercel.app](https://kufu-labs.vercel.app/) (Vercel sign-in).

Open [Home](index.html), [Explorations](explorations.html), [Problems](problems.html), [Sources](sources.html) or [Validation](validation.html). Each tab is an independent page; the interactive pose demo can open in a separate browser tab. Exploration entries describe the runtime, constructed inputs, launch command, expected result and verification limits.

Run `npm ci --ignore-scripts --no-audit --no-fund`, then `npm run build` and `npm test`. Serve the reviewed package with `python3 -m http.server 8879 --bind 127.0.0.1 --directory dist`. See [delivery](site/DELIVERY.md) for pinned scientific checks, the protected Vercel pipeline and retained evidence; [WORKSPACE.md](WORKSPACE.md) records actual publication/deployment state.

## Explorations

| Exploration | Current evidence | Remaining validation |
| --- | --- | --- |
| [Pairwise overlap inspector](projects/overlap-inspector/README.md) | Offline synthetic demo checked against a pinned sleap-nn tensor filter | Real host instance/skeleton/score integration and researcher workflow benefit |
| [movement edit-aware filtering](projects/movement-edit-filtering/README.md) | Local patch; 97 earlier synthetic filtering cases and a real Qt-widget/model-event replay | API acceptance, rendered host interaction and real-workflow benefit; separate deletion-provenance defect remains |
| [Pose-review task research](research/pose-review-validation/README.md) | Existing-tool audit and one specific pairwise-score request | Proposed outcome study is unrun; outreach is deferred |
| [Opportunity discovery](research/opportunity-discovery/README.md) | Named candidates, existing tools, source boards and comparative audit | Most ideas lack a demonstrated remaining gap |

The board aggregates 25 named candidates from these records, including deferred concepts and competing work, with 15 source boards/directories. It is a curated snapshot, not an exhaustive census or a live feed. No end-to-end user problem is claimed resolved.

## Structure and boundaries

`research/` preserves sourced investigations and decisions. `projects/<name>/` keeps each contribution, executable check, source pin and limits. `site/catalog.json` is the maintained hub catalogue; `site/build.py` generates the root website and safe, readable copies of the Markdown research records. Keep upstream implementation checkouts separate.

The [deletion diagnostic](projects/movement-edit-filtering/DELETION-PROVENANCE.md) records an unfixed repeated-export provenance defect. The coordinate-filtering result and this remaining defect are kept separate. Source revisions, patches, commands and outcomes live with each project.

No recordings, model weights, environments, patient information or credentials belong in the repository. Dataset, model and software licences are independent. A passing check does not establish scientific correctness, adoption, clinical utility or researcher benefit.

## Licensing

The lab's original code and documentation use the [MIT License](LICENSE), except where an existing project-specific licence or upstream notice applies:

- The [pose overlap inspector](projects/overlap-inspector/COPYING), including its source and generated demo, remains GPL-3.0-only.
- Upstream movement code included in the filtering patch retains its [BSD-3-Clause notice](projects/movement-edit-filtering/UPSTREAM-LICENSE). The lab's original integration and verification scripts use the default MIT licence.

Retain the applicable project and upstream notices when redistributing. These software licences do not grant rights to recordings, model weights, external datasets or linked publications.

Vercel production deployment is explicitly authorised in the personal scope, with Authentication protection for production and previews. The CI pipeline must verify the tested artifact and current main before promotion. Publication still follows full-diff/contribution-record/exact-commit approval and explicit PR merge authorisation. Outreach, new accounts, paid services and data/model downloads remain outside scope.
