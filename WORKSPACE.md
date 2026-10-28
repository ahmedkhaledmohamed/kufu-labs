# Kufu Labs workspace

## Current task

Simplify the NWB stream-preservation patch to reuse HDMF's existing helper, and make its baseline/patched replay part of the existing required scientific CI check. This remains one contribution within Kufu's purpose: free, useful software for evidenced scientific workflow gaps, integrated with existing tools and assessed against a baseline. The [implementation and learning plan](research/opportunity-discovery/NEUROINFORMATICS-PLAN.md) keeps science learning and company discovery in support of this work.

The existing-helper substitution and linked HDMF dependency PR each preserved all values in a 24-case constructed replay. The source patch now re-exports the released helper and passes 341 unit tests, with 5 skipped. It keeps 11 regression cases; the extra arbitrary-iterator policy from the first patch is outside this reported task. The new source-preparation script checks the exact revision and patch digest and preserves existing checkouts. CI uses a separate environment, retains NWB evidence and packages freshly generated results.

PR #14 contains the approved initial package at `bcf65b77899a7cce3710693775adf6e0e15dc306`, with all three checks passed; it remains open. The follow-up is isolated on `fix/nwb-helper-ci`, prepared from refreshed main with that approved package carried forward. It is intended to update #14 after exact-diff approval, rather than create a second overlapping PR. No merge, upstream outreach or upstream PR is authorised by this state record.

The exact new CI replay, pytest, Ruff/Black and result-copy commands passed in a fresh isolated environment; `pip check` found no broken requirements. Swapped baseline/patched expectations were rejected. Hub build, packaging, formatting and desktop/mobile checks passed across five pages and 204 local links, with no page errors or external browser requests. The remote follow-up CI run remains pending publication.

Production remains the independently verified `f06a068c23d33e7a615a6048b17fb8b9aaa3efc2` release at https://kufu-labs.vercel.app. Preserve existing research worktrees and all publication boundaries.

## Entry points

- [Home](index.html): meaning, purpose and the practical-ingenuity figure.
- [Explorations](explorations.html): project implementations, runnable examples and limits.
- [Problems](problems.html), [sources](sources.html) and [validation](validation.html): the evidence catalogue and outcome assessment.
- [Delivery](site/DELIVERY.md): CI/CD, artifact identity and protected deployment.
- [Licensing](README.md#licensing): default MIT terms and preserved GPL/BSD exceptions.

## Verified baseline

Main `10b5e2c139adc693f774792b41ffa85bacd37b69` includes merged PRs #1–#9. Run 40577617957 passed scientific, build/browser and protected Vercel deployment checks. The site is live at the existing protected production URL; its source and sampled asset hashes match the exact CI artifact. Independent desktop/mobile checks passed the inspector navigation, comparison, 182 local links and blocked unauthenticated requests. The earlier deployment goal is complete.

## Release state and remaining work

PR #10 merged at `1fb72e3f81dc6184e1d7a40cf9871808b69419cb`. Main run 40598637899 passed all three jobs, promoted the tested Kufu site, and passed an independent production audit. Public repository and license access were verified anonymously. The earlier standalone Home proposal is superseded by the released Kufu meaning/purpose/figure page.

No outreach, new accounts, spending, recordings or model-weight downloads are authorised. Preserve existing research worktrees and project/upstream licence notices.

## Scientific claims

The pose inspector uses constructed inputs and unchanged upstream filtering. It is not yet integrated into SLEAP. The movement patch addresses a local filtering subproblem; repeated-export deletion provenance remains an unfixed finding. Researcher benefit, adoption and end-to-end problem resolution remain unmeasured.
