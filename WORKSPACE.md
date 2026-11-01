# Kufu Labs workspace

## Current task

PR #28 is merged at `80fe8e9550e9828f8fe61edf2a5a9855f6bea376`. Its preview passed all four required checks, including the real rendered deletion replay. Main run [41160760475](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41160760475) passed scientific contracts, refine.bio and browser verification; deployed browser checks passed, but hosted scientific verification stopped at the shared daily submission limit (HTTP 429). Explicit promotion did not run. An authenticated canonical manifest read still reports `49c92d28e38c872116b6c407403ba155e34a91f8`. No manual deployment or quota reset was performed.

The continuation is `feat/ci-reliability`. The previous successful main run [41156016312](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41156016312) spent about ten minutes in Node setup and reported “Failed to restore: Egress is over the account limit.” Both Node setup steps now explicitly disable optional package-manager caching. Locked installs, public registry configuration and all required checks remain unchanged. Cloud verification remains pending publication; this change cannot establish that the cache service itself has recovered.

CI currently shares the ten-submission UTC daily allowance with ordinary experiments. A separate capped CI allowance is a pending policy choice; no budget or identity change is implemented here. Owner ID and session secret are provisioned in production/preview; Vercel App client settings are still absent, so live owner sign-in remains disabled.

The merged deletion replay establishes constructed-input Qt click/Delete and two native save/load round trips. Reset/re-add gestures, full host suite, real recordings and researcher benefit remain unverified. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees and licences. Any push/PR requires approval of the exact diff; merge is separately authorised per PR.

## Entry points

- [Home](index.html): meaning, purpose and the practical-ingenuity figure.
- [Execution lab](lab.html): explicit NWB/MNE experiment selection, progress, comparisons and downloads.
- [Problems](problems.html): the main directory; each problem has its own explanation, solution, runtime and validation.
- [Explorations](explorations.html): compatibility index linking to implemented problem pages.
- [Sources](sources.html): discovery boards and their limits. [Validation](validation.html) remains a compatibility index.
- [Delivery](site/DELIVERY.md): CI/CD, artifact identity and protected deployment.
- [Licensing](README.md#licensing): default MIT terms and preserved GPL/BSD exceptions.

## Earlier verified baseline

Main `10b5e2c139adc693f774792b41ffa85bacd37b69` includes merged PRs #1–#9. Run 40577617957 passed scientific, build/browser and protected Vercel deployment checks. The site is live at the existing protected production URL; its source and sampled asset hashes match the exact CI artifact. Independent desktop/mobile checks passed the inspector navigation, comparison, 182 local links and blocked unauthenticated requests. The earlier deployment goal is complete.

## Release state and remaining work

PR #10 merged at `1fb72e3f81dc6184e1d7a40cf9871808b69419cb`. Main run 40598637899 passed all three jobs, promoted the tested Kufu site, and passed an independent production audit. Public repository and license access were verified anonymously. The earlier standalone Home proposal is superseded by the released Kufu meaning/purpose/figure page.

No outreach, new accounts, spending, recordings or model-weight downloads are authorised. Preserve existing research worktrees and project/upstream licence notices.

## Scientific claims

The pose inspector uses constructed inputs and unchanged upstream filtering. The published browser demo is separate from the locally verified experimental SLEAP source adapter. The movement patch addresses a local filtering subproblem; a separate deletion-provenance candidate now has local regression coverage, without upstream acceptance. Researcher benefit, adoption and end-to-end problem resolution remain unmeasured.
