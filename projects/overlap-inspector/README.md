# Pairwise overlap inspector

Local read-only demonstration of overlap filtering, using seven constructed pose examples. No recordings, biological ground truth, accounts or network connection are needed to use it. **No outreach is planned or authorised.** This replaces recruitment as the immediate next step in the earlier unpublished research plan.

## Open and demonstrate

Open [index.html](index.html) directly in a browser. The complete dataset and filter decisions are embedded in that file; Python and dependencies are unnecessary for viewing it. Keep COPYING alongside it when sharing a copy. Alternatively run `python3 -m http.server 8876 --bind 127.0.0.1` from this directory and visit `http://127.0.0.1:8876`.

1. Select **Swapped node labels**. At threshold 0.8, Box IoU suppresses B; Keypoint OKS retains both. The identical boxes hide a node correspondence difference.
2. Select **Different scale, same neighbourhood**, use OKS at 0.6, and reverse score order. The surviving poses change because OKS uses the candidate's bounding-box area. Both directions are shown.
3. Click **Set exact pair boundary**. Equality retains the candidate; entering a slightly smaller threshold can suppress it. Rounded displayed values are not used for this comparison.
4. Select **Three-instance context**, use IoU at 0.5, then move B first. The full frame changes from A/C retained to B retained. A pair score alone does not determine a frame's result.
5. Inspect **Missing / no shared nodes** and **Zero-area boxes**. Missing input is distinguished from suppression. These geometries return zero in this implementation; that is not evidence of a distinct animal.

Controls include pair selection, metric, continuous threshold, score-order permutations, a tied-score example, and bounding-box visibility. Pose inputs are fixed so every displayed result can be traced to the actual pinned numerical code.

## Existing output and inspector contribution

The comparison uses the same constructed input, selected metric, threshold and score order on both sides. The first side shows the pinned filter output states; the inspector side explains the selected pair and exposes the pose overlay, pair measurements and exact boundary. The filtering algorithm and returned poses do not change. This is an inspection capability, not a filtering fix, a screenshot comparison with SLEAP, or completed SLEAP GUI integration.

The demo retains Home, Problems and Sources navigation, an About this problem link, and its implementation/verification code. The hub browser check exercises each return route; the standalone browser check verifies that both comparison views agree with the displayed states at all 168 boundaries.

## Reference implementation

Reference: [sleap-nn tensor FilterPipeline](https://github.com/talmolab/sleap-nn/blob/a2b97fe0a7d908813f0d555df284307fd5060fd5/sleap_nn/inference/filters.py), revision `a2b97fe0a7d908813f0d555df284307fd5060fd5`. Motivation: [SLEAP request #2816](https://github.com/talmolab/sleap/issues/2816). This supports one pinned main-branch tensor processing path, not a claim about all released SLEAP pipelines. The legacy NumPy overlap path can use a different OKS argument order.

`generate.py` executes unchanged upstream FilterPipeline.apply, Outputs and PreprocInfo modules on CPU with float32 tensors. Only overlap filtering is enabled. It verifies source hashes from `source-lock.json`. Namespace packages bypass eager package initializers that would load model/predictor dependencies; no numerical module, output container or metric is mocked or ported. The upstream sources remain outside this repository.

For each case, metric and score ordering, the generator runs the full filter at every possible similarity boundary and at interior and adjacent representable values. It stores decision regions beginning at each boundary. JavaScript selects a region and draws the result; it does not implement OKS, IoU or NMS. Tied-score processing order is recorded from Torch, not assumed from JavaScript sorting. All-missing inputs are identified separately before comparing the outputs.

## Reproduce

Build dependencies are isolated; no monorepo framework or model stack is required. Python 3.13.2 and the exact versions in requirements-build.txt produced the checked-in bundle on macOS arm64. Other platforms/versions may change floating-point or tied-score behaviour; regenerate and reverify rather than assuming identical values.

```sh
python3.13 -m venv /tmp/overlap-build-env
/tmp/overlap-build-env/bin/python -m pip --isolated install --index-url https://pypi.org/simple -r requirements-build.txt
/tmp/overlap-build-env/bin/python generate.py --source /tmp/overlap-reference --fetch
```

`--fetch` downloads only the four hash-pinned source/licence files from the upstream revision, not recordings, model weights or repositories. With an existing verified source cache, omit `--fetch` to regenerate offline. A changed source file aborts generation. `template.html` is the editable page; `index.html` and `verification.json` are generated. No downloading or Python execution occurs when opening index.html.

`verify-browser.cjs` uses an existing Playwright installation and Chrome. Set `PLAYWRIGHT_MODULE` to the installed Playwright package, `CHROME_PATH` to the Chrome executable if needed, and optionally `DEMO_OUTPUT` to a local evidence directory, then run `node verify-browser.cjs`. It launches a separate headless instance, opens the standalone file, exercises controls, checks every stored boundary against the rendered state, checks mobile overflow, and records screenshots/errors/network activity. It never accesses existing user browser windows.

## Verified results and limits

[verification.json](verification.json) records software/source versions and the oracle run counts; [browser-results.json](browser-results.json) records the browser checks. Seven fixtures passed **498 full-filter calls**, including **330 interior/adjacent-boundary probes**. Browser interaction passed **168 boundary views**, at desktop 1360×1100 and mobile 390×844; no JavaScript errors or HTTP requests were observed. Python lint/format and JavaScript syntax checks passed. Screenshot review covered the pose overlay, selected controls, result labels and mobile layout.

The CPU generator's measured maximum resident set was 222,396,416 bytes (about 212 MiB). The broad measured disk envelope, including all Personal worktrees and earlier verification environments/caches, was about 4.07 GiB, below the 5 GiB cap. The isolated browser-check runner reported a maximum resident set of 249,528,320 bytes (about 238 MiB); this is a process measurement, not aggregate Chrome memory. Exact browser/runner versions are in browser-results.json. No recordings or weights were downloaded. The build reused an existing scratch verification environment; it is not a runtime dependency or committed artifact.

This demonstrates numerical behaviour and an inspection workflow. It is not integrated into SLEAP, does not edit labels or run inference, cannot accept arbitrary files/poses, and does not establish identity, researcher usefulness, biological correctness, time savings or adoption. Real dataset import, skeleton matching, score availability and selection integration still need work before this can be called a researcher-ready plugin.

## Design and next step

The pose canvas is primary, with a compact control rail. Cool white, navy and teal/coral/violet instance colours combine with textual states and dashed suppressed poses; colour alone never conveys the decision. System fonts, SVG and embedded data keep runtime portable. Mobile stacks controls below the canvas. Visible focus and keyboard inputs support inspection without pointer-only controls.

Before coding, the design review identified three risks: colour-only decisions, pair scores that hide greedy context, and rounded values that obscure equality. The implementation addresses these with explicit states, a three-instance fixture, both OKS directions and an exact-boundary action. Screenshot review removed an unnecessary metric-button transition and clarified unavailable-pair explanations.

Next local milestone: evaluate a read-only SLEAP selection adapter or explicit .slp import, preserving instance/skeleton/node order and actual confidence fields. Verify against real host data structures before promising GUI integration. Researcher feedback remains deferred until Ahmed chooses to share a concrete artifact. Further publication follows the lab’s exact-diff approval and PR process. Outreach remains deferred.

## Licence

Demo source and generated bundle: GPL-3.0-only. Upstream sleap-nn source: GPL-3.0. See [COPYING](COPYING) for full terms and retain this attribution and source-lock when redistributing. Synthetic coordinate fixtures were constructed for this demonstration; they are not scientific observations.
