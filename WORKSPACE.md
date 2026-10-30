# Kufu Labs workspace

## Current task

PR #22 is merged at `cad3a223ef36bf64d06d6f3d3fc36c23a799bc23`. All four jobs passed in [main run 41061466521](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41061466521). Independent authenticated reads matched production's manifest and seven NWB implementation/result assets to the tested artifact. The deployment gate's real experiment `11d913b3-d62b-46a7-8568-65ec70f84913` completed with its Sandbox stopped. The public Inspector 0.7.2 and existing development profiles are now CI-covered; the hosted lab still uses its documented development pin.

The current continuation on `fix/movement-deletion-provenance` implements an independent local candidate for [movement #1174](https://github.com/neuroinformatics-unit/movement/issues/1174). On current upstream `00e7a232c90ac451e27b1a72f41e7234878d0417`, six new deletion-round-trip cases fail before the patch and all 15 cases pass after it. All 45 existing conversion cases also passed in Linux CPU Mesa/Xvfb. The candidate preserves loaded flags only for currently missing points; it retains current live flags, never-detected controls and existing coordinate-drop behaviour. The original filtering patch is unchanged.

Another contributor reported the same repair approach in #1174 on 29 October, before this local candidate. No linked code was available for assessment. Retain independent regression evidence and check that contribution before any separately authorised upstream discussion; do not publish a competing upstream PR. See the [source pin, implementation, commands and limits](projects/movement-edit-filtering/DELETION-PROVENANCE.md).

The separate patch, CI addition and problem-page update are local and await exact-diff approval before publication. Native round trips compare all positions, confidence and edit flags over up to four reopen cycles. The normal macOS Qt test run crashed at viewer startup; the full 45-case conversion check passed in Linux. Full host suite, real recordings, rendered deletion gestures, reset/re-add UI, researcher benefit and upstream acceptance are unverified. The next useful task is comparing independent tests with an accessible upstream candidate; no outreach is authorised.

No outreach, spending, new accounts, research recordings or model weights. Preserve existing research worktrees. Show the exact full diff and contribution record before a personal-repository push or PR; merging requires a separate explicit instruction. Wait for CI/CD after an authorised merge; do not deploy manually.

## Entry points

- [Home](index.html): meaning, purpose and the practical-ingenuity figure.
- [Execution lab](lab.html): real queued NWB experiments, progress, comparisons and downloads.
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
