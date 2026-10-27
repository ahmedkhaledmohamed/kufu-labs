# movement edit-aware filtering

Use movement's existing boolean `edited` provenance to retain explicitly corrected pose points during confidence filtering, while allowing other unscored predictions to be dropped.

- [Scope, implementation result, and reproduction commands](PILOT.md)
- [Complete implementation patch](movement-pilot.patch)
- [Environment and resource measurements](movement-pilot-environment.json)
- [Evidence and rejected alternatives](../../research/opportunity-discovery/AUDIT.md)
- [Upstream BSD-3-Clause licence](UPSTREAM-LICENSE)

## Source and result

Upstream: [neuroinformatics-unit/movement](https://github.com/neuroinformatics-unit/movement), revision `39ee15e29706150d7d4f60ba617aa99d2027eed7`. The patch changes only `movement/filtering.py` and adds `tests/test_unit/test_filtering_edited.py`. Implementation branch: `feat/explicit-edit-filtering`, maintained in a separate upstream worktree.

97 targeted tests passed: 15 new acceptance cases and 82 existing synthetic filtering cases. Native save/reload, lint, formatting, spelling, and targeted type checks passed. The two SLEAP recording-dependent cases, full repository suite, GUI verification, and researcher validation remain unrun. The full pinned pre-commit pipeline has also passed on both changed files, including manifest validation.

## Continue locally

Apply the patch to the pinned upstream revision in an isolated feature worktree; follow the upstream contribution instructions and the pilot's environment/setup commands. Do not execute a fresh remote main in place of the recorded baseline without refreshing the comparison.

Keep the upstream source tree, virtual environment, caches, and generated data outside this repository. The lab stores the contribution and its evidence, not a separately maintained fork of the whole toolbox. Retain the upstream licence with this artifact.

The implementation diff was approved for continuation. No commit, push, upstream PR, or maintainer outreach has occurred. Publication still follows the full-diff, contribution-record, and exact-commit approval process.
