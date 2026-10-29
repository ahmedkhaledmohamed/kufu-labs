# Lab hub maintenance

The primary navigation is Home, Problems, Sources and Execution lab. Every catalogued problem has a static page at `problems/<id>.html`, containing its audience, source evidence, proposed or implemented solution, execution model, validation and next step. Four implemented explorations include terms, workflow explanations and before/after comparisons. Research-only entries do not imply that a solution exists. The reproduced deletion-provenance defect is labelled separately as an unfixed failure.

The old Explorations and Validation addresses remain compact indexes. Legacy problem fragments and demo/result deep links resolve to their canonical problem pages. Generated research records retain the same global navigation. Problem pages and the directory links work without JavaScript; filters are enabled when the script loads.

The dedicated [Execution lab](../lab.html) submits explicitly requested NWB experiments to Vercel Sandbox and retains actual progress and results. Problem pages continue to display recorded scientific evidence. The pose demo’s browser controls select precomputed real-filter outputs; the other problem pages show recorded runs. Opening a page or generating an input plan starts no scientific compute. The build reads actual retained export/round-trip records for the corresponding comparisons.

Start at [Problems](../problems.html). [Explorations](../explorations.html) and [Validation](../validation.html) remain compatibility indexes, while each problem owns its explanation and demonstration links.

See [delivery and validation](DELIVERY.md) for the exact build, CI stages, artifact packaging, protected Vercel configuration, evidence retention and deployment gates. Source Markdown remains authoritative; generated research views show the recorded investigation rather than silently rewriting its historical findings.

## Maintain the catalogue

Edit catalog.json. Problems retain stable IDs, domain, work state, evidence description, need/concept, possible contribution, existing alternatives, integration route, limits, next action, primary references, source-board IDs, investigation record and review date. Work state is independent of resolution. Problem entries also supply a canonical URL, audience and possible value. Implemented entries provide their plain-language story, terms, workflow, comparison and execution model. Demonstration entries state runtime, inputs, command, expected output, verification and limits, and link back to their problem.

Run `npm run build`; this generates the root entry pages, one page per catalogued problem, readable research records and a deployable `dist/` allowlist and bundled Vercel Functions in `dist-backend/`. The build manifest records static and backend file hashes. The standard-library Markdown renderer escapes raw HTML and supports the headings, prose, links, code, simple tables and list items used here. It does not implement all CommonMark extensions. Generated pages must be rebuilt after edits to a linked record.

No background crawler is installed. Refresh dated evidence deliberately and retain blocked-fetch notes, competing work and negative findings. A board listing is not a licence, a current unmet need or permission to download data or contact anyone.

## Checks

`npm run lint` checks maintained web/workflow source formatting. Python uses the recorded Ruff version. `npm test` verifies the packaged site with real browser interactions, every navigation page, filtering/reset, cross-page links, source navigation, demo popup, document targets and desktop/mobile overflow. It writes reports, screenshots and offline traces under ignored `.runs/`; it does not overwrite historical tracked result files.

`HUB_ROOT` selects another package directory and `HUB_URL` selects the corresponding authenticated deployment. In deployed mode, the test compares its build manifest with the tested local artifact. `VERCEL_AUTOMATION_BYPASS_SECRET` is consumed only through request headers; remote traces are disabled to keep that credential out of evidence artifacts. `CHROME_PATH` can select an existing local Chrome installation.

The [validation review](VALIDATION.md), [earlier hub result](verification.json), and [bounded software results](validation-results.json) distinguish historical checks from current CI execution. GitHub Actions is the authoritative source for cloud job status. No researcher benefit, biological correctness or completed upstream fix is inferred from green checks.
