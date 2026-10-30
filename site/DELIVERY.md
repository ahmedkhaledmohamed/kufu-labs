# Lab delivery and runnable demonstrations

## Current verified release

PRs #17–#19 are merged. Main `b0e884450008c0ecc472e783626f0b4b6509ffa0` passed all four required jobs in [run 40877666335](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40877666335). An independent production audit verified eight tested-asset hashes, 13 retained experiment stages, a private archive hash, stopped compute and blocked unauthenticated access. The canonical protected production address is https://kufu-labs.vercel.app. Pending-release and failure descriptions in earlier delivery records below describe their historical state.

Publication history: PRs #3–#7 are merged. Main run [40572525361](https://github.com/ahmedkhaledmohamed/scientific-software-lab/actions/runs/40572525361) passed scientific, local browser and deployed browser verification. The project promotion API accepted the request, but its empty successful response made the helper fail JSON parsing. Independent inspection and browser verification confirmed that production is live at merged main `16e4cdb65ff79c614b7201a0349d986e5706c018`. The focused response-handling fix is local; a green updated main release remains required.

## Runtime and navigation

Home, Problems, Sources and Execution lab are the primary navigation destinations. Each problem has an independent static document at `problems/<id>.html`. The old Explorations and Validation documents remain compact indexes; historical problem/demo/export fragments resolve to the corresponding problem page. Each implemented problem explains the need, science, actual contribution, before/after result, execution model, reproduction and limits. The pose browser demo opens a separate tab and returns to its problem page. Research-only candidates clearly state that no solution is implemented.

The hub and pose inspector are browser software. The movement example runs the actual pinned Python/Qt host in an isolated local or CI environment. Python source downloads are inert website assets, not arbitrary server execution endpoints. No universal hosted code runner or remote desktop is introduced.

## Build and inspect

