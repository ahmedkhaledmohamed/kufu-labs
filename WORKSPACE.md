# Kufu Labs workspace

## Current task

Implement a bounded neuroinformatics contribution while preparing a gradual science-learning path. The [detailed plan](research/opportunity-discovery/NEUROINFORMATICS-PLAN.md) covers candidate comparison, milestones, learning exercises and FirstPrinciples/Canadian organisation research. Neuroinformatics is an active interest, within the lab's wider cross-domain scope.

The new [NWB stream-integrity experiment](projects/nwb-stream-integrity/README.md) reproduces Inspector #771 at pinned source and preserves all constructed values with a local patch. The actual HDF5/Zarr matrix covers 12 inspected and 12 uninspected cases per revision. The broader upstream unit run passed 343 tests and skipped 5. No recordings or model weights were downloaded. The new replay is not yet a required CI execution gate; that and dependency-design comparison are next.

Verification: the exported patch applied to a fresh pinned worktree and passed the full round-trip matrix. Ruff/Black passed on the upstream change, and Ruff passed on the lab runner. Site generation, packaging, formatting and desktop/mobile browser checks passed across five pages and 204 local links, with 26 problems, 16 boards and three runnable entries. No page errors or external browser requests occurred. The new code and pages remain local pending publication approval.

Work is isolated on `research/neuroinformatics-plan` from main `f06a068c23d33e7a615a6048b17fb8b9aaa3efc2`; upstream implementation stays in a separate pinned worktree. No outreach, upstream PR or maintainer approval is claimed. Publication requires full-diff/exact-commit approval and an explicitly authorised merge. The upstream guide also requires issue approval before a PR.

PRs #12 and #13 merged. Main run 40607757738 passed all three jobs, and independent production checks confirmed source, seven sampled asset hashes, desktop/mobile navigation, the broader overview, removed duplicate callout and blocked unauthenticated access at https://kufu-labs.vercel.app. No open PRs remained at that check.

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
