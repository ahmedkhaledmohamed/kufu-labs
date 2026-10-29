# Lab hub maintenance

The website has independent pages: [Home](../index.html), [Explorations](../explorations.html), [Problems](../problems.html), [Sources](../sources.html), [Validation](../validation.html) and [Execution lab](../lab.html). The execution lab submits parameterized NWB jobs to Vercel; other pages retain recorded evidence and browser demos.

See [delivery and validation](DELIVERY.md) for the exact build, CI stages, artifact packaging, protected Vercel configuration, evidence retention and deployment gates. Source Markdown remains authoritative; generated research views show the recorded investigation rather than silently rewriting its historical findings.

## Maintain the catalogue

Edit catalog.json. Problems retain stable IDs, domain, work state, evidence description, need/concept, possible contribution, existing alternatives, integration route, limits, next action, primary references, source-board IDs, investigation record and review date. Work state is independent of resolution. Demonstration entries additionally state runtime, inputs, command, expected output, verification and limits.

Run `npm run build`; this generates the pages, readable research records, a deployable `dist/` allowlist and bundled Vercel Functions in `dist-backend/`. The build manifest records static and backend file hashes. The standard-library Markdown renderer escapes raw HTML and supports the headings, prose, links, code, simple tables and list items used here. It does not implement all CommonMark extensions. Generated pages must be rebuilt after edits to a linked record.

No background crawler is installed. Refresh dated evidence deliberately and retain blocked-fetch notes, competing work and negative findings. A board listing is not a licence, a current unmet need or permission to download data or contact anyone.

## Checks

`npm run lint` checks maintained web/workflow source formatting. Python uses the recorded Ruff version. `npm test` verifies the packaged site with real browser interactions, every navigation page, filtering/reset, cross-page links, source navigation, demo popup, document targets and desktop/mobile overflow. It writes reports, screenshots and offline traces under ignored `.runs/`; it does not overwrite historical tracked result files.

`HUB_ROOT` selects another package directory and `HUB_URL` selects the corresponding authenticated deployment. In deployed mode, the test compares its build manifest with the tested local artifact. `VERCEL_AUTOMATION_BYPASS_SECRET` is consumed only through request headers; remote traces are disabled to keep that credential out of evidence artifacts. `CHROME_PATH` can select an existing local Chrome installation.

The [validation review](VALIDATION.md), [earlier hub result](verification.json), and [bounded software results](validation-results.json) distinguish historical checks from current CI execution. GitHub Actions is the authoritative source for cloud job status. No researcher benefit, biological correctness or completed upstream fix is inferred from green checks.
