# Kufu Labs workspace

## Current task

PRs #33 and #34 are merged. Main `a2026408b220137ebe235fbd0f77ebee54f1bf2b` passed all four jobs in run 41708924580 and deployed to the protected canonical URL. Independent production checks verified the movement acknowledgment, all four generated NWB files, exact archive hashes, numeric comparisons and anonymous HTTP 302 protection. No PR remained open at completion of that release.

The authorised continuation is `verify/movement-upstream-1190`: assess the existing contributor’s newly available draft PR #1190, without outreach or a competing implementation. Base `96733f808885300cc3d86b11e2c5189997671b65` and head `78e41a2c726ddd4733f9ca46a78034a5a23c8d47` are pinned with source, test and licence hashes. The base converter matches the earlier baseline. Neither source has the local Kufu patch applied.

The base has the six expected Kufu deletion failures and the PR’s four expected new-test failures. The head passes all 15 independent Kufu cases and all 49 selected upstream conversion cases. The real Qt canvas/Delete/Save/reopen replay loses provenance at base and preserves it at head, with numeric values, time and never-detected/unscored controls correct. Both final runs used the cached immutable Linux arm64 CPU image, disabled networking and bounded resources. Logs, XML, native files and captures stay under .runs; sanitized JSON and a reproduction runner are prepared for review.

The problem page and investigation distinguish independent validation of a contributor’s draft from the existing local candidate, upstream review/merge/release and researcher benefit. Reset/re-add UI, recordings and the full napari suite remain unverified. The new scientific comparison is retained local evidence; existing CI behavior is unchanged. Local Ruff 0.16.10, site lint/build and desktop/mobile browser checks passed across all 27 problem pages and 640 local links. The upstream head is still the assessed revision and no human PR review was present when rechecked. Exact-diff approval is required before push/PR, and merge requires separate authorisation.

No outreach, spending, accounts, recordings or model weights. Preserve existing research worktrees and licences.

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
