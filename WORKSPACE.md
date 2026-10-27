# Kufu Labs workspace

## Current task

Prepare Kufu Labs for a renamed public GitHub repository, with explicit licensing and a Home page that explains the lab rather than duplicating its navigation. The selected name is Kufu Labs, from Japanese 工夫 (kufū), practical ingenuity. The repository has been renamed to `ahmedkhaledmohamed/kufu-labs` and remains private. Required main-branch checks and admin enforcement were verified after the rename.

## Entry points

- [Home](index.html): meaning, purpose and the practical-ingenuity figure.
- [Explorations](explorations.html): project implementations, runnable examples and limits.
- [Problems](problems.html), [sources](sources.html) and [validation](validation.html): the evidence catalogue and outcome assessment.
- [Delivery](site/DELIVERY.md): CI/CD, artifact identity and protected deployment.
- [Licensing](README.md#licensing): default MIT terms and preserved GPL/BSD exceptions.

## Verified baseline

Main `10b5e2c139adc693f774792b41ffa85bacd37b69` includes merged PRs #1–#9. Run 40577617957 passed scientific, build/browser and protected Vercel deployment checks. The site is live at the existing protected production URL; its source and sampled asset hashes match the exact CI artifact. Independent desktop/mobile checks passed the inspector navigation, comparison, 182 local links and blocked unauthenticated requests. The earlier deployment goal is complete.

## Public-release preparation

The isolated `feat/public-lab-preparation` worktree started from that refreshed baseline. A pattern scan of 22 reachable commits/144 blobs, all 11 Actions logs and PR discussion records found no matches to the checked credential, internal-host or private-path patterns. This is a bounded pattern audit, not a guarantee against every secret format. No raw logs or secret values are committed.

The intended public release retains existing project licences, upstream notices, scientific source pins and unchanged numerical behaviour. GitHub Actions history/artifacts follow repository visibility. The Vercel project ID, owner and authentication remain unchanged; making the repository public does not remove site protection.

The earlier `feat/home-lab-overview` draft is superseded by this Kufu meaning/purpose/figure Home; do not publish that draft.

Remaining steps: finish local checks and exact-diff/commit review; publish and merge through a PR with successful checks; verify the Kufu production branding and Home; audit the final publication state; change the authorised repository visibility and confirm unauthenticated GitHub access. Preserve earlier research worktrees. No outreach, new accounts, spending, recordings or model-weight downloads are authorised.

## Scientific claims

The pose inspector uses constructed inputs and unchanged upstream filtering. It is not yet integrated into SLEAP. The movement patch addresses a local filtering subproblem; repeated-export deletion provenance remains an unfixed finding. Researcher benefit, adoption and end-to-end problem resolution remain unmeasured.
