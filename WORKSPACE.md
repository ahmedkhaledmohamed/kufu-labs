# Kufu Labs workspace

## Current task

PR #23 is merged at `ae40f3c97839d6fc0c6ba9d860d7edb6d0a9ac58`. All four jobs passed in [main run 41066376233](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41066376233). Production's manifest and seven sampled deletion-provenance assets match the tested artifact. Anonymous access remains protected. The actual deployment experiment `b05e3c6d-0edb-4c86-9c67-c6663089ade3` completed with its Sandbox stopped. The existing movement repair approach overlaps another contributor's report; independent evidence is retained without a competing upstream submission.

The current continuation on `fix/mne-unclipped-onsets` investigates [MNE #12327](https://github.com/mne-tools/mne-python/issues/12327). A sample-1 annotation rounds to a value whose default floor lookup returns sample 0 at 300, 512 and 2048 Hz, in release 1.13.2 and current source `0265fc9a575f125d95c5c92f672fd0bb85cfab2d`. Existing `use_rounding=True` correctly finds sample 1; it does not restore the original onset value. This is software timestamp mutation, not evidence of physical clock drift or biological harm.

The local candidate retains the original onset only if neither side was clipped and the original span is wholly inside the existing datetime-resolved limits. Existing clipping behavior remains. The existing crop test is extended across four rates and dated/undated origins; six baseline cases fail and all 12 selected candidate cases pass, including four other existing tests. All applicable upstream pre-commit checks passed on the two changed files. The source-only preparation and network-blocked verifier lock source, tests, patch and licence hashes. See the [implementation, science explanation and limits](projects/mne-annotation-onsets/README.md).

The patch, CI addition and EEG problem-page update are local, pending exact-diff approval and publication. No general datetime-precision repair, nonzero-first-sample workflow, serialization, HED-specific evaluation, full MNE suite, real recordings or user benefit is claimed. MNE's contribution policy requires personal human review and prohibits fully automated submissions; no MNE submission text, outreach or PR is prepared. Recheck upstream before further investment. The [cross-domain follow-up](research/opportunity-discovery/VALIDATION-BATCH.md#30-october-follow-up) records why this bounded case was selected over overlapping accessibility work.

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
