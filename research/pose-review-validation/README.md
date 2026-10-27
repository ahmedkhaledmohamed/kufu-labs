# Pose-review problem validation

Current handoff: the research-only decision below is historical. A later approved [synthetic overlap demonstration](../../projects/overlap-inspector/README.md) now exists, but researcher validation remains unrun. Outreach is deferred; no recruitment draft is authorised for sending.

Historical status: desk-research decision complete; recommended workflow validation of pairwise overlap inspection, deferring software implementation. Started 27 October 2026 UTC. Working branch: `research/pose-review-validation`, isolated worktree `scientific-lab-pose-validation`, based on lab main `78375803a4326b2a26d725568bea84b95a169e35`.

## Decision

Select **pairwise overlap inspection while tuning duplicate-instance filtering** as the next task to validate. The [bounded pilot](PILOT.md) starts with current-workflow confirmation, then measures whether exact metric readouts improve task time without increasing mistaken removals. Do not build a new application or feature yet.

Evidence supports related recurring multi-animal review work and one specific unresolved score-inspection request, not broad demand or measured benefit. A workflow-validation pilot is justified; a software MVP is not yet justified. The protocol has explicit data, correctness, dependency, participant, and outcome gates and a stop decision if they fail.

## Goal and completion condition

Find one recurring researcher task that existing pose-review tools handle poorly, then produce a decision-ready bounded pilot or an evidence-based stop/defer decision. A software bug, maintainer interest, or a working prototype does not establish researcher benefit.

Record the beneficiary, actual workflow and workaround, evidence of recurrence/frequency and consequences, current tool coverage, data/access/licence and resource requirements, integration boundary, independent validation method, measurable outcome, and stop conditions. Separate observed reports from hypotheses and unresolved assumptions.

No outreach, public posts, accounts/forks, new pushes, merges, spending, recording/model downloads, or pilot implementation is authorised by this research goal. Preserve pending PRs and earlier contributions.

## Current contribution state

At the goal's initial live check, movement issue [#1027](https://github.com/neuroinformatics-unit/movement/issues/1027) had the approved design question and no maintainer response; [#1174](https://github.com/neuroinformatics-unit/movement/issues/1174) had no comments. Lab [PR #3](https://github.com/ahmedkhaledmohamed/scientific-software-lab/pull/3) was open at `d89bab59eee2626e46899d36dad9be8eaa70b05e`. Refresh these mutable states before relying on them again.

The filtering proposal and deletion-provenance report remain separate contributions in progress. Neither validates demand for a new pose-review product. Do not let the convenience of these codebases determine the next scientific problem.

## Initial primary-source evidence

