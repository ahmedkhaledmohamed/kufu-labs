# Kufu Labs workspace

## Current task

PR #16 is merged at `88ad9eedf0f96c30cedddbccf5257858c8168fa2`; its main pipeline and independent production audit passed. PR #17 (dedicated problem pages) remains separate and open. It is not merged by this task.

Ahmed approved an execution lab on Vercel. Implementation is isolated on `lab/vercel-experiments` from refreshed main `88ad9ee`. The first adapter runs parameterized synthetic NWB baseline/patched round trips, with fresh uninspected controls. Vercel Functions submit/read jobs, Queues schedules one worker at a time, Sandbox runs the actual Python software, and private Blob storage retains results after compute stops. The UI offers editable inputs, seeded signals, boundary batches, real comparisons, logs and downloads. Viewing the page or generating its input plan starts no scientific compute.

A direct Vercel Sandbox run passed HDF5 and Zarr cases in 16.301 seconds; baseline changed 300/500 and 51/51 rows, patch changed zero, controls preserved inputs, and the VM stopped. Complete pinned CPython resolved the hosted runtime's missing `_bz2`. Four additional local parameterized cases passed. API and browser checks distinguish their local service doubles from actual scientific execution. The protected deployment gate now requires a real queue-to-Sandbox job and private download verification before promotion; that gate is pending publication.

The existing personal Hobby project has a new private `kufu-experiments` store and lab configuration for future preview/production builds. No deployment was replaced and no paid plan/account was added. A broad local environment pull was rejected by automatic approval review due to unrelated-secret exposure; it was not performed. Native Blob read/write verification needs credentials, so the deployed function's own OIDC path remains to be exercised by the preview gate. Do not download the full environment to bypass that boundary.

Finish checks and show the exact full diff and contribution record before committing/pushing/opening the execution PR. Publication and merge remain separate approvals. No outreach, spending, research recordings or model weights. Other exploration implementations remain unchanged; extend the execution interface to them after this first deployed flow passes.

## Entry points

- [Home](index.html): meaning, purpose and the practical-ingenuity figure.
- [Explorations](explorations.html): project implementations, runnable examples and limits.
- [Problems](problems.html), [sources](sources.html) and [validation](validation.html): the evidence catalogue and outcome assessment.
- [Execution lab](lab.html): parameterized scientific jobs on Vercel.
- [Delivery](site/DELIVERY.md): CI/CD, artifact identity and protected deployment.
- [Licensing](README.md#licensing): default MIT terms and preserved GPL/BSD exceptions.

## Verified baseline

Main `10b5e2c139adc693f774792b41ffa85bacd37b69` includes merged PRs #1–#9. Run 40577617957 passed scientific, build/browser and protected Vercel deployment checks. The site is live at the existing protected production URL; its source and sampled asset hashes match the exact CI artifact. Independent desktop/mobile checks passed the inspector navigation, comparison, 182 local links and blocked unauthenticated requests. The earlier deployment goal is complete.

## Release state and remaining work

PR #10 merged at `1fb72e3f81dc6184e1d7a40cf9871808b69419cb`. Main run 40598637899 passed all three jobs, promoted the tested Kufu site, and passed an independent production audit. Public repository and license access were verified anonymously. The earlier standalone Home proposal is superseded by the released Kufu meaning/purpose/figure page.

No outreach, new accounts, spending, recordings or model-weight downloads are authorised. Preserve existing research worktrees and project/upstream licence notices.

## Scientific claims

The pose inspector uses constructed inputs and unchanged upstream filtering. It is not yet integrated into SLEAP. The movement patch addresses a local filtering subproblem; repeated-export deletion provenance remains an unfixed finding. Researcher benefit, adoption and end-to-end problem resolution remain unmeasured.
