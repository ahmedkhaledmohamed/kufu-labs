# Kufu Labs workspace

## Current task

PR #24 is merged at `105f59fe670e715817d850c6670ba8e82f878016`. All four jobs passed in [main run 41075662488](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41075662488). Production's manifest and seven sampled assets match the tested artifact, anonymous access remains protected, and its actual deployment experiment completed with the Sandbox stopped. The MNE interior-onset candidate is now maintained alongside the earlier investigations. It remains a bounded local software contribution, without MNE upstream submission or researcher validation.

The current continuation on `feat/mne-execution-lab` adds MNE as a second explicitly selected experiment in the existing Execution lab. Users can edit rate/sample/origin, generate four reference rates, and view timestamp/index comparisons with original-signal and input-annotation controls. Both recipes reuse the same worker, progress and private-download path; old NWB requests remain supported. No new provider, credentials, recording upload or arbitrary-code path is added. Existing four-case, four-minute and ten-per-day shared limits remain.

The actual parameterized MNE driver passes four reference and four boundary cases locally. API/executor checks cover recipe validation, cross-recipe idempotency conflicts, legacy requests and cleanup even after failed commands or progress writes. Browser checks use local API doubles with real Python reports; the new deployment gate will also submit actual MNE failure/control cases and verify stopped compute and download hashes. Hosted MNE verification is pending publication; the current production execution lab still offers NWB only.

The work is local and awaits exact-diff approval before publication. The approved MNE source patch is unchanged. Sampling offset stays zero, duration 100 ms and signals are constructed ramps. No general timing, physical-clock, biological-correctness, full-suite, real-recording, user-benefit or upstream-acceptance claim is added. MNE's personal human-review policy remains applicable before any separately authorised upstream contribution. See the [parameterized record](projects/mne-annotation-onsets/README.md#parameterized-execution-lab).

No outreach, spending, new accounts, research recordings or model weights. Preserve existing research worktrees. Show the exact full diff and contribution record before a personal-repository push or PR; merging requires a separate explicit instruction. Wait for CI/CD after an authorised merge; do not deploy manually.

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
