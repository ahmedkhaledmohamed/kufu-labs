# Scientific software lab

Private lab for scientific-software explorations, reproducible experiments, upstream contributions and small demonstrations.

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

The [deletion diagnostic PR #3](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/3) has a prepared conflict resolution preserving both the merged hub and its diagnostic records. Those records are incorporated locally for the delivery work; remote merge status is tracked in WORKSPACE.md. Research originals and modified implementation worktrees are preserved.

No recordings, model weights, environments, patient information or credentials belong in the repository. Dataset, model and software licences are independent. A passing check does not establish scientific correctness, adoption, clinical utility or researcher benefit.

Vercel production deployment is explicitly authorised in the personal scope, with Authentication protection for production and previews. The CI pipeline must verify the tested artifact and current main before promotion. Publication still follows full-diff/contribution-record/exact-commit approval and explicit PR merge authorisation. Outreach, new accounts, paid services and data/model downloads remain outside scope.
