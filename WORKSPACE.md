# Kufu Labs workspace

## Current task

Broaden the lab overview to reflect the existing cross-domain investigation. Pose tracking is the first implemented exploration, not the lab's exclusive subject or an automatic priority for the next build. The README now separates candidate problems from implemented pilots; Home states the wider scope without duplicating the navigation. The [investigation plan](research/opportunity-discovery/PLAN.md#current-direction-compare-candidates-across-domains) defines the next comparison and its evidence requirements.

Work is isolated on `docs/broaden-lab-overview` from main `5589a1830231ec1976362d1f822c7f17160bfc9e`. Publication requires full-diff/exact-commit approval, PR checks and explicit merge authorisation. PR #12 separately removes the duplicate Explorations callout; this change does not include or supersede it.

Local verification: `python3 site/build.py`, `python3 site/package.py`, Prettier on the Home template and the existing `site/verify.cjs` passed with Node 22.22.2, Playwright 1.64.1 and Chrome 156.0.8078.48. Browser checks covered five pages, 180 local links and desktop/mobile navigation with no page errors or external requests. Scientific execution checks were not rerun because this change only updates the overview and plan; sources were not freshly audited.

The canonical production address is https://kufu-labs.vercel.app. PR #11 merged and main run 40602566469 passed all three delivery jobs. The canonical artifact and both legacy-address redirects were independently verified. Authentication protection remains enabled.

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