Use Node 22 and Python 3.13. A local `.npmrc` selects the public npm registry.

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run build
npm test
DEMO_OUTPUT=.runs/overlap npm run test:overlap
python3 -m http.server 8879 --bind 127.0.0.1 --directory dist
```

Playwright needs an installed browser. Locally `CHROME_PATH` can point to an existing Chrome executable; CI installs its matching Chromium with `npx --no-install playwright install --with-deps chromium`. No research recordings, model weights or training are used.

`site/build.py` validates the catalogue and generates the pages/research views. `site/package.py` copies an allowlist of static pages, records, result files and tracked research/project download types into ignored `dist/`. It excludes environments, credentials, `.git`, CI scripts and untracked project files. `build-info.json` records the source commit, dirty-source flag and SHA-256 of each packaged asset; a dirty local build is not falsely presented as a clean release.

## CI stages and evidence

The immutable-action-pinned `lab-delivery.yml` workflow runs on PRs, main pushes and manual dispatch:

1. **Scientific contracts:** source-only checkouts of movement at the recorded revision, one with the unchanged approved patch and one clean; actual sleap-nn modules and licence checked against pinned hashes; CPU-only Torch; real offscreen Qt/widget replay; independent deletion reproduction. Pip environment and failure logs are retained. A reproduced deletion bug is a negative result, not a fixed defect.
2. **Web:** consume that run's CPU-generated pose demo, install locked tooling, lint, build once and verify five-page navigation, filters, source/deep links, demo tab, validation scope, mobile layout and local document targets. Test the full pose boundary UI. Retain the exact tested site plus screenshots and offline browser traces.
3. **Delivery:** download the tested artifact, verify each hash and its commit, verify the exact Vercel project/team and all-deployment protection, deploy without rebuilding and run authenticated browser checks against the deployed site. Verify unauthenticated requests cannot read the hub, catalogue or demo. A main release uses `--prod --skip-domain`, is checked for stale-main races, then explicitly promoted through the project API. Generated aliases may already be assigned before this promotion; the flag skips custom domains, not all generated routing. Same-repository PRs receive protected unpromoted previews; fork PRs receive no deployment secrets.

For a brand-new Vercel project, the first deployment can be production-targeted even when requested as a preview. The script uses `--prod --skip-domain` for that bootstrap and never explicitly promotes it from a PR. Actual main deployment metadata showed `autoAssignCustomDomains: false` while the generated `.vercel.app` alias was assigned. Do not interpret the flag or CLI wording as proof that all aliases stayed unchanged. All deployments remain authenticated. Only current `main`, after both verification jobs and deployed browser checks succeed, can request explicit promotion.

Reports/screenshots/traces are GitHub Actions artifacts retained for 14 days. Their visibility follows the repository visibility; publishing the repository also exposes its Actions history. Authenticated remote traces are deliberately disabled: traces can capture request headers, so only offline traces are retained. Remote reports/screenshots contain no verification credential. Longer-term example result files in the repository are dated evidence, not an assertion that the latest cloud workflow has passed.

## Vercel configuration

Verified target: personal scope `ahmed-khaled-mohameds-projects`, project `scientific-software-lab`. `site/deployment-config.json` contains non-secret identity constraints; the deployment script checks them before mutations. Vercel Authentication is configured for **All Deployments**, covering production and preview. No paid protection add-on, new account or purchased domain is used. Implicit Git linking is disabled so a separate integration cannot bypass the CI promotion gate.

A verified CLI limitation ([upstream #17506](https://github.com/vercel/vercel/issues/17506)) makes a fresh CLI profile request user/team metadata even when its project-scoped token can access the project. The delivery script creates a temporary private CLI profile containing only the already verified team-ID mapping, passes it to every Vercel command and removes it afterward. It stores no token in that profile, grants no broader access, and retains the server-side token restrictions plus explicit project/owner/protection checks. A short-lived project token confirmed direct project access and CLI access with that mapping; the original PR run's scientific and browser checks passed before its deployment preflight exposed this limitation. The cached scope mapping passed cloud preview deployment. The high-level `promote` command still performs additional user/team lookups, so the fix uses the [documented project promotion endpoint](https://vercel.com/docs/rest-api/projects/point-production-traffic-to-a-given-deployment) via `vercel api`, retaining the same project-scoped token. Before POST it verifies deployment project, owner, source commit, production target and ready state. An empty successful mutation response is accepted; required reads still require JSON. It waits up to three minutes for the current production target to match the exact deployment ID, ready state and source commit, then verifies the served alias and artifact. Optional `lastAliasRequest` metadata can reject a failed/skipped job but is not required: the real API omitted it after successful promotion. Failed, skipped, unrelated or timed-out promotion cannot produce a success record. The project-scoped API performed the real promotion in main CI; the final response-handling and completion-observation fix still needs a green cloud run.

GitHub Secrets contains a project-scoped `VERCEL_TOKEN` (90-day lifetime, rotate before expiry) and a project-specific `VERCEL_AUTOMATION_BYPASS_SECRET` for browser verification. Values are never placed in source, process arguments, logs or browser traces. Vercel CLI telemetry is disabled. Use secret rotation to replace credentials; do not weaken protection to make a check pass.

After the reviewed PR is published, inspect the actual GitHub jobs and fix observed platform failures before requesting its merge. After the explicitly authorised merge, wait for the main pipeline, verify the production alias as both an authenticated user and an unauthenticated request, and record the deployment URL/commit. Do not manually deploy as a substitute for a broken pipeline without Ahmed's applicable instruction.

## What validation establishes

Execution proves that the selected software runs with stated inputs. Host-contract checks establish the tested integration semantics and preserved invariants. Problem resolution additionally requires comparison with the original workflow and its defined success criterion, with authorised researcher evidence when appropriate. These statuses remain separate on the Validation page. Outreach stays deferred.

## Deployed navigation verification

Main run 40558190385 passed scientific and local browser verification, then stopped before promotion when the deployed source-board check read a select before the external application script had applied its query. A controlled delayed-script probe on that exact staged artifact reproduced an empty initial value and the correct `sleap` value after document load. The verifier now waits for the destination URL and completed load before the unchanged outcome assertions. It deliberately delays that script request for the source-board scenario to retain a regression check. This changes test readiness, not the application, accepted outcomes or deployment gate.

## Project-scoped promotion verification

The original eight helper simulations passed before PR #7, but did not represent the API's empty mutation response or absent job metadata. The actual main run exposed both differences. The corrected local helper passes eleven isolated control-flow cases: empty and JSON mutation responses, successful production without job metadata, rejected empty required reads, stale main, wrong owner, failed/skipped promotion, unrelated promotion, queued timeout and unauthenticated exposure. These simulations do not replace a green real release job.

On 27 October, a separate read-only production audit confirmed the ready current production target and source commit against GitHub main, matched four served asset hashes against the CI artifact, and passed desktop/mobile browser checks across five pages and 180 local links. Unauthenticated hub, catalogue and demo requests were blocked; all-deployment Authentication remained enabled. Production URL: https://kufu-labs.vercel.app. No manual promotion or broader credential was used to bypass CI. Updated PR checks, approved merge, successful main CI and a repeated independent audit remain the completion gates.

## Kufu Labs release preparation

PR #9 merged at `10b5e2c139adc693f774792b41ffa85bacd37b69`. Main run 40577617957 passed all three jobs and promoted the tested artifact; an independent audit passed production source/hash, navigation/comparison and blocked unauthenticated access checks. Earlier failure descriptions above are historical. The public-release branch updates the brand and repository links to Kufu Labs, adds an explicit default MIT licence with retained project/upstream exceptions, and replaces the Home directory with the lab meaning, purpose and approach figure. The GitHub repository is now `ahmedkhaledmohamed/kufu-labs`; private visibility and required checks were retained. Publication of the code changes and the public-visibility transition remain pending review. The Vercel project identity and all-deployment authentication remain the verified existing target.

## Canonical production address

The live production address is https://kufu-labs.vercel.app. It is a verified production domain on the existing project, so subsequent production promotions continue assigning it. The old short production address has a verified 308 redirect to this host. The team-scoped legacy alias still serves the verified release during the CI transition, because the currently merged helper selects that alias first and rejects cross-origin redirects. After the canonical-host helper is merged and main passes at Kufu, enable its project-domain redirect to Kufu as well. Project ID, ownership, deployed source and all-deployment authentication are unchanged; no build or manual deployment was needed to change the routing.

`site/deployment-config.json` names the canonical host explicitly. The delivery helper waits up to one minute for that host to appear on the exact promoted deployment, then performs browser and unauthenticated-access checks there. It does not select an arbitrary first alias. The local helper change still requires reviewed publication and cloud CI; the live domain/routing change is already independently verified.

## NWB stream-integrity follow-up

The follow-up adds `projects/nwb-stream-integrity/prepare.py` to source preparation and an isolated NWB environment inside the existing required **Pinned scientific software contracts** job. The baseline replay must exhibit the documented constructed-data loss, while the helper patch must preserve all values and dtypes. The upstream unit regressions and Ruff/Black checks must also pass. A failure therefore fails an already-required check; no new branch-protection setting is needed.

The existing `scientific-evidence` artifact retains `.runs/contracts/nwb/` results and JUnit output. The web job downloads this artifact and copies the newly generated baseline and patched JSON into the project before packaging the tested site. Vercel promotion remains downstream of the scientific and browser gates. The local equivalent passed; the first remote run of this follow-up remains pending publication.


## Vercel execution lab

The new Execution lab is a parameterized NWB adapter alongside the static evidence pages. Functions submit/read jobs, Vercel Queues invokes the worker, Vercel Sandbox executes pinned baseline/patched software, and a private Blob store retains reports and downloadable arrays after the VM stops. GitHub Actions remains CI and invokes the deployed acceptance check; it does not execute user-submitted jobs.

`npm run build` bundles `dist-backend/functions/` separately from the static allowlist and records its hashes in `dist/build-info.json`. CI retains `tested-backend` alongside `tested-site`; deployment verifies both artifacts and assembles the Build Output API package. The worker has a `queue/v2beta` trigger, one concurrent delivery and a 300-second function duration. The actual Sandbox is capped at 240 seconds and is non-persistent. Private store access uses the function's OIDC context; credentials are not embedded in the artifact.

The existing personal Hobby project runs the reviewed execution workflow with its private `kufu-experiments` store connected to preview/production and `KUFU_LAB_ENABLED=1`. No paid plan upgrade or manual deployment was performed. Static/offline previews explicitly disable execution. Pages and API reads never create Sandboxes. An atomic daily budget and immutable run claim bound submissions and duplicate delivery. Completed runs are retained without automatic cleanup in this first version; quota failures are explicit service failures.

`node lab/verify.cjs` checks request and worker contracts with service doubles and consumes CI's actual parameterized scientific reports. `node lab/verify-browser.cjs` checks UI interactions against local API doubles. `node lab/verify-deployed.cjs` is the separate real hosted acceptance check: it submits HDF5 and Zarr inputs to the protected deployment, waits for the Vercel Queue/Sandbox result, requires stopped compute and preserved controls/patched values, and verifies the private ZIP hash. Deployment runs it before any main promotion. It consumes one of the ten daily submission slots; its real deployed result passed in the merged-main run above. Authentication protection remains enabled for the site and API.

## MNE execution extension

The local follow-up adds MNE annotation attachment to the existing worker and private result flow. The API accepts only `nwb` or `mne`; omitted recipe remains NWB for older requests. Run IDs bind to both the recipe and inputs, and downloads identify the recipe. The existing queue topic and single consumer remain in use; the shared budget stays at ten submissions per UTC day, four cases per submission and four minutes per Sandbox.

MNE accepts bounded sampling rate, annotation sample and constructed origin fields only. Source, patch and experiment payloads are embedded in the tested backend artifact. Networking is disabled before either scientific run. Original/attached timestamp fields and unchanged-input controls are compared, and actual input/output NumPy arrays remain in the private bundle after compute stops. There are no recording uploads, arbitrary-code submissions, new providers or new credentials.

The required contracts consume freshly generated reference and boundary reports for both projects. Local browser checks use API doubles and actual scientific output, including MNE recipe selection, generation, progress, reload and download controls. The real deployed gate submits one NWB job containing HDF5/Zarr cases and one MNE job containing a precision failure and unchanged control. It verifies each download hash, source identity and stopped Sandbox before main promotion. It therefore uses two of the ten shared daily submission slots. MNE's new hosted flow remains unverified until this addition is published and that gate passes. No manual deployment substitutes for the pipeline.


## Owner account quota exemption

The local `feat/owner-quota` continuation adds application-level Sign in with Vercel alongside existing Deployment Protection. Auth.js 0.41.3 handles OIDC discovery, signature/issuer/audience validation, state, PKCE and nonce, and encrypted secure-cookie sessions with a one-hour rolling lifetime. Only `openid` is requested; no project-management, email, profile or offline-access scope is needed. The server compares the verified Vercel subject with `KUFU_OWNER_VERCEL_ID`; browser fields and identity headers are not trusted. Sign-out uses Auth.js's CSRF-protected confirmation flow.

The verified owner bypasses the daily submission cap and does not consume a shared slot. Other users retain ten submissions per UTC day. Submission records retain the quota policy without copying account profile data. All case, payload, Sandbox duration, network-isolation and worker-concurrency limits remain. CI uses a separate identity and does not receive this exemption. Missing configuration or an invalid session never grants owner privileges.

The additional `api/auth` Function handles the Auth.js routes; the maintained deployment helper rewrites their suffixes explicitly. Host validation permits the configured production hostname and the deployment/branch hostnames supplied by Vercel. The Execution lab displays whether the server verified the owner; sign-in is hidden until configured. Offline previews do not authenticate.

### Activation settings

Use Vercel's [App registration instructions](https://vercel.com/docs/sign-in-with-vercel/manage-from-dashboard). Create an App in the existing personal team's Settings → Apps (no new Vercel account or paid integration). Use a descriptive name such as Kufu Labs owner sign-in. Select `client_secret_basic` client authentication, generate a client secret, and enable only `openid`.

Register `https://kufu-labs.vercel.app/api/auth/callback/vercel`. For previews, use Vercel's linked-project callback option with `/api/auth/callback/vercel`, or register the exact preview callback URL before testing it. Redirect URIs must match the deployment where sign-in begins; do not add unrelated domains or broad wildcard callbacks.

