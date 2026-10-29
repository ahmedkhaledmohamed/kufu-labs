# Kufu Labs workspace

## Current task

PR #18 is open with approved commit `b2f5d228defa99b4d901b8c1bbf577ebc8dd763d`; run 40799273939 ended when the scientific job hit its 25-minute timeout. Refine.bio passed. Logs show package downloads around 250–600 KB/s consumed most of the job; baseline and patched NWB replays completed, but remaining checks and deployment were skipped. A focused CI repair adds pip caching and a 45-minute cold-install job limit, with all commands/assertions retained. That repair is local and requires exact-diff approval before updating PR #18. PR #17 remains separate and open. Neither PR is authorised for merge.

Ahmed requested progress for experiments launched from the Execution lab. The follow-up is isolated on `lab/experiment-progress`, based on the approved execution commit. The worker saves timestamped stage snapshots to private Blob storage; immutable completed/failed results retain the final timeline. API responses expose the actual reported stage. The UI shows queue/runtime/scientific/output stages and elapsed time, preserves them across reloads, marks stale polling explicitly, and distinguishes failed/interrupted runs. No completion percentage is estimated. Progress persistence cannot prevent Sandbox cleanup.

Local API/worker checks cover running snapshots, stage transitions, immutable final history, duplicate delivery and failed stages. Browser checks use local API doubles to verify live transitions, reload persistence, failures, interruption, stale updates and desktop/mobile layout, separately from the existing real scientific reports. The hosted acceptance gate now requires timestamped baseline, patched, stop and save stages in the actual final result. That new gate remains pending publication. Numerical algorithms, generated input rules and execution bounds are unchanged.

The existing personal Hobby project retains its prepared private `kufu-experiments` store and configuration. Direct Vercel scientific runs already passed; full deployed Queue/Sandbox/private-storage verification remains pending PR #18's preview. The broad environment download rejected by automatic approval review was not performed. Do not retrieve unrelated environment credentials to bypass that boundary.

Local API/worker and browser progress checks, existing hub regression checks and formatting passed. Present the incremental full diff against the approved execution commit before pushing this follow-up. Publish the focused CI repair to PR #18 first after approval, then base the progress change on it. No merge, outreach, spending, new accounts, research recordings or model weights. Continue monitoring PR #18 independently; diagnose its actual CI result without weakening required checks.

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
