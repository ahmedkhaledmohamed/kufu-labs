# Scientific software lab workspace

## Entry points

| Focus | Read first |
| --- | --- |
| Continue the movement contribution | [Project status](projects/movement-edit-filtering/README.md), then [pilot and results](projects/movement-edit-filtering/PILOT.md) |
| Explore a new problem | [Research record](research/opportunity-discovery/README.md) and [existing-tool audit](research/opportunity-discovery/AUDIT.md) |
| Reconsider priorities | [Investigation plan](research/opportunity-discovery/PLAN.md) |

Read only the selected task and its applicable instructions. Refresh mutable issue, PR, and upstream revision information before relying on it. Keep working implementation checkouts separate from the lab repository.

## Current status

Private lab [migration PR #1](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/1) is open at the approved 15-file snapshot. The initial README-only main bootstrap is preserved. Original Personal copies remain until the destination migration is merged and a reviewed pointer change replaces the old entry. The migration manifest is an immutable record of that approved snapshot, not a checksum claim for later edited project documents.

The approved movement patch is unchanged. Its earlier 97 targeted synthetic cases and full pinned pre-commit results were reused. A new fresh-worktree demonstration now passes the real Qt-widget/model-event load → edit/remove → save → reload → filter boundary; four existing pose-conversion cases also pass. No canvas or mouse gestures were tested. See the [review package](projects/movement-edit-filtering/REVIEW.md) for evidence and the observed loss of deleted-point flags on second export.

## Working handoff

Local branch: `research/movement-workflow-verification`, isolated worktree `scientific-software-lab-workflow`. It began from main while migration PR #1 was pending, with the approved migration tree overlaid for local work. The new review-package changes remain uncommitted and unpushed; compare them against `research/lab-migration`, not against the README-only bootstrap.

A second pinned movement worktree, `movement-workflow-replay`, was created from upstream main at the audited revision and received the exact approved patch. The verifier imports that source explicitly and checks its baseline/patch before execution. The original approved implementation worktree and published migration snapshot remain intact.

## Next actions and boundaries

1. Review the unpublished package, executable demonstration, result, and upstream PR draft. A maintainer can assess API scope and coordinate semantics; no maintainer has been contacted.
2. After Ahmed merges migration PR #1, refresh main and base a new publication branch on it, carrying only the review-package delta. Follow full-diff, contribution-record, and exact-commit approval before any push or PR.
3. Seek separately authorised upstream design review; do not claim #1027 is fully addressed. Consider a separate report for deletion-provenance loss if maintainers want one.
4. Full host CI, rendered GUI interaction, recording-dependent tests, and researcher validation remain future gates. Do not download recordings or expand scope merely to turn these into passing claims.
5. Replace the Personal entry with a reviewed destination pointer only after migration verification/merge. No merge, outreach, paid service, account/fork creation, or new publication is authorised by the autonomous verification goal.
