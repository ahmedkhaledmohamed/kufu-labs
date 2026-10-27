# Workflow-validation pilot: inspect pairwise overlap while tuning duplicate filters

Current handoff: this is a proposed researcher-validation protocol, not a completed study. A later approved [synthetic demo](../../projects/overlap-inspector/README.md) demonstrates one pinned numerical path. No participants, recordings, measured workflow benefit or outreach are authorised by the lab-hub goal.


Status: validation direction approved; concrete session materials and first-contact text prepared locally. Outreach and implementation remain pending their specific approval. Decision basis and primary sources: [research audit](README.md). No new software, recording download, or user session was performed for this proposal.

## Decision

Recommend a small workflow-validation pilot for researchers choosing how to remove duplicate pose instances from existing multi-animal predictions. Defer a software build until the task and benefit are confirmed with current users. Reject another general-purpose pose editor, tracking system, or QC dashboard.

The recurring underlying work is reviewing unreliable multi-animal predictions and adjusting processing settings. Direct demand for this exact score display comes from one original requester in [SLEAP discussion #2815](https://github.com/talmolab/sleap/discussions/2815), cross-posted as [issue #2816](https://github.com/talmolab/sleap/issues/2816), with their own August follow-up. Do not count those as independent requests. Other researchers' duplicate/assembly and identity reports establish related recurring work, not adoption demand for this interface.

## Beneficiary, task, and current workaround

Beneficiary: a researcher who already has a SLEAP project with predicted instances and wants to suppress duplicate detections while preserving distinct animals, including close-contact cases.

Task: inspect a suspicious pair in one frame, understand the scores used by the chosen overlap filter, and choose a method/threshold to test. The reported workaround is guessing the numeric similarity needed to choose settings. Repeated runs and their time cost are plausible consequences to confirm, not measured or explicitly counted facts from that report. A capable user's existing notebook, console, QC panel, or script is also a baseline; do not compare only against uninformed guessing.

The current GUI has filter settings, model metrics, and anomaly/QC review. The inspected surfaces did not expose the requested two-instance post-processing comparison. Showing a metric might still fail to help: overlap does not establish that two poses belong to one animal, and the real need may be model repair, node exclusion, or a different metric. Those are reasons to stop or redefine the task with evidence.

## Gate A: confirm the workflow before constructing anything

Use the [session protocol, blank task record and decision sheet](WORKFLOW-STUDY.md).

After explicit approval of outreach and the session protocol, seek three independent researchers who have recently tuned duplicate-instance filtering; one may be the original requester. Include a second person even if the first strongly likes the idea.

Ask each to demonstrate their last actual case using the current software: inputs, settings, steps, existing workaround, number of reruns, active time, and what made the result acceptable. Ask how often they encountered it in their own last three analysis sessions. Preserve an unknown rather than inventing a recall-based frequency estimate. A preference for a proposed interface is not task evidence.

Continue only if at least two independent users demonstrate the same current task and a burdensome workaround that existing supported controls or a simple existing script do not already resolve adequately. If the original reporter's need is now solved, or the others have no such task, record a no-go for implementation. The number two is a practical pilot gate, not a prevalence or statistical claim.

No researcher has agreed to participate. Public issue authors are possible contacts only after authorisation; the investigation has not contacted or recruited them.

## Gate B: establish the metric contract

Freeze one processing path and source revision before offering a readout. The audited SLEAP develop revision is `d24a98fbc2f69d84c6c080bab4e826c4992ac76f`; the latest release API reported v1.6.6. The audited sleap-nn revision is `a2b97fe0a7d908813f0d555df284307fd5060fd5`.

The current tensor filter and the legacy label-level helper are different integration paths. OKS uses the first instance's bounding-box area and therefore need not be symmetric. The tensor NMS implementation passes candidate then retained instance; the legacy helper passes retained then candidate. Resolve the intended version and argument order with maintainers rather than assuming equivalent decisions or changing filtering semantics inside this pilot.

A technical check, separately approved before execution, must cover missing nodes, no shared valid nodes, degenerate bounding boxes, unequal instance sizes, reversed pair order, score ties, and threshold equality. Compare against the actual selected filter path on constructed inputs. Label reference/candidate roles and normalisation; do not call the metric a generic probability or QC anomaly score.

Do not promise a full-frame suppression preview from one pair. Greedy suppression order can involve additional instances. The initial intervention is a read-only metric report, not an automatic deletion decision. Stop if there is no maintainable, agreed route to the selected path's exact semantics.

## Gate C: measure benefit with an existing-metric readout

Start with a manually prepared, source-verified readout using the selected existing metric implementation. This can test whether the information helps without committing to a GUI feature. It is a future authorised study intervention, not an artifact already produced or a substitute for verifying metric correctness.

Each of three participating researchers works through six matched cases per condition: their best existing workflow and the same workflow with the readout available. Counterbalance order and use different matched cases to reduce learning effects. Include genuine close-contact animals, true duplicate predictions, a flipped duplicate, missing nodes, and a tail/outlier case if applicable to the selected project. Keep the first pilot to one host and one project type.

Two domain-competent reviewers should label whether each proposed removal is acceptable from the authorised visual evidence and experimental context. Mark genuinely ambiguous cases unresolved. Metric agreement alone is not the reference standard.

Record active task time, number of trial runs, result quality, and the scientist's explanation of the decision. Assess the chosen settings against the actual selected full-frame filter on the reference subset, not just a subjective pairwise classification. A provisional continuation target is at least 25% lower median active time without any additional erroneous removal of genuine instances on the reviewed subset. This is an explicit design threshold, not a predicted effect. Report each participant's result and uncertainty; a three-person convenience pilot cannot establish population-level efficacy.

Stop if the readout does not improve the existing workflow, increases inappropriate removals, is only cosmetic, or cannot be interpreted reliably. Do not rescue the result by reporting only satisfaction or changing the success threshold after observation.

## Conditional integration if the study supports it

Only after the workflow and benefit gates pass, consider an upstream SLEAP action or small panel selecting two predicted instances in the same frame. Use existing project identities and coordinates; select pair A/B explicitly rather than redesigning global selection or the QC dashboard. Show metric name, value, reference role, node/NaN policy, and processing version. Preserve original labels and project files; no inference, retraining, automatic removal, or account-backed service belongs in this first feature.

Exclude node-subset filtering, identity restitching, broad threshold optimisation, and downstream behavioural analysis. The requester's tail-node concern is important, but if it is necessary for usefulness it invalidates this scope rather than silently expanding it.

Maintain the contribution upstream if wanted. The GUI uses PySide6, requires Python 3.11–3.13, and depends on sleap-io. The inference backend is optional and Torch-based. Whether a read-only inspector can use an agreed lightweight metric API without making the optional backend mandatory remains unresolved. Do not copy or vendor backend code to conceal that dependency decision.

## Data, access, licences, and resources

For technical checks, construct a few dozen tiny pose pairs with node names, coordinates/NaNs, and instance scores; target under 1 MB total. No videos or weights are required for these checks. Synthetic examples cannot establish scientist benefit or whether two real overlapping poses represent distinct animals.

For workflow validation, access to a small, explicitly authorised researcher-owned project and visual reference is a prerequisite, not an access claim. Prefer researchers keeping recordings on their own machines and sharing only permitted deidentified pose extracts and approved session observations. Confirm permission for derived labels and any viewed/copied images; do not reuse issue attachments merely because they are public. No existing recording/data licence was established and no such data were downloaded during this goal. Do not redistribute study data without separate permission.

Code licences are distinct: SLEAP's LICENSE identifies Clear BSD despite shorter project metadata; sleap-io is BSD-3-Clause and sleap-nn repository metadata reports GPL-3.0. Preserve notices and let the upstream project select the accepted API/dependency boundary. None of these software licences grants recording or model rights.

Proposed effort cap: six hours for workflow confirmation and protocol refinement, then at most ten more hours for the correctness/readout study before a continue/stop decision. Sessions depend on participant availability, so this is effort, not a calendar promise. Proposed local limits are 5 GB total pilot working storage, 4 GB peak process memory, CPU only, no training, no model weights, no paid services, and no bulk recordings. Environment size, import cost, UI latency, and study time savings are unmeasured. Stop and reassess if the supported setup or metric path cannot meet these limits.

## Outputs and completion decision

Deliver a deidentified task record, baseline workflow, metric-contract record, authorised-input manifest, per-case decisions/timing, negative results, and a continue/stop recommendation. A successful technical display is insufficient; the primary outcome is researcher task performance at equivalent result quality.

The current research supports this bounded validation step, with no-go on a standalone app and defer on implementation. Maintainer approval, participant access, practical benefit, correctness of a future implementation, and broad demand remain unproven. The existing movement filtering proposal and deletion report continue independently.

Approval for a next phase must explicitly cover outreach/participants and any computation or implementation selected from this protocol. This document does not authorise a new public post, account, push, PR, merge, expense, data download, or build.
