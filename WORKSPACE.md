# Kufu Labs workspace

## Current task

PR #25 is merged at `bca3bab8d0e23f225b0eec554c2a3d33872391e4`. Its [preview run 41083618486](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41083618486) passed all four jobs. Actual queued NWB and MNE runs completed with stopped Sandboxes and verified downloads. The MNE 512 Hz case reproduced onset rounding and floor-index displacement; the candidate preserved both, and the 1000 Hz UTC control was unchanged in both revisions. Production CI [41086509994](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41086509994) passed scientific, refine.bio and web checks, then stopped at the hosted gate with HTTP 429 because the shared daily submission budget was exhausted. It did not promote production. Rerun the failed deployment job after the UTC-day reset; preserve the existing limits and reviewed deployment path.

The current continuation on `feat/execution-validation` verifies the contents of the existing downloadable results. The earlier hosted gate checked the archive hash and API summary but did not independently inspect the exported arrays. The new standard-library checker reads the two supported numeric NPY formats without extracting files or loading scientific packages. It checks report/API and source identities, array hashes, shapes and dtypes, identical comparison inputs, MNE unchanged-signal claims, and NWB changed-value/row counts calculated from the actual exported bytes.

Local checks accept four real parameterized cases per recipe and reject altered arrays, unsupported dtypes, mismatched source records and output counts/controls that the report and API falsely agree on. The deployed gate will retain the downloaded ZIPs and verification receipts in the existing CI artifact. It reuses the two existing hosted jobs; no additional experiment, integration or compute allocation is introduced. The new checker also passed locally against both actual successful PR #25 Vercel downloads (two cases per recipe), read without launching another job. CI integration of this check remains pending reviewed publication.

The work is local and awaits exact-diff approval before publication. It validates exported software evidence, not biological accuracy, physical-clock accuracy, researcher benefit or upstream acceptance. Existing scientific patches are unchanged. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees. Show the exact diff and contribution record before a personal-repository push or PR, and obtain a separate explicit instruction before merging.

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
