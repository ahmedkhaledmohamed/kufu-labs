# Scientific software lab workspace

## Active goal

Deliver independent navigation pages, meaningful CI/CD, runnable demonstrations and protected Vercel production for the scientific-software lab. The approved production target is Ahmed's personal Vercel scope; outreach, new accounts, paid add-ons, model weights and research recordings remain outside this goal.

## Entry points

| Task | Entry |
| --- | --- |
| Browse the lab | [Home](index.html), [explorations/demos](explorations.html), [problems](problems.html), [sources](sources.html), [validation](validation.html) |
| Build, run and deploy | [Delivery guide](site/DELIVERY.md), [hub maintenance](site/README.md) |
| Verify the pose inspector | [Project record](projects/overlap-inspector/README.md) and its pinned oracle generator |
| Verify movement filtering | [Project](projects/movement-edit-filtering/README.md), [widget replay](projects/movement-edit-filtering/verify_workflow.py), [negative deletion reproduction](projects/movement-edit-filtering/DELETION-PROVENANCE.md) |
| Evaluate resolution claims | [Validation review](site/VALIDATION.md) and the website's separate execution/integration/problem-resolution descriptions |

## Source and publication state

PRs #3–#6 are merged; no lab PR remains open at this checkpoint. Current main is `f08e1f007cfb009afab2d94497539025038506d3`. The isolated `fix/project-scoped-promotion` branch starts from that refreshed commit. Existing source checkouts and draft research worktrees are preserved.

Main run [40570051300](https://github.com/ahmedkhaledmohamed/scientific-software-lab/actions/runs/40570051300) passed scientific contracts, build/local browser checks and deployed browser checks, then failed during `vercel promote`: its user lookup is unavailable to the project-scoped token. Vercel's generated alias was assigned despite `autoAssignCustomDomains: false`; explicit promotion and production-target state were not completed. Authentication remains enabled for all deployments. Do not claim a completed production release or guaranteed absence of generated aliases before promotion.

## Actual verification versus remaining work

Five independent pages, 25 problems, 15 source boards, four exploration entries, two demonstration entries, 16 research pages and 180 local links passed both local and deployed browser checks on merged main. The source-navigation load regression passed. The actual pinned scientific checks also passed; deletion-flag loss remains an unfixed negative finding.

The focused fix replaces only the high-level promotion command with Vercel's documented project API. It verifies deployment ownership/source/state, waits for that exact promotion to succeed and retains post-promotion browser/artifact/protection checks. Eight isolated simulated helper scenarios passed, including failure and timeout cases. No actual promotion with the changed helper has occurred.

Remaining gates: review the full exact diff and approve publication; open the fix PR; inspect cloud checks; explicitly authorised merge; wait for main CI to promote; independently verify source/asset identity, navigation/demos and blocked unauthenticated access on the production alias. Keep the existing goal unfinished until those actual requirements pass. No credential broadening, manual deployment, outreach or recordings are needed.

## Validation discipline

A runnable browser or ephemeral CI example establishes execution. Pinned host checks establish only the tested integration semantics. Resolving the original researcher problem requires the stated workflow outcome evidence. No adoption, researcher time saving, biological correctness or full upstream resolution is claimed. The next scientific feature candidate remains read-only host-native SLEAP instance/skeleton/score mapping, not a generic hosted code runner.

## Continuation authority

Ahmed asked future authorised goals to continue without additional goal-approval pauses. Repository publication instructions still require exact-diff/exact-commit approval and an explicitly authorised merge. The earlier navigation fix was approved and merged; that approval does not cover this new promotion fix. Prepare the reviewable change before requesting the final publication approval. Preserve boundaries around outreach, spending, new accounts and data access.
