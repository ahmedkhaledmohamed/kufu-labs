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

PR #4 is merged at main `902dd4ccea229bac16e110ef1fad8b5b72bcfa8e`. The delivery branch `feat/lab-pages-and-delivery` started from that refreshed main in isolated worktree `scientific-lab-delivery`. Existing source checkouts and draft research worktrees are preserved.

PR #3 is merged at `ee2f51fcebb363dc8b3eb8125dcbd688649cc847`, including the approved conflict resolution `6d79e5ce799ec484c25b33a7800608d723d9cacd`. [Delivery PR #5](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/5) is open at the originally approved `2751a4e34bb9445b09b59a422459f7c460c635b2` snapshot.

The [first cloud run](https://github.com/ahmedkhaledmohamed/scientific-software-lab/actions/runs/40511509142) passed the Linux scientific and browser jobs. Deployment stopped before uploading because a fresh Vercel CLI profile tried to read user metadata with a project-only token. A local fix supplies only the already verified team mapping in a temporary private CLI profile; the actual changed helper passed with a fresh ten-minute project-only credential. No broader credential permissions or protection changes were needed. The fix is local pending renewed exact-commit approval; do not push a changed commit under the previous approval.

After the approved update, rerun actual cloud CI, inspect the protected preview, merge PR #5 only with the applicable explicit authorisation and successful checks, then wait for main's tested production promotion and verify the production alias. Production deployment remains authorised, but not a shortcut around the CI gate.

## Actual verification versus remaining work

Local multi-page/browser checks pass: five distinct URLs, current navigation state, 25 problems, 15 source boards, four exploration entries, two runnable demonstration entries, compound filters/reset, cross-page deep links/source navigation, separate pose-demo tab and mobile layout. The real movement widget/model replay again passes its eleven invariants while retaining deletion-flag loss as an unfixed negative finding. The full frozen-pose browser boundary checks also pass.

The Vercel project exists in verified personal scope `ahmed-khaled-mohameds-projects`; Authentication covers all deployments including production. A 90-day project-scoped deployment token and project-specific verification credential are stored in encrypted GitHub Secrets; no values are committed or printed. Automatic Git connection is disabled to preserve the CI deployment gate. No site has been deployed by this branch yet.

Remaining gates: exact-commit approval for the CLI fix; updated PR/CI and protected-preview verification; explicitly authorised merge; main pipeline deployment and promotion; verify the protected production alias and artifact identity. Keep the goal active until those cloud/runtime requirements are proved. A successful local test is not completion of CI/CD.

## Validation discipline

A runnable browser or ephemeral CI example establishes execution. Pinned host checks establish only the tested integration semantics. Resolving the original researcher problem requires the stated workflow outcome evidence. No adoption, researcher time saving, biological correctness or full upstream resolution is claimed. The next scientific feature candidate remains read-only host-native SLEAP instance/skeleton/score mapping, not a generic hosted code runner.
