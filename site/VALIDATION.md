# Contribution validation review

Reviewed 27 October 2026. The question is whether the original reported problem is addressed, not whether a local demonstration runs. No researcher study or outreach occurred.

| Contribution | Baseline / observed result | Does this solve the original problem? | Remaining evidence |
| --- | --- | --- | --- |
| movement explicit-edit confidence filter | Pinned revision `39ee15e29706150d7d4f60ba617aa99d2027eed7` plus unchanged approved patch; earlier 97 synthetic filtering cases and real-widget/model-event workflow. The local CPU-rendered replay adds an actual Qt pointer drag and verifies the visible saved/filtered reload; the CI follow-up remains unpublished. | A local filtering subproblem is addressed. Issue #1027 also concerns representation and workflow; it is not claimed resolved. | Supported API scope, upstream acceptance/release, the first cloud rendered replay and independent workflow usefulness. |
| Pairwise overlap inspector | sleap-nn `a2b97fe0a7d908813f0d555df284307fd5060fd5`; 7 synthetic cases, 498 full-filter calls, 168 browser boundary views. | No. Numerical semantics and inspection behaviour are demonstrated; the requested SLEAP GUI feature is not implemented. | Read-only host selection/import with correct node/instance/score mapping; useful decisions on an authorised real task. |
| Deleted-point provenance | Pinned movement repeated-export reproduction; coordinates remain missing while deletion flags disappear. | No. A defect is reproduced and reported, not fixed. | Before/after regression covering deletion-only and mixed edits without resurrecting coordinates. Separate PR #3 contains the artifacts. |

The [fresh replay result](validation-results.json) passed on 27 October 2026 (4.526 seconds; 410,976,256 bytes peak RSS). The unchanged synthetic verifier rechecks eleven invariants: exact patch, real loader/saver buttons, move flag and NaN score, removed/originally missing positions, XY/time mapping, edit flag reload, explicit versus legacy filtering, immutable input and filtering decisions after a second export. It again retains the negative result: removed-point edit provenance is lost after reexport. This loss does not invalidate the verified coordinate-filtering decision, but prevents a broader preservation claim.

Source-state refresh: [movement #1027](https://github.com/neuroinformatics-unit/movement/issues/1027), [#1174](https://github.com/neuroinformatics-unit/movement/issues/1174) and [SLEAP #2816](https://github.com/talmolab/sleap/issues/2816) remain open at this review. [SLEAP #2810](https://github.com/talmolab/sleap/pull/2810) is an open draft, so custom left/right pairing is not unclaimed work and not a proven landed resolution. The exact API snapshot is retained in catalog.json. Open/closed status alone is not outcome evidence.

## Next bounded validation goal

The most concrete next local task is to select a supported SLEAP version, construct host-native predicted instances, and verify a read-only adapter preserving skeleton node order, coordinates/NaNs, frame/instance identity and scores. No models, inference, videos or UI label edits are necessary. Stop if dependency/licence boundaries cannot remain explicit, the selected backend does not match the displayed result, or an adequate supported comparison surface is found.

A native selection panel or real .slp input follows only after that contract is verified. Technical adapter success still does not establish researcher benefit. The proposed workflow study remains archived and unsent until Ahmed chooses to share the solid artifact; no recruitment or dataset access is implied by this plan.

## Source-directory freshness

The hub links 15 boards/directories. Gap Map, JLA, NIH, Neurostars, USA.gov, OpenADMET and the Challenge.gov retirement notice were read on 27 October. OpenChallenges exposed a JavaScript shell; Grand Challenge and Light My Cells returned HTTP 403. LipSync’s listing was retrieved from a cached crawl without a live issue audit. AI4Life is retained as historical use-case/call evidence, not an asserted current call. Older candidate citations retain their earlier review dates.

Challenge.gov’s official notice records retirement on 30 March 2026 and points to USA.gov innovation resources. No comprehensive or authoritative board of every scientific problem was found. The aggregation includes named candidates already investigated in this lab; it is not an automated feed, prevalence estimate or ranking of scientific importance.
