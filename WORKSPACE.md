# Kufu Labs workspace

## Current task

PR #32 merged at `a1707967766bfcb07e62d7366a905c4952d5a39c`. [Main run 41352041534](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41352041534) passed and deployed the protected production site. Independent checks verified production wheel bytes, GitHub-authenticated CI receipts, native NWB/MNE artifacts and stopped Sandbox compute. CI now uses its separate twenty-submission UTC daily pool; the existing ordinary ten and owner exemption remain unchanged.

The approved continuation is `feat/ecephys-conversion-workflow`: a runnable PyNWB ElectricalSeries conversion using installed baseline/repaired wheels and generated electrode patterns. Twelve separate-process HDF5 round trips cover 0.5, 16 and 128 MiB arrays, with inspected and uninspected controls. Every repaired/control value is preserved. Inspected baseline conversions change 12,288 rows while electrode links, voltage factors, timing and file schema remain correct. Baseline Inspector ERROR messages remain explicit. Full installed-package identities are verified, network connections blocked and larger generated files removed after readback.

The project README, runnable example, result record and problem-page walkthrough explain the science and tested behavior. CI repeats the comparison and packages four small constructed NWB files for a hash-checked download. Memory measurements are reported without a constant-memory claim. The full electrode conversion runs in Python; the hosted generic stream recipe is unchanged. Real recordings, biological validity, researcher benefit and upstream acceptance remain untested. Exact-diff approval is required before push/PR; merge is separately authorised.

Local verification passed: all 12 scientific conversions, the standalone user command without the full manifest, Ruff 0.16.10, site lint/build, desktop/mobile checks of all 27 problem pages, 632 local links and the actual generated-file download hash. The source-only fallback has no broken download link. Cloud CI and protected deployment verification remain pending publication.

No outreach, spending, new accounts, recordings, weights or new hosted recipe. Preserve research worktrees and licences.

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