| Source and date | Research workflow and reported friction | Existing response/workaround | What it establishes and leaves unknown |
| --- | --- | --- | --- |
| [DeepLabCut issue #2466](https://github.com/DeepLabCut/DeepLabCut/issues/2466), opened 18 December 2023, follow-up January 2024 | Multi-camera marmoset tracking; the researcher reported too many identity/assembly errors to correct manually, with labelling work multiplied across camera projects | Maintainer suggested identity-independent assembly/stitching and diagnostic affinity plots, then parameter adjustment; the author reported that an initial suggested change did not improve results | A concrete workflow and manual burden in DLC 2.3.6. No measured review time, representative population frequency, or demonstrated persistence in current versions. Closed/stale state is not proof of a solution. |
| [SLEAP discussion #1503](https://github.com/talmolab/sleap/discussions/1503), started 15 September 2023 | Two-mouse social-behaviour tracking; researcher reported repeated identity switches despite substantial targeted labelling, then tried an identity-aware model | Model/tracking configuration investigation; full reply chain has now been reviewed; see the follow-up audit below | An independent report in another tool and animal context. It supports recurrence across these two reports, not prevalence, current demand, or a missing editor. |
| [Official SLEAP proofreading tutorial](https://tutorial.sleap.ai/proofreading/), inspected 27 October 2026 UTC; page copyright 2024 | Review predictions, locate likely close-contact errors, correct a track identity, retain an original version | Built-in centroid-proximity seekbar, track reassignment propagated forward, save-as workflow | Existing review and correction capability; a generic identity editor would overlap. Tutorial instructions are not evidence of typical review duration or residual difficulty. |
| [Current DeepLabCut multi-animal guide](https://github.com/DeepLabCut/DeepLabCut/blob/main/docs/maDLC_UserGuide.md), inspected 27 October 2026 UTC | Assembly, tracklet stitching, diagnostic inspection, identity/bodypart correction | Existing tracklet-refinement GUI and parameter controls | Strong reason to audit current tools before proposing any new review UI. Remaining gap has not been demonstrated. |

No linked recording or attachment was downloaded. No raw user logs or local paths from discussion posts were copied into the lab. Tool documentation was used as a capability source, not an independent report of user demand.

## Candidate tasks to compare

1. Reduce effort locating and correcting consequential identity switches. Two dated workflow reports support the pain; existing editing and review heuristics substantially overlap. Need current independent reports and a specific remaining task.
2. Decide which low-confidence or suspicious frames warrant review. Plausible, but no independent workflow evidence has yet been established here. Audit current uncertainty/QC and active-learning tools before retaining it.
3. Determine whether pose corrections or filtering choices materially change a downstream behavioural measure. Plausible connection to scientific decisions, but no direct researcher request, standard task, or inadequate baseline has been established. Do not assume that a sensitivity dashboard is wanted.

## Evidence discipline

Two independent dated reports show two observed instances, not a count of affected labs or a percentage of recordings. Self-reported many errors and too much manual work are qualitative observations, not elapsed-time estimates. Old-version failures need reconciliation with present tool versions. A maintainer suggestion does not establish that the workaround succeeded; an unanswered/stale thread does not establish that today's problem is unsolved.

## Investigation steps completed

- Reviewed the SLEAP reply chain, current correction/tracking/QC source and documentation, and Lightning Pose diagnostic coverage.
- Added recent primary reports and explicitly retained solved/partly solved cases as counterevidence.
- Compared five task variants, rejected duplicate/in-progress features, and selected one bounded workflow-validation task.
- Specified constructed technical inputs, prerequisites for permitted real-workflow evidence, outcome measures, resource limits, API uncertainty, and stop/defer gates in [the pilot](PILOT.md).

No experiment has been run and no collaborator, prevalence estimate, architecture, or new build is selected. This record is a local draft pending the normal publication review process.

## Follow-up audit: recent workflows and current coverage

### What changed the assessment

- [SLEAP #2457](https://github.com/talmolab/sleap/issues/2457), opened 6 November 2025, contains the original two-mouse identity-switch report plus two other accounts describing similar trouble. A maintainer identified model/tracker configuration confusion; the original author reported some improvement but remaining close-contact failures in December, and another user asked about a resolution in March 2026. This supports recurrence across those reports, not a frequency estimate or proof that current 1.6.6 fails.
- [SLEAP #2529](https://github.com/talmolab/sleap/issues/2529), 5 January 2026, describes multi-mouse bottom-up inference producing extra incomplete skeletons despite additional labelling, preventing reliable tracking. This is an observed duplicate/assembly workflow problem; it is not independently a request for a pairwise-metric panel.
- [SLEAP #2666](https://github.com/talmolab/sleap/issues/2666), 31 March 2026, reports wing-side swaps in fly mating videos passed to SimBA. The animal can change orientation relative to the camera, so the meaning of a swap requires domain review; a geometric flag cannot establish an error by itself.
- [DLC #2867](https://github.com/DeepLabCut/DeepLabCut/issues/2867), February–June 2025, describes identity problems in a 3.0 release candidate. A partial fix was offered; the author reported remaining errors, then maintainers pointed to newer models. This is counterevidence to treating old failures as a new editor requirement.
- The complete reply chain for [SLEAP #1503](https://github.com/talmolab/sleap/discussions/1503) ends with the author reporting improved predictions after changing model family. It is a troubleshooting example with partial progress, not evidence that a missing review UI is the cause.

No lab count, hours saved, error rate, or current-version failure rate can be inferred from these threads. Multiple commenters are distinct reports within a selected support population; they are not a representative sample, and distinct accounts do not verify independent laboratories.

### Current tools that rule out broad builds

SLEAP's [tracking/proofreading guide](https://docs.sleap.ai/v1.6.5/guides/tracking-and-proofreading/) supports re-tracking precomputed predictions and built-in identity correction. Its [QC guide](https://docs.sleap.ai/latest/guides/label-quality-control/) supports anomaly detection, a ranked review queue, configurable thresholds, explanations, and CSV export. The [Lightning Pose evaluation tools](https://lightning-pose.readthedocs.io/en/v1.9.2/source/user_guide/evaluation.html) already offer prediction comparison and diagnostic metrics via FiftyOne/Streamlit. [refineDLC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12744387/) is another existing post-processing pipeline. These capabilities weaken generic editor, cleaning, and QC-dashboard proposals.

Versioned documentation can lag: the repository's latest release API reported SLEAP **v1.6.6**, published 20 October 2026. The inspected develop revision is `d24a98fbc2f69d84c6c080bab4e826c4992ac76f`. The annotated v1.6.6 tag resolves to that same commit. Its Python range is 3.11–3.13, GUI backend PySide6, and sleap-io requirement is `>=0.9.3,<0.10.0`. The optional inference backend is sleap-nn `>=0.3.4,<0.4.0`. No environment was installed for this audit.

Solved cases matter: [discussion #2512](https://github.com/talmolab/sleap/discussions/2512) and [issue #2025](https://github.com/talmolab/sleap/issues/2025) document fixes/new controls for repeated-inference duplication and project matching. Their historical failures cannot justify a separate duplicate-cleanup application today.

### Specific candidates retained or rejected

| Task | Evidence and overlap | Decision at this stage |
| --- | --- | --- |
| Generic identity correction/review queue | Recurring complaints, but mature correction, re-tracking, seekbar and QC workflows exist; causes include model configuration and actual prediction errors | Reject another generic editor; insufficient remaining task definition |
| Custom left/right pairing for QC | Direct [request #2806](https://github.com/talmolab/sleap/issues/2806), but [draft PR #2810](https://github.com/talmolab/sleap/pull/2810) already implements related symmetries UI | Reject competing implementation; an open issue alone does not mean unclaimed work |
| Inspect pairwise overlap scores while tuning duplicate filtering | Direct original [discussion #2815](https://github.com/talmolab/sleap/discussions/2815), cross-posted to [#2816](https://github.com/talmolab/sleap/issues/2816), with an August follow-up about metric choice; current GUI inspection found no pairwise IoU/OKS comparison surface | Retain for a bounded workflow-validation proposal; one original requester and their follow-up, not two independent requests |
| Broad uncertainty/outlier selection | SLEAP QC and Lightning Pose already cover much of the proposed surface | Reject broad dashboard; no validated narrower missing task yet |
| Downstream behavioural sensitivity to corrections | Scientifically plausible, but no direct recurring workflow request or inadequate baseline established in this search | Defer; do not invent demand from scientific plausibility |

### Why pairwise inspection is different

The stated task is choosing a duplicate-filter method/threshold while proofreading existing predictions, rather than predicting poses or fixing identities generally. The requester describes guessing pairwise scores; the later example says OKS can miss a flipped duplicate and that IoU/node inclusion affects the decision. The proposed benefit is fewer tuning iterations or less active review time at equal retention of genuine animal instances. Neither benefit has been measured.

The issue body cross-posts the original discussion, so these are one source family. The broader duplicate/assembly reports support related recurring work, but do not prove that every affected researcher wants this interface. This distinction must be preserved in any pilot decision.

Pinned source inspection covered `sleap/gui/commands.py`, `app.py`, `widgets/qc.py`, `dialogs/metrics.py`, the training dialog, and QC detector/frame logic. Existing model metrics and QC anomaly scores are not the requested pairwise post-processing scores. Issue #2816 remained open/unassigned; issue-number and semantic PR searches found no matching implementation. This is bounded code/search evidence, not proof that no other plugin or unpublished work exists.

### Technical constraints that could stop the pilot

The inspected sleap-nn revision is `a2b97fe0a7d908813f0d555df284307fd5060fd5`. The current tensor `FilterPipeline` is Torch-based, while the legacy label-level overlap helper uses NumPy. Both have IoU and OKS routines, but OKS is directional because its scale comes from the first instance's valid-keypoint bounding-box area. The tensor NMS call passes candidate then retained instance, whereas the legacy NMS helper compares retained then candidate. Do not assume identical suppression decisions or label one unqualified score as the filter result. No runtime parity test was performed under this research-only scope.

A proposed read-only inspector must choose the intended processing path, preserve its node/NaN/normalisation/order semantics, and distinguish pairwise similarity from full-frame greedy suppression. A third instance can change suppression order. A QC anomaly score is a different quantity again. These are feasibility and scientific-correctness gates, not an instruction to repair either backend here.

Licences are separate: SLEAP's [pinned LICENSE](https://github.com/talmolab/sleap/blob/d24a98fbc2f69d84c6c080bab4e826c4992ac76f/LICENSE) says Clear BSD while [project metadata](https://github.com/talmolab/sleap/blob/d24a98fbc2f69d84c6c080bab4e826c4992ac76f/pyproject.toml) says BSD-3-Clause; sleap-io is BSD-3-Clause and sleap-nn's repository metadata reports GPL-3.0. No code was copied into a product. Any implementation must follow the host's chosen dependency/licence boundary rather than extracting an algorithm into a differently licensed GUI without review. No dataset or model reuse permission follows from these code licences.

## Final decision and handoff

The research-only goal is complete at the problem/pilot-decision level. The [pilot specification](PILOT.md) defines the beneficiary, baseline, measurable outcome, existing-metric intervention, data/permission prerequisites, source/API boundary, resource/effort caps, maintenance route, and stop conditions. It does not claim researcher validation, current sample access, metric parity, implementation feasibility, or effectiveness has already been demonstrated.

The exact UI intervention has one original requester, repeated in an August example; the wider identity/duplicate-review problem has several independent public reports. Duration, prevalence, tuning iteration counts, and end-to-end costs remain unmeasured. This is the principal reason to confirm the workflow before building.

Next authorised work requires approval of a specific validation phase and its outreach/data/computation boundaries. Until then, preserve this local report and the existing contributions. No messages, posts, downloads, installations, pushes, merges, expenses, accounts, or new pilot implementation occurred during this goal.

The recommendation should change if a supported existing workflow already provides the scores adequately, overlapping work is discovered, current users no longer have the task, metric semantics cannot be made unambiguous, or the readout fails to improve their actual decisions. A no-go under those conditions is a useful outcome.

## Validation preparation after direction approval

Prepared the [asynchronous screening/walkthrough protocol and blank measurement records](WORKFLOW-STUDY.md). No observations or participants are fabricated. A refreshed search for overlap-filter reports still identifies the original requester as the clearly relevant first contact; adjacent identity/duplicate reports are not automatically qualified participants.

The proposed first action is one exact question on existing SLEAP issue #2816, asking whether the task persists, the current workaround, and a recent example without requesting files. No message has been posted under this validation approval. Further contacts and study execution depend on explicit scope/participant permission and Gate A evidence.
