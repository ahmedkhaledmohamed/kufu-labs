# Kufu Labs workspace

## Current task

PR #20 is merged at `c212493aad24fedc9c762d86ace6b06880e8c7d8`. All four required jobs passed in [main run 40886268226](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40886268226), which promoted the tested site to the protected production URL. Independent authenticated reads matched the production manifest and seven implementation/demo assets to that artifact; an unauthenticated walkthrough request remained blocked. The production browser check passed 557 local links. Its real queued experiment `6bf03105-2fd0-4512-8dc6-2a3642d64c4a` completed with compute stopped. The [SLEAP adapter and recording](projects/overlap-inspector/sleap-adapter/README.md) are published; researcher usefulness and upstream acceptance remain unverified.

The current continuation is a rendered movement edit → save → reload → filter verification on isolated branch `feat/movement-rendered-verification`. The actual CPU Mesa/Xvfb canvas replay now passes: a Qt pointer drag moves the selected point to x=100/y=200, native save/reload preserves the edit, and a filtered reload visibly retains the correction while removing the unedited unscored point. The unchanged approved filtering patch and 11 original workflow invariants remain enforced. The repeated-export deletion-flag defect still reproduces and remains explicit. See the [host record and captures](projects/movement-edit-filtering/README.md#rendered-host-workflow).

The replay uses the actual napari 0.9.2/PyQt6 host with CPU Mesa/Xvfb and constructed poses. Its Qt pointer events explicitly retain the held button, and navigation uses world-frame coordinates so the captured slice is the tested frame. The verifier rejects missed clicks, wrong visible point counts and non-software rendering. No direct point mutation substitutes for the rendered drag. The run completed with networking disabled and CPU/memory limits enforced; measurements are retained in rendered-result.json.

The follow-up adds the replay and fresh captures/results to the existing required CI check. Local rendered and model-only verification, Ruff/formatting, CI YAML parsing, packaging and desktop/mobile browser checks passed. The site check covers 27 problem pages and 561 local links. A cloud result is not claimed before publication. Current movement upstream was reviewed at `00e7a232c90ac451e27b1a72f41e7234878d0417`; the replay remains pinned to `39ee15e29706150d7d4f60ba617aa99d2027eed7`. No API/schema expansion or new outreach is included.

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

The pose inspector uses constructed inputs and unchanged upstream filtering. The published browser demo is separate from the locally verified experimental SLEAP source adapter. The movement patch addresses a local filtering subproblem; repeated-export deletion provenance remains an unfixed finding. Researcher benefit, adoption and end-to-end problem resolution remain unmeasured.