Set these server-only variables in the existing Kufu project's production and preview environments:

| Variable | Value |
| --- | --- |
| `KUFU_VERCEL_CLIENT_ID` | The registered App's client ID |
| `KUFU_VERCEL_CLIENT_SECRET` | Its generated client secret |
| `KUFU_AUTH_SECRET` | A unique cryptographically random session secret of at least 32 bytes; keep it consistent across deployments |
| `KUFU_OWNER_VERCEL_ID` | The existing personal owner's immutable Vercel user ID, verified with `vercel api /v2/user`; use the ID, not the username |

Enter secrets directly in Vercel settings or through stdin to `vercel env add`; never place them in chat, source, command arguments or public-prefixed variables. Redeployment through the reviewed CI pipeline is required to activate new environment settings. Keep Deployment Protection enabled. After deployment, sign in as the owner, verify the exemption indicator, and confirm one submission is recorded as owner-exempt. Verify a signed-out/non-owner session remains capped and sign-out removes the exemption. No real sign-in or owner-exempt hosted job has been tested in this local continuation.

`node lab/verify-auth.cjs` uses real session encryption and the built Functions to check owner/non-owner/expired/forged sessions, spoof rejection, host restrictions, CSRF, unchanged input validation, quota accounting and retries. Browser tests use local API doubles for account messages and launch no compute. Auth.js is pinned in the public-registry lockfile; credentials are not embedded in the bundle.
