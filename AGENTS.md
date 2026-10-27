# Scientific software lab instructions

## Task scope

Start with WORKSPACE.md and the selected project's record. Keep sourced observations, proposed work, experimental results, and unresolved questions distinct. Prefer an established tool's missing capability over duplicating its broad purpose.

Keep project dependencies and environments local to that project. Do not add a monorepo build framework merely to hold multiple investigations. Upstream patches belong with their pinned source revision and reproducibility record; keep upstream implementation worktrees separate.

## Scientific evidence

Record dataset, model, software, and baseline revisions independently. Verify each licence and access route before reuse. Preserve sample grouping and timestamp assumptions; do not equate a passing software test or benchmark with biological correctness, clinical utility, or user benefit.

Use constructed fixtures or permitted public data for initial pilots. Do not commit patient information, recordings, model weights, environment directories, or secrets. Label predictions and human annotations by their actual source.

## Git and publication

Use the personal GitHub account and personal author/committer identity required by the global instructions. Work in an isolated feature worktree from current main. Show the full diff and contribution record, obtain explicit approval, and mark the exact commit before any push or PR. Follow the global thinking-trail process; never store raw conversation extracts here.

Keep PRs open until Ahmed merges or explicitly instructs a merge. Do not contact maintainers or research participants, spend money, register accounts, or publish research data without the applicable explicit authorisation.

## Verification and handoff

Use the host project's required checks and meaningful tests for the selected change. Record commands, exact inputs and versions, results, resource measurements, and tests not run. Update the existing project record with the next step and remaining approval boundary.
