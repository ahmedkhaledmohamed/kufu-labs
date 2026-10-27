# Lab delivery and runnable demonstrations

Publication history: PR #4 provided the approved hub baseline, and PR #3's diagnostic resolution is now merged. [PR #5](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/5) contains the delivery implementation. Its [initial cloud run](https://github.com/ahmedkhaledmohamed/scientific-software-lab/actions/runs/40511509142) passed the Linux scientific and browser jobs, then stopped at Vercel's user lookup before any upload. The project-scoped CLI fix described below is prepared and locally verified; its updated cloud run is still a release gate. Do not equate these local checks with a deployed preview or production release.

## Runtime and navigation

Home, Explorations, Problems, Sources and Validation are independent HTML documents. Ordinary navigation changes page URLs; the interactive pose demo action opens a separate tab. Each software entry lists its runtime/version boundary, constructed inputs, launch command, expected result, verification evidence and limitations.

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
3. **Delivery:** download the tested artifact, verify each hash and its commit, verify the exact Vercel project/team and all-deployment protection, deploy without rebuilding and run authenticated browser checks against the deployed site. Verify unauthenticated requests cannot read the hub, catalogue or demo. A main release is staged without domain assignment, checked for stale-main races, then promoted. Same-repository PRs receive protected unpromoted previews; fork PRs receive no deployment secrets.

For a brand-new Vercel project, the first deployment can be production-targeted even when requested as a preview. The script explicitly stages that bootstrap with `--prod --skip-domain` and never promotes it from a PR. Only current `main`, after both verification jobs succeed, can assign production domains.

Reports/screenshots/traces are private GitHub Actions artifacts retained for 14 days. Authenticated remote traces are deliberately disabled: traces can capture request headers, so only offline traces are retained. Remote reports/screenshots contain no verification credential. Longer-term example result files in the repository are dated evidence, not an assertion that the latest cloud workflow has passed.

## Vercel configuration

Verified target: personal scope `ahmed-khaled-mohameds-projects`, project `scientific-software-lab`. `site/deployment-config.json` contains non-secret identity constraints; the deployment script checks them before mutations. Vercel Authentication is configured for **All Deployments**, covering production and preview. No paid protection add-on, new account or custom domain is used. Implicit Git linking is disabled so a separate integration cannot bypass the CI promotion gate.

A verified CLI limitation ([upstream #17506](https://github.com/vercel/vercel/issues/17506)) makes a fresh CLI profile request user/team metadata even when its project-scoped token can access the project. The delivery script creates a temporary private CLI profile containing only the already verified team-ID mapping, passes it to every Vercel command and removes it afterward. It stores no token in that profile, grants no broader access, and retains the server-side token restrictions plus explicit project/owner/protection checks. A short-lived project token confirmed direct project access and CLI access with that mapping; the original PR run's scientific and browser checks passed before its deployment preflight exposed this limitation. The updated cloud run remains the release gate.

GitHub Secrets contains a project-scoped `VERCEL_TOKEN` (90-day lifetime, rotate before expiry) and a project-specific `VERCEL_AUTOMATION_BYPASS_SECRET` for browser verification. Values are never placed in source, process arguments, logs or browser traces. Vercel CLI telemetry is disabled. Use secret rotation to replace credentials; do not weaken protection to make a check pass.

After the reviewed PR is published, inspect the actual GitHub jobs and fix observed platform failures before requesting its merge. After the explicitly authorised merge, wait for the main pipeline, verify the production alias as both an authenticated user and an unauthenticated request, and record the deployment URL/commit. Do not manually deploy as a substitute for a broken pipeline without Ahmed's applicable instruction.

## What validation establishes

Execution proves that the selected software runs with stated inputs. Host-contract checks establish the tested integration semantics and preserved invariants. Problem resolution additionally requires comparison with the original workflow and its defined success criterion, with authorised researcher evidence when appropriate. These statuses remain separate on the Validation page. Outreach stays deferred.
