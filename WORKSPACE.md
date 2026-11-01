# Kufu Labs workspace

## Current task

PR #29 merged at `f6c09d4105e4d42811467abc76e4eaec3175eb61`. Main [run 41261081202](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41261081202) passed all four jobs and promoted the release. Independent canonical manifest and downloaded NWB/MNE array checks matched that commit; both Sandboxes stopped. The earlier quota-blocked PR #28 release is superseded by this successful release.

The approved continuation is `feat/mne-workflow-validation`: exercise the existing MNE candidate through attachment, native FIF save/reopen, event extraction and epoch creation. The complete local comparison passes 32 constructed cases per revision, including zero/nonzero first-sample offsets and relative/UTC origins. It verifies 256 exported signal/epoch arrays. Candidate attachment changes zero onsets versus 22 on the baseline; FIF serialization still changes 16 candidate onsets. Default rounded event extraction and epoch contents are correct on both revisions. Explicit truncation remains vulnerable, including eight pre-existing exact-reference mismatches. No broader precision or researcher-benefit claim is supported.

Local verification passed: the real 64-case host comparison, Ruff lint/format, site lint/build and desktop/mobile browser checks across 27 problem pages and 618 local links. No page errors, external requests or background scientific execution occurred.

The annotation patch is unchanged: serialization uses a separate float32 representation and the existing default rounded event extraction already selects correct samples in every tested case. The useful result is a runnable host workflow and an honest boundary for the repair. The problem page derives representative stage tables from retained evidence; the existing hosted recipe still covers attachment only. The CI addition and website changes require local verification, exact-diff approval and publication before cloud verification. No push or upstream outreach is authorised by implementation approval.

CI still shares the ten-submission UTC daily allowance; the separate CI allowance policy remains pending. Owner sign-in remains disabled until the Vercel App client settings exist. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees and licences. Any push/PR requires approval of the exact diff; merge is separately authorised per PR.

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
