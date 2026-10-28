# Scientific software investigation plan

Prepared: 26 October 2026. Status: research milestone and approved local technical pilot complete; full-diff review and external validation remain pending. Context and source links: [research record](README.md).

## Current direction: compare candidates across domains

Updated 27 October 2026. The first pose-tracking pilots are technical experiments, not a commitment to specialise the lab in that domain. The earlier audit and selection below remain historical evidence for that first pilot.

Before selecting the next build:

1. Compare a concrete candidate in microscopy, biomedical evidence, accessibility, bioinformatics, neuroscience timing and research methods. Include the pose pilots as existing work, without giving them automatic priority because code already exists.
2. For each candidate, refresh the primary report and existing tools; record who encounters the task, evidence strength and date, what remains unsupported, and reasons not to build. Do not equate a broad scientific priority with a software defect.
3. Identify a supported integration boundary, permitted small inputs, a baseline and a demonstrable before/after result. Prefer a host contribution or adapter where it addresses the gap. A constructed demo must be labelled separately from a real reported failure.
4. Compare likely benefit, technical difficulty, ability to measure an individual contribution, maintenance and evidence still needed using qualitative judgments. Do not invent comparable impact scores from unrelated studies.
5. Propose one bounded next pilot only when a remaining gap survives that comparison. If none does, report that result and investigate further rather than filling the lab with speculative applications.

This comparison requires no outreach, new accounts, paid services, recordings or model weights. It can establish a technical demonstration and its limits; researcher benefit remains unvalidated without appropriate workflow evidence. Refreshing the sources and running these candidate comparisons are next work, not completed results of this overview change.

## Goal and completion condition

Identify one worthwhile, sustainable scientific-software contribution and demonstrate it in a bounded pilot. Completion requires a specific beneficiary, a documented task that existing tools do not adequately support, an agreed baseline, a measurable improvement, and a practical integration and maintenance route. A shortlist, polished interface, or challenge score alone is insufficient.

The immediate research goal is fulfilled by the submitted initial PR, [comparative audit](AUDIT.md), and [movement pilot proposal](../../projects/movement-edit-filtering/PILOT.md). The broader goal above still requires validation of usefulness in a researcher's workflow; the technical synthetic result is now recorded. Ahmed approved the bounded movement pilot, which now has a local implementation and synthetic evaluation. Scientific usefulness and maintainer acceptance remain unvalidated.

## Scope and decisions

- Investigate label-free microscopy and behavioural neuroscience first; retain biomedical evidence retrieval as a lower domain-switching-cost alternative.
- Retain drug-safety modelling and epilepsy evidence access as alternatives with additional expertise or maintenance requirements.
- Use public or properly authorised research data. Establish the selected dataset's licence and access conditions before downloading or reusing it.
- Prefer an existing project's missing capability to a new application when both solve the same problem.
- Keep software research separate from claims of clinical benefit. The first pilot should support a research task.
- Research and local preparation can proceed within approval. Contacting people, publishing externally, committing to a partner, or incurring service costs requires the applicable explicit authorisation.
- Follow the repository's branch, diff-review, contribution-record, and PR process. Leave merging to Ahmed unless explicitly instructed otherwise.

## Phase 0: Preserve the investigation

Deliverables: the research record, this plan, project-index link, reviewed diff, and submitted PR.

Initial work completed:

