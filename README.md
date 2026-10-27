# Scientific software lab

Private lab for scientific-software explorations, reproducible experiments, upstream contributions and small demonstrations.

**Open [the lab hub](index.html)** for the exploration directory, searchable problem/evidence board, source-board links and validation ledger. The hub runs as a standalone local file without accounts, hosted services or runtime dependencies. Alternatively serve the repository locally:

```sh
python3 -m http.server 8878 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8878`. Start with [WORKSPACE.md](WORKSPACE.md) for the current working handoff and [site/README.md](site/README.md) to maintain or verify the hub.

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

The [separate open PR #3](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/3) contains the deletion diagnostic and earlier publication status. Its files are not duplicated by this change. Research originals and modified implementation worktrees are preserved.

No recordings, model weights, environments, patient information or credentials belong in the repository. Dataset, model and software licences are independent. A passing check does not establish scientific correctness, adoption, clinical utility or researcher benefit.

Private storage does not authorise outreach, new accounts, spending, public deployment or merging. The current work prepares a private lab PR; publication still follows full-diff/contribution-record/exact-commit approval. No merge is authorised.
