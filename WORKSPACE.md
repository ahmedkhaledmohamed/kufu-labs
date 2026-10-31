# Kufu Labs workspace

## Current task

Main is at merged PR #25 (`bca3bab8d0e23f225b0eec554c2a3d33872391e4`). The owner-exemption continuation is on `feat/owner-quota`. PR #26 remains open: its required scientific and browser checks passed, but the deployment job in run 41123580209 reached the shared daily quota (HTTP 429). The existing merge authorisation applies to that PR once checks pass. Automatic merge is disabled; no branch-protection bypass or manual deployment is authorised.

The requested change gives the lab owner's verified Vercel identity an exemption from the daily submission cap. Auth.js handles OIDC state/PKCE/nonce checks and encrypted, secure-cookie sessions; the API compares the verified subject against a server-only owner ID. Unconfigured, expired, forged, wrong-key, non-owner and unrecognized-host sessions receive no exemption. User-supplied account IDs and flags do not grant privileges. Owner submissions record `quota_policy: owner-exempt` without consuming shared slots; other users keep the ten-per-UTC-day allowance. Existing case, input, runtime, network and concurrency limits remain. CI credentials remain separately capped.

Local tests use real Auth.js session cryptography and built backend functions, plus service/browser doubles. They cover owner and non-owner quota behaviour, expiry/forgery, spoofed identity, CSRF, input limits, idempotent retries, secure-cookie responses and both original/rewritten auth URLs. They do not constitute an actual Vercel sign-in or hosted validation. No additional scientific jobs were launched.

Activation requires a Sign in with Vercel App, its client ID/secret and callback configuration, plus a server-only session secret and the verified owner's Vercel ID. The CLI exposes no App-registration command and this session has no browser surface. The exact setup is in [Delivery](site/DELIVERY.md#owner-account-quota-exemption). No credentials are stored in source or requested through chat. The feature remains disabled until all required settings exist. Source publication still requires exact-diff approval, and merge is a separate gate.

No outreach, spending, new accounts, recordings or model weights. Preserve scientific worktrees and licence notices. The scientific patches are unchanged. This account feature does not establish researcher benefit or biological correctness.

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
