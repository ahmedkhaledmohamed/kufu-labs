# Kufu Labs workspace

## Current task

PR #30 merged at `bdd26acb61f166a1618748ab7e8ef8dc6219ac7f`. Main [run 41264716288](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41264716288) passed all four jobs and promoted the release. Independent canonical manifest, MNE page and workflow-evidence reads match the tested artifact; NWB/MNE result archives verify and both Sandboxes stopped. The MNE workflow establishes the bounded in-memory fix and its FIF/default-event limits, rather than better epoch selection than the existing default.

The approved continuation is `feat/nwb-installable-builds`: build labelled wheels from the pinned 0.7.2 baseline and unchanged repair, install them into separate fresh environments, verify imports/package bytes and repeat real inspection/write/reopen plus selected regressions. No upstream submission or package-registry publication is authorised.

Packaging preserves source and attribution, adds distinct local versions and embeds the full licence and provenance. A first missing-licence build was rejected. The macOS standalone interpreter required symlink-based environments; the network blocker now raises the OS error handled by upstream's existing streaming probe. These harness corrections leave scientific expectations unchanged. Both installed replays passed their expected comparisons: baseline preserves 0/12 inspected cases and repair preserves 12/12, with all 24 uninspected controls preserved. The installed unit suites retain 278/289 passes, the same three known failures and five skips each. All 55 package files per build were verified. Source-import and altered-wheel negative probes are rejected. Both browser downloads match their verified wheel hashes. Ruff 0.16.10 lint/format, site lint/build and desktop/mobile checks across 27 problem pages and 625 local links pass; the installed repaired CLI reports its local version. Cloud CI of this new build step remains pending publication.

PR #31 scientific and local browser jobs passed in [run 41314310305](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41314310305). Independent inspection verified every Linux package file and both wheel hashes; both artifacts match the local builds byte for byte. Protected preview browser verification timed out waiting for a download. Direct authenticated HTTP returns the correct wheel bytes, while a local HTTP probe shows Chromium omits custom context headers from native downloads. The scoped correction requests Vercel's documented bypass cookie in the existing authenticated browser context; a second local probe verifies exact download bytes with the cookie and no custom header. Project protection and anonymous checks remain unchanged. The new commit needs exact-diff approval before pushing; the requested merge remains pending successful CI.

CI will generate and verify the wheels before packaging fresh result manifests and downloads; source-only builds omit missing wheel links. Generated binaries/environments stay out of Git. Complete local verification and exact-diff approval precede push/PR. Merge remains separately authorised per PR. Real recordings, other dependency stacks and researcher benefit remain unverified.

The shared ten-submission UTC daily experiment allowance and pending separate-CI policy are unchanged. Owner sign-in still needs Vercel App client settings. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees and licences.

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
