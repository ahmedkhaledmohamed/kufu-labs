# Lab hub maintenance

Open the root index.html directly or serve the repository with `python3 -m http.server 8878 --bind 127.0.0.1`. The website is local and static; it is not deployed. Search, filters, expanded evidence, source links and the overlap demonstration need no account or runtime service.

## Maintain the board

Edit catalog.json. Each problem has a stable ID, domain, work state, evidence description, reported need or concept, possible contribution, existing alternatives, integration route, limits, next validation action, primary references, source-board IDs, investigation record and evidence review date. Deferred concepts remain visible; source presence alone does not establish demand.

Keep work state independent of resolution: a local patch, reproduced defect or technical demo must not become “solved” without the ledger’s stated outcome evidence. Review an issue’s original scope and linked implementations, not just open/closed state. Source-board records distinguish directory purpose from reachability and freshness.

Run `python3 site/build.py` from the repository root. It uses Python’s standard library, validates IDs/references/local entry points, embeds the catalogue in the root page, and generates readable research pages under site/records. Raw HTML is escaped; the minimal renderer supports the Markdown constructs used here (headings, prose, links, code, simple tables and list items). Nested list formatting and full CommonMark extensions are not supported. Source Markdown remains authoritative. Rebuild after editing a linked record.

No crawler or background refresh is installed. Refresh dated evidence deliberately, retain negative results, and record access failures without treating them as absent evidence. Catalogue links do not grant data licences or permission to register, download recordings, message others or publish.

## Verify

`verify.cjs` uses an existing Playwright installation with a separate headless Chrome process. Set `PLAYWRIGHT_MODULE` to the package directory and `CHROME_PATH` to an installed Chrome binary if necessary, then run `node site/verify.cjs`. No dependency install or browser download is required by this repository. Evidence is written outside the repository by default; `HUB_OUTPUT` can override that directory.

The recorded run passed: 25 problems, 15 source boards, four explorations, 14 rendered research pages and all local document links, with no page errors or HTTP requests. Desktop and mobile screenshots were inspected.

The check exercises search and compound filtering, empty/reset states, problem deep links, disclosure contents, source-board filtering, every exploration, rendered research links, embedded demo controls and return navigation, source provenance, mobile layout and local link integrity. It checks that standalone-file browsing causes no HTTP requests and records JavaScript errors and screenshots.

The overlap project separately retains its real numerical oracle generator and browser verification script. The movement project retains its pinned patch and real-widget replay. [Validation review](VALIDATION.md) explains what these do and do not prove; [verification.json](verification.json) records this hub’s actual check results.

## Next steps and publication

The next local validation candidate is a read-only host-native SLEAP instance/skeleton/score adapter on constructed data. It has not been implemented by the hub task. Researcher outreach remains deferred. The requested private-repository PR follows full-diff, contribution-record and exact-commit approval; no merge or public deployment is authorised.