- [x] Read the selected repository instructions and preserve the modified original checkout.
- [x] Fetch upstream main and create an isolated feature worktree.
- [x] Verify the personal repository owner and effective Git author/committer identity.
- [x] Draft the research record with sources, uncertainty, alternatives, and integration routes.
- [x] Run branch-specific contribution extraction; no matching prompts were returned from the repository's extraction context. Do not create a trail file for that result.
- [x] Validate Markdown structure, relative links, whitespace, and private-content patterns; inspect the full diff before approval.
- [x] Obtain approval of the full diff, verify the commit matches it, and mark commit `23e44fdb29ab57f20b3d3e464df08264a5406cf6` with the required no-prompts gate result.
- [x] Push the approved commit and submit [PR #228](https://github.com/ahmedkhaledmohamed/Personal/pull/228). Subsequent investigation edits remain local until separately reviewed.

Exit: a real submitted PR; a comparison page or local branch is not completion. The PR remains open for review.

## Phase 1: Audit the evidence and existing implementations

Suggested timebox: two focused research sessions. This is an effort estimate, not a deadline.

For each of the first three candidates, record the following in the research record:

1. The exact scientific task, beneficiary, and evidence supporting the need, with publication or review dates.
2. One to three relevant existing tools or baseline methods, including recent releases and issue discussions.
3. A concrete remaining gap; label it as documented by users, inferred from papers, or unverified.
4. Representative public data, licence, access procedure, sample grouping, download size, and required hardware where documented.
5. The host environment and precise input/output boundary; check the installed or current supported API before implementation.
6. The scientific expertise needed to judge correctness and a plausible route to finding a collaborator.
7. Maintenance burden and reasons the contribution might add no value.

Desk audit completed in [AUDIT.md](AUDIT.md): pinned baseline revisions, existing capabilities, licences/access, representative data or structures, integration boundaries, resource uncertainties, maintenance, and retain/defer decisions for all three domains. Generic plugins were rejected. Several specific movement ideas were also rejected because open PRs already address them. A remaining explicit-edit filtering gap is supported by issue #1027 and current source. At the desk-audit stage no installations, data/model downloads, runtime tests, or user interviews had occurred. The later approved pilot installed the host dependencies and ran synthetic tests; it downloaded no research recordings or model weights.

Exit: a compact evidence card for each candidate and explicit reasons to retain or reject it. If no gap survives comparison, switch to an existing project's concrete request instead of inventing a product.

## Phase 2: Select two tasks and validate the workflow

Suggested timebox: one synthesis session, followed by collaborator availability. Prepare outreach drafts for review; do not send messages without explicit instruction.

- Identify a relevant imaging facility, neuroscience lab, or maintained project for each surviving candidate.
- Prepare a short explanation of the proposed help and ask for a recent example of the task and its workaround.
- Request workflow evidence rather than reactions to a product idea: inputs, steps, recurring failure, frequency, time spent, and existing alternatives tried.
- Establish which part software can change and which part depends on missing data, scientific uncertainty, training, or organisational resources.
- Agree what would make a small contribution useful and who can assess its correctness.

Exit: two specific task descriptions, with the strongest available workflow evidence and remaining access limits. A positive opinion about an idea is insufficient. If collaborators are unavailable, label any public-data experiment as exploratory and avoid claiming user validation.

Desk-research result: the two compared concrete tasks are (1) retaining explicit manual corrections while dropping other unscored pose predictions and (2) evaluating fluorescence predictions across acquisition groups for a specified measurement. The first has a public workflow request and source-confirmed API gap; the second lacks a selected measurement and reviewer. External workflow validation has not occurred and remains a later gate if authorised. Public evidence supports the technical pilot, not a claim of user validation.

## Phase 3: Choose one bounded pilot

Compare surviving tasks using evidence strength, value to the beneficiary, personal interest, technical feasibility, access to expertise, workflow fit, maintenance, and ability to attribute an actual contribution. Use reasoned judgments rather than invented numeric scores.

Write a one-page pilot specification covering:

- Beneficiary, concrete task, existing workaround, and the gap to address.
- One supported dataset or data structure and one host application.
- Existing baseline and the smallest proposed improvement.
- Scientific reviewer or explicit limit on independent validation.
- Measures of accuracy, usefulness, and effort; conditions that would stop the work.
- Local compute/storage budget, dependency choices, and data/licensing constraints.
- Output artifact, reproducibility record, and intended contribution destination.

Draft complete: [PILOT.md](../../projects/movement-edit-filtering/PILOT.md) specifies the recommended task, baseline, integration, acceptance criteria, resource caps, review requirements, and stop conditions. Ahmed subsequently approved the bounded implementation. Its result and remaining publication gate are recorded in the pilot document.

## Phase 4: Reproduce the baseline before adding a feature

Suggested timebox: one to three focused sessions, revised after installation and data inspection.

- Use an isolated implementation worktree in the selected repository and read its instructions.
- Obtain the smallest representative permitted dataset and establish an environment from the project's supported setup.
- Reproduce the selected baseline, recording versions, inputs, grouping, parameters, resource use, and known failure cases.
- Keep data outside version control unless its size, licence, and repository conventions explicitly support inclusion.
- Confirm that the failure being addressed occurs in the actual environment.

Completed for the approved technical pilot: reproduced baseline and failing new-policy tests at the inspected revision. The isolated host environment uses Python 3.13.2; inputs are constructed data. See PILOT.md for the reproduction commands and measured limits.

## Phase 5: Build and evaluate one improvement

- Implement the smallest change that addresses the confirmed task; add only the required integration surface.
- For microscopy: separate predicted and observed images; evaluate across held-out acquisition groups and inspect downstream measurement errors.
- For behavioural neuroscience: compare review accuracy/effort and document timestamp assumptions and consequences of annotation changes.
- For retrieval: assess evidence relevance, citation support, and unanswered cases against a baseline with independent review where available.
- Choose verification appropriate to the change and host-project requirements. Avoid tests that merely mirror implementation.
- Record negative results and limitations. Preserve the experiment if it establishes that the proposed feature is unnecessary.

Technical portion completed: optional edit-aware filtering, input validation, usage example, 15 new acceptance cases and 82 existing synthetic regressions passed. Native save/reload, lint, formatting, and targeted type checks passed. A subsequent offscreen Qt-widget/model-event demonstration passed in a fresh pinned worktree, with four existing conversion cases also passing. The two recording-dependent filtering cases, full CI, rendered GUI interaction, and external workflow evaluation remain unrun.

## Phase 6: Decide whether to continue

Review actual use, correctness, integration friction, maintenance cost, personal engagement, and the clarity of the contribution. Decide among contributing upstream, maintaining a focused tool, revising the task, or stopping.

Public release requires a suitable licence, portable outputs, documented support limits, and the repository's reviewed PR workflow. Disease outcomes or clinical utility must not be inferred from a successful research-software pilot.

## Handoff and next gate

The approved local movement pilot and subsequent programmatic widget-workflow verification are technically complete. The [review package](../../projects/movement-edit-filtering/REVIEW.md) contains a reproducible demonstration, exact-version result, upstream draft, and maintainer questions. Review its [full patch](../../projects/movement-edit-filtering/movement-pilot.patch), [results and commands](../../projects/movement-edit-filtering/PILOT.md), and [environment inventory](../../projects/movement-edit-filtering/movement-pilot-environment.json). Implementation branch: `feat/explicit-edit-filtering`, in the sibling worktree `movement-filter-provenance`. No commit or publication has occurred. The code demonstrates provenance-sensitive filtering on constructed data, not improved biological results or measured researcher benefit.

Before any new push, show the full repository diff, run the required contribution-record process, obtain approval of the exact change/commit, and mark it with the gate. The research PR remains at the initially approved snapshot unless separately updated. Do not merge it. Next steps are a publication decision and separately authorised maintainer/workflow review; Phase 6 cannot claim adoption or user validation yet.
