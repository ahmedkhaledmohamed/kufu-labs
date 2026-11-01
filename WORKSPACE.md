# Kufu Labs workspace

## Current task

PR #31 merged at `c8c7530e8e2f867f998ebb4fa66d1b4a6589148a`. Its corrected preview passed all four checks, including protected native wheel downloads and hosted NWB/MNE experiments. Main [run 41316789150](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41316789150) passed scientific, build and protected browser checks but stopped at the shared daily experiment limit (HTTP 429) before promotion. Canonical production still serves `bdd26acb61f166a1618748ab7e8ef8dc6219ac7f`; independent checks verified the retained production-target wheel-download bytes. No manual promotion or quota reset was performed.

The approved continuation is `feat/verified-ci-allowance`: authenticate GitHub delivery CI and give it a separate 20-submission UTC daily pool while preserving the existing ordinary ten and owner exemption. The implementation binds signed OIDC proof to immutable repository/owner IDs, audience, workflow, environment, hosted runner and deployed commit. PR previews additionally require same-repository head/base and matching open-PR merge metadata; outages fail closed. Only the deployment job receives id-token write permission. Tokens stay in process memory and request headers, never Sandbox inputs or artifacts.

Local signed-token tests reject forged/wrong claims and forks, enforce concurrent CI/ordinary pool caps, preserve same-origin validation and sequential retries, check run receipts and refresh expiring proof. Existing ordinary budget keys are untouched; no weaker deployment or scientific acceptance gate is introduced. Local lint/build, signed-policy/concurrent-pool/client-refresh checks, actual bundled Function verification, existing API/worker and encrypted-session checks, experiment UI browser checks and desktop/mobile site checks all pass. A local defensive review traced fork identity, fixed outbound endpoints, replay bounds and budget fallback; no specialized reviewer is exposed. Exact-diff approval is the next publication gate. Actual GitHub-minted proof and cloud CI allocation remain unverified until the PR deployment gate runs.

The existing owner sign-in still needs Vercel App client settings. No outreach, spending, new accounts, recordings or model weights. Preserve research worktrees and licences. Any push/PR requires approval of the exact diff; merge remains separately authorised per PR.

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
