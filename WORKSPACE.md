# Kufu Labs workspace

## Current task

The scientific continuation on `feat/execution-validation` broadens the existing MNE candidate's supported-input checks. A deterministic 160-case matrix uses the unchanged pinned source/patch and actual parameterized driver. It records 60 baseline onset changes and 40 attachment-induced truncating-index changes. The candidate preserves every tested onset, duration and original index; all controls and 640 exported array-role hashes pass. Two original references already truncate to the preceding sample. These are reported as a limit, not hidden or counted as an annotation-attachment failure. Rounded lookup recovers every requested sample in the matrix.

The continuation also retains PR #26's downloaded-evidence checker: it verifies array hashes, shapes/dtypes and report/API identity, recomputes NWB changed-value/row counts, and checks MNE signal-preservation claims. Actual prior hosted bundles pass; eight corrupted bundles are rejected.

The new runner is local and reviewable. The proposed CI integration reuses the existing CPU scientific job, retains reports/arrays and publishes a fresh summary; it creates no additional hosted submission, dependency, infrastructure or upstream patch. CI integration and source publication remain pending exact-diff review. See the [project record](projects/mne-annotation-onsets/README.md#generated-input-matrix).

Owner-auth PR #27 is merged at `71e705dbc6f2eadeaeef033290fa5f453b814c89` after its retried hosted check passed following the UTC-day reset. Production run [41147986046](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/41147986046) passed all four jobs and promoted the release. Independent checks matched the canonical production manifest and four sampled assets to the tested artifact, confirmed protected anonymous access, and verified both hosted result bundles and stopped Sandboxes. Owner ID and session secret have been provisioned in Vercel production/preview, but App client settings are still absent. Production reports sign-in unavailable and its auth route returns the expected unconfigured response; no working live sign-in is claimed. PR #26 remains open at its earlier approved snapshot; this expanded combined diff requires fresh approval before its head is updated, followed by a separate merge decision. Do not bypass required checks or change the protected branches directly.

No outreach, spending, new accounts, research recordings or model weights. Preserve research worktrees and licences. Tests establish bounded software properties, not biological correctness, physical-clock accuracy, adoption or user benefit. Any source push/PR still requires approval of the exact diff; merge is separately authorised per PR.

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
