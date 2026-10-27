# Scientific software lab workspace

## Entry points

| Focus | Read first |
| --- | --- |
| Continue the movement contribution | [Project status](projects/movement-edit-filtering/README.md), then [pilot and results](projects/movement-edit-filtering/PILOT.md) |
| Explore a new problem | [Research record](research/opportunity-discovery/README.md) and [existing-tool audit](research/opportunity-discovery/AUDIT.md) |
| Reconsider priorities | [Investigation plan](research/opportunity-discovery/PLAN.md) |

Read only the selected task and its applicable instructions. Refresh mutable issue, PR, and upstream revision information before relying on it. Keep working implementation checkouts separate from the lab repository.

## Current status

The approved movement patch passes 97 targeted synthetic cases, including native netCDF save/reload. The full pinned upstream pre-commit pipeline also passes. The audit compared three scientific domains and selected this specific upstream gap. Runtime success does not establish scientific utility or adoption.

Research and pilot artifacts were prepared for migration from Personal on 26 October 2026. [The manifest](migration-manifest.json) maps all six source files and their original hashes. Source copies remain in Personal until the destination has been published, verified, and linked from the old entry point. Personal PR #228 preserves the initial research snapshot; it has not been merged by this migration.

## Next actions

1. Review the lab's complete initial contents and repository bootstrap plan before publication.
2. Publish the reviewed migration through a feature branch and PR; leave merging to Ahmed.
3. Replace the old Personal research entry with a destination link through a separate reviewed change after destination verification.
4. Complete remaining movement host checks and decide whether to seek upstream review. Outreach, a fork push, and an upstream PR need their applicable authorisation.
5. Validate a real researcher workflow before claiming practical benefit; otherwise retain the pilot as a technical result.
