# Kufu Labs workspace

## Current task

PR #18 is open at `7f7399302373b1dc7c00a6d432775d48da69eeb4`; PR #19 is stacked on it at `d0afa61e259e3e542e6d8e71645f7819c09b4440`. Runs 40802573803 and 40802657820 passed scientific contracts, refine.bio workflows and browser verification. Both protected deployments failed before hosted execution because the prebuilt queue trigger omitted its required consumer identifier. Production is unchanged. PR #17 remains separate and open; no merge is authorised.

The local repair derives the consumer with Vercel's path-normalisation utility and validates generated configurations with the same NodejsLambda class used by deployment. The already installed build-utils version is now an explicit pinned build dependency. A negative contract check recreates the missing-consumer rejection. Both branches pass local build, contracts and formatting; the corrected hosted deployment remains pending exact-diff review and publication.

The execution backend remains parameterized NWB baseline/patched software on Vercel Sandbox, with fresh controls and private saved outputs. The progress follow-up retains timestamped worker stages, elapsed time, reload-safe history and explicit failed/interrupted/stale states. Scientific/input-generation rules and execution bounds are unchanged. Direct Vercel scientific runs passed previously; the full deployed Queue/Sandbox/private-storage path and its progress history have not passed yet.

Show the repair diff before pushing either branch. Update PR #18 first and preserve PR #19's approved progress implementation when rebasing it. Mark each exact approved commit through the contribution gate. No merge, manual deployment, outreach, spending, new accounts, real recordings or model weights. Do not download unrelated environment credentials; the rejected broad environment pull was not performed.

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
