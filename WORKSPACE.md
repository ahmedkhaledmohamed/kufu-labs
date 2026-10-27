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

Ahmed requested merging all currently open lab PRs. PR #3 is the remaining one; GitHub reports a WORKSPACE conflict after the hub merge. Prepared resolution `6d79e5ce799ec484c25b33a7800608d723d9cacd` on `fix/reconcile-diagnostic-pr` preserves the current hub handoff and diagnostic files. That resolution is incorporated into the delivery branch locally. It has not been pushed or merged remotely; its changed exact commit still requires the full-diff approval required by AGENTS.md.

The delivery implementation is local pending its own complete-diff/contribution-record/exact-commit approval. Once authorised, push PR #3's resolution, merge that existing PR, submit the delivery PR, verify actual GitHub CI, and obtain explicit merge authorisation for that resulting PR unless Ahmed supplies it with the exact-snapshot review. Production deployment is already authorised; the pipeline must release only tested current main. Do not bypass this chain with a manual deployment.

## Actual verification versus remaining work

Local multi-page/browser checks pass: five distinct URLs, current navigation state, 25 problems, 15 source boards, four exploration entries, two runnable demonstration entries, compound filters/reset, cross-page deep links/source navigation, separate pose-demo tab and mobile layout. The real movement widget/model replay again passes its eleven invariants while retaining deletion-flag loss as an unfixed negative finding. The full frozen-pose browser boundary checks also pass.

The Vercel project exists in verified personal scope `ahmed-khaled-mohameds-projects`; Authentication covers all deployments including production. A 90-day project-scoped deployment token and project-specific verification credential are stored in encrypted GitHub Secrets; no values are committed or printed. Automatic Git connection is disabled to preserve the CI deployment gate. No site has been deployed by this branch yet.

Remaining gates: full local checks and review snapshot; exact-commit approvals; actual PR/CI runs; explicitly authorised merge; main pipeline deployment and promotion; verify the protected production alias and artifact identity. Keep the goal active until those cloud/runtime requirements are proved. A successful local test is not completion of CI/CD.

## Validation discipline

A runnable browser or ephemeral CI example establishes execution. Pinned host checks establish only the tested integration semantics. Resolving the original researcher problem requires the stated workflow outcome evidence. No adoption, researcher time saving, biological correctness or full upstream resolution is claimed. The next scientific feature candidate remains read-only host-native SLEAP instance/skeleton/score mapping, not a generic hosted code runner.
