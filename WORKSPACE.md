# Kufu Labs workspace

## Current task

The previous goal is complete. PR #15 merged at `d60b408cb95fa4905cdf0402ef5aa5273a7fe683`; main run 40693803427 passed scientific, browser and protected production deployment gates. Independent production checks matched fourteen asset hashes, verified the source commit, PostgreSQL evidence, desktop/mobile navigation and authentication protection.

Ahmed approved the next zero-age workflow milestone. Work is isolated on `validation/refinebio-workflow` from refreshed main `d60b408`. The active goal is to exercise refine.bio's supported ingestion/export path, relevant official migrations and production hooks with constructed inputs, then maintain the demonstrated path in CI and explain its before/after result in the hub. The current component/database replay is evidence to build on, not a substitute for executing the actual exporter. The new local `--migrations` replay passed official migration execution (91 migrations per revision), real startup-hook registration, save/reload and metadata checks on both revisions. It resolves tracked configuration from the source root; the initial probe from the wrong directory failed before that correction. The S3 deletion handler is registered but deliberately not executed. Actual worker TSV/JSON export remains unrun. Real SRA `_generate_sample` creation now passes with five constructed metadata cases per revision, a constructed ENA file-report response, actual original-file/experiment associations and saves. The 28-case harmoniser replay and eight targeted new methods plus existing Sample check also pass. Fresh source-only partial/sparse preparation passed without checking out test volumes. A new independent Linux CI job is configured using the pinned upstream base and actual worker/common dependency files; web/deploy wait for its success and the validation view reads actual export result records. PR #16 was opened at approved commit `e024999`. First remote run 40760162685 passed the existing scientific gate and built the exact R 3.4.4/rpy2 base, then failed worker-image `pip check`: the floating base wheel 0.48.0 requires packaging >=24 while upstream pins packaging 23.0. The exporter and web/deploy did not run. The approved wheel 0.41.3 correction was pushed at `42e1d9a`. Second run 40761617775 built the worker image and passed dependency checks, then failed the baseline real-worker import because the harness entered the worker directory after import-time relative assets were read. A new local correction moves directory entry before exporter and test-module imports, retaining the actual code and assertions. Its remote execution needs fresh exact-diff approval. No other workflow scope or acceptance check is relaxed. Source and environments remain outside the lab repository.

Portfolio milestones under discussion: NWB retains its maintained round-trip CI and upstream review package; pose overlap needs a read-only boundary against actual SLEAP structures and rendered selection; movement needs rendered interaction verification and a separate decision on deletion provenance; accessibility retains its reproduction and existing upstream PR rather than a competing fix. These milestones do not authorise parallel speculative applications or extra upstream publication. Keep one implementation active while evaluating the next task.

The [validation batch](research/opportunity-discovery/VALIDATION-BATCH.md) records the cross-domain findings. The [first signals exercise](research/opportunity-discovery/SIGNALS-EXERCISE.md) supports gradual neuroscience learning. Researcher benefit and upstream acceptance remain unvalidated. No outreach, new accounts, spending, research recordings or model weights. Exact-diff approval is required before pushing or creating a PR, and explicit merge authorisation is separate.

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
