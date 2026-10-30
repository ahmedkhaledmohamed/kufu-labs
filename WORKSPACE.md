# Kufu Labs workspace

## Current task

PR #21 is merged at `24bb3adeae8a35d29e04f40c63fa4dbfbb8cd1d8`. All four required jobs passed in [main run 40990877466](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40990877466). The tested artifact was promoted to protected production. Independent authenticated reads matched its manifest and seven movement/page assets; anonymous access still returns a protection redirect. The deployment gate's real experiment `ad69c262-1995-4ba7-824b-d4c05fb7b232` completed with its Sandbox stopped.

The actual movement rendered edit → save → reload → filter workflow now runs in required CI. It uses napari/PyQt6 with CPU Mesa/Xvfb and constructed poses, with the unchanged filtering patch and 11 original invariants. Native canvas captures show the correction retained and the unedited unscored point removed. The repeated-export deletion-flag defect remains explicit and unfixed. See the [host record and captures](projects/movement-edit-filtering/README.md#rendered-host-workflow).

The current continuation on `feat/nwb-released-version-validation` tests NWB Inspector's public 0.7.2 release, rather than only the existing 0.7.3 development pin. Python 3.12.12, PyNWB 4.2.0 and HDMF 6.2.0 reproduce the reported stack at the documented granularity. Across both storage backends, iterator types and three lengths, all 12 inspected baseline cases lose values; all 12 patched cases and all uninspected controls preserve every value. Source and patch hashes are checked before execution.

The released unit suite has three pre-existing dependency failures on both revisions: 278 baseline tests pass, 289 patched tests pass, and 5 skip in each. A differential runner retains and checks those exact failures and collection counts. The CI addition and [released profile/results](projects/nwb-stream-integrity/README.md#released-version-comparison) are local, pending exact-diff approval and publication. The hosted execution lab remains on the documented development pin. The next decision is whether the bounded patch or the existing dependency PR should be preferred before any separately authorised upstream discussion; no researcher benefit or upstream acceptance is claimed.

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
