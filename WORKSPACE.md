# Kufu Labs workspace

## Current task

PR #26 is merged at `49c92d28e38c872116b6c407403ba155e34a91f8`; all required preview checks passed. Production run [41156016312](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41156016312) passed all four jobs and promoted the tested release. Its ten-minute Node-setup delay recovered without bypass or manual deployment. Independent production reads match the tested manifest, matrix summary, runner and EEG problem page. Both actual hosted experiments completed with stopped Sandboxes and verified downloaded-array receipts; anonymous access remains protected. No open PRs remain.

The new continuation is `feat/deletion-gui-validation`. It leaves the existing movement deletion patch unchanged and adds a rendered path to its verifier. A real Qt canvas click and Delete key remove the intended point; real Save/Load buttons export/reopen native netCDF twice. Baseline loses the deletion flag on its second save and the final loader reads false; the candidate preserves true through both saves and final loading. Positions/confidence/time, unscored and never-detected controls, and the original dataset are checked. The other contributor's existing repair proposal remains credited; no competing patch or upstream message is prepared.

Both local runs passed in the cached Linux arm64 CPU-Mesa image, with networking disabled, two CPUs and a three-GiB container limit. The first container launch stalled before Python started and was stopped; retained successful runs use an init process. Each measured replay took about 8–9 seconds, with peak RSS below 850 MiB and less than 34 KB of native fixtures. Captures and source-locked JSON results are retained. The problem page derives its actual before/after flags from those reports and verifies capture hashes; it launches no Qt application or scientific job.

The proposed CI addition runs both rendered replays in the existing scientific job and publishes fresh captures/results. No dependency, provider, quota or scientific-source change is added. Local checks and exact-diff review precede publication; rendered CI has not run yet. Reset/re-add gestures, full host suite, real recordings and researcher benefit remain unverified.

Owner ID and session secret are provisioned in production/preview; Vercel App client settings are still absent, so live owner sign-in remains disabled. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees and licences. Any push/PR requires approval of the exact diff; merge is separately authorised per PR.

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
