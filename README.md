# Kufu Labs

**Kufu** (工夫, *kufū*) is Japanese for devising better ways to do something: practical ingenuity. [Dictionary source](https://www.kanjipedia.jp/kotoba/0002126000).

An open-source lab for building and testing small tools around reported research-workflow problems. Each exploration connects an original problem report to an intended user, an implementation and evidence of what has actually improved.

## Problems, people and expected value

| Problem | Who encounters it | Original evidence | Current contribution | Expected value and remaining proof |
| --- | --- | --- | --- | --- |
| Choosing overlap-filter settings requires guessing pairwise similarity | People proofreading overlapping pose predictions in SLEAP | [SLEAP #2816](https://github.com/talmolab/sleap/issues/2816) asks to select two instances in the GUI and see their IoU/OKS scores | A browser inspector of seven constructed examples, with unchanged filter output and its explanation | Could reduce trial-and-error when choosing settings. It does not yet accept users' own poses or integrate into SLEAP; prevalence, time saved and better proofreading decisions are unmeasured. |
| Keeping manually corrected poses while filtering unscored predictions | Users processing proofread movement pose datasets | [movement #1027](https://github.com/neuroinformatics-unit/movement/issues/1027) and the [pinned local investigation](projects/movement-edit-filtering/README.md) | A local explicit-edit filtering patch with reproducible Qt/model-event checks | Preserves a correction while dropping an unscored prediction in the tested workflow. The broader upstream request, rendered user interaction and practical user benefit remain unvalidated. |

These are specific reported needs, not evidence that they affect most researchers or are the most important scientific problems. The overlap inspector adds visibility; it does not change the filtering algorithm. Technical execution, host integration and useful human outcomes are tracked separately.

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
