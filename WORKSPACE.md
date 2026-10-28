# Kufu Labs workspace

## Current task

An autonomous goal is active to execute the approved Kufu plan: finish the NWB review package, compare concrete current gaps across neuroinformatics/accessibility/biological metadata, implement only a justified bounded improvement and maintain the gradual science-learning path. Kufu remains focused on useful free scientific software, rather than courses or one domain.

Work is isolated on `research/kufu-validation` from main `ebe44bf6ccb1c2b92b769e7694f0acae36110e05`. The [validation batch](research/opportunity-discovery/VALIDATION-BATCH.md) records the decisions. The [NWB review package](projects/nwb-stream-integrity/REVIEW.md) is prepared locally. Actual JupyterLab browser checks reproduce a toolbar focus failure with an existing PR; no competing patch was built. Source inspection shows refine.bio already retrieves BioSample metadata, so generic enrichment was rejected.

A source-discovered [zero-age metadata omission](projects/refinebio-zero-age/README.md) now has a local component patch: 16 constructed zero variants change from omitted to retained, with positive/empty/unknown controls unchanged. The 28-case replay imports the actual pinned harmoniser with Django 3.2.18 and blocked network connections. Five harmoniser and three model-metadata test methods pass, including after patch reapplication. Source handoff review found a second zero-loss fallback in Sample metadata export; it is included in the same bounded patch and an offline real-model replay. An additional follow-up now passes actual PostgreSQL 16.2 schema creation, Sample save/reload and metadata output with five cases per revision and the existing Sample regression. It uses private Unix-socket databases with no TCP listening, verifies fixture identity and cleans up. Production hooks, migrations, full service tests and output-file generation remain untested. A [first signals exercise](research/opportunity-discovery/SIGNALS-EXERCISE.md) supports the learning path.

Final local formatting and desktop/mobile hub checks passed across five pages and 251 local links, with no page errors or external browser requests. The combined patch reapplied cleanly and passed both replays; the harmoniser-only patch is rejected by the model-metadata replay. The signals exercise produced its documented mathematical outputs. The PostgreSQL follow-up is not pushed and has passed its final hub checks and needs a refreshed exact-diff review. The published initial batch remains unchanged. The approved initial batch was pushed and PR #15 was opened at head `e7c2e407a787f864f5d8c54284607bb265ff8c00`. All three gates passed in CI run 40619511153. Full-diff/exact-commit approval is required before publishing a lab PR; explicit merge authorisation remains separate. No outreach, upstream PR, account, spending or research-recording/model download occurred. The goal stays active while required publication review is pending; do not mark user benefit or upstream integration complete.

PR #14 is merged at `ebe44bf6ccb1c2b92b769e7694f0acae36110e05`. Main run 40613968067 passed all three gates. The production audit confirmed source and eleven sampled asset hashes, desktop/mobile navigation and blocked unauthenticated access at https://kufu-labs.vercel.app. The NWB CI artifact records 341 passed and 5 skipped, and production serves its fresh results. Preserve existing worktrees and the separation of lab publication from upstream acceptance.

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
