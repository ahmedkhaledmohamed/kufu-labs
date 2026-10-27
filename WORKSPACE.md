# Scientific software lab workspace

## Entry points

| Focus | Read first |
| --- | --- |
| Continue the movement contribution | [Project status](projects/movement-edit-filtering/README.md), then [pilot and results](projects/movement-edit-filtering/PILOT.md) |
| Explore a new problem | [Research record](research/opportunity-discovery/README.md) and [existing-tool audit](research/opportunity-discovery/AUDIT.md) |
| Reconsider priorities | [Investigation plan](research/opportunity-discovery/PLAN.md) |

Read only the selected task and its applicable instructions. Refresh mutable issue, PR, and upstream revision information before relying on it. Keep working implementation checkouts separate from the lab repository.

## Current status

Private lab [migration PR #1](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/1) and [verification PR #2](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/2) are merged. Main was verified at `78375803a4326b2a26d725568bea84b95a169e35` with all 18 reviewed files. The migration manifest records the original approved snapshot, not later document revisions.

Superseded [Personal PR #228](https://github.com/ahmedkhaledmohamed/Personal/pull/228) is closed without merge or branch deletion. [Personal PR #229](https://github.com/ahmedkhaledmohamed/Personal/pull/229) adds the single project-index link and remains open. The modified original Personal research worktree is preserved.

The explicitly approved [public design question](https://github.com/neuroinformatics-unit/movement/issues/1027#issuecomment-6431299925) has been posted from the personal GitHub account. It asks about the optional edit mask and coordinate policy without publishing the patch or linking private lab contents. Maintainer acceptance and researcher benefit have not been established.

The approved movement patch is unchanged. Its earlier 97 targeted synthetic cases and full pinned pre-commit results were reused. A new fresh-worktree demonstration now passes the real Qt-widget/model-event load → edit/remove → save → reload → filter boundary; four existing pose-conversion cases also pass. No canvas or mouse gestures were tested. See the [review package](projects/movement-edit-filtering/REVIEW.md) for evidence and the observed loss of deleted-point flags on second export.

## Working handoff

Local follow-up branch: `docs/maintainer-review-status`, isolated worktree `scientific-lab-maintainer-status`, created from merged main. This status update is an uncommitted local draft and has not been pushed. The clean lab checkout is `scientific-software-lab`; the two completed, clean lab publication worktrees were removed after their commits merged.

A second pinned movement worktree, `movement-workflow-replay`, was created from upstream main at the audited revision and received the exact approved patch. The verifier imports that source explicitly and checks its baseline/patch before execution. The original approved implementation worktree and published migration snapshot remain intact.

## Independent deletion-provenance investigation

A clean, unmodified upstream worktree (`movement-deletion-provenance`) at the audited revision now reproduces the loss without Qt, file IO, or the filtering patch. Deletion-only data lose the entire `edited` variable on the second conversion; mixed deletion/move data retain the variable but lose the deletion flag. A never-detected point remains correctly unedited. Positions and confidence are unchanged.

The [diagnostic/report draft](projects/movement-edit-filtering/DELETION-PROVENANCE.md), executable three-case reproducer, and observed result remain local on this follow-up branch. The exact standalone snippet was also executed successfully. No repair has been implemented or further upstream contact made. Initial searches found the original closed issue #1047 and PR #1057, plus the loaded-baseline discussion in PR #1137; no specific repeat-conversion fix was identified.

## Next actions and boundaries

1. Check the linked upstream discussion before deciding the next implementation step; do not treat the posted question as design acceptance or an upstream PR.
2. Leave Personal PR #229 open until Ahmed explicitly authorises its merge. Preserve the original research worktree and superseded remote branch.
3. If maintainers want the contribution, review their requested API/coordinate semantics and prepare the smallest appropriate upstream PR. A public fork, patch push, upstream PR, or additional outreach requires the applicable explicit authorisation.
4. Full host CI, rendered GUI interaction, recording-dependent tests, and researcher validation remain future gates. Keep deletion-provenance loss separate unless scope is explicitly expanded.
5. Follow full-diff, contribution-record, and exact-commit approval before publishing this local status update or further code. Do not infer permission for merges, spending, or additional contact from the completed three-action approval.
