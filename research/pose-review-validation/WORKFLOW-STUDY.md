# Overlap-filter workflow confirmation materials

Status: archived, unsent study preparation. Outreach is deferred. No participants have been contacted for this study and no data have been received. A later approved synthetic demonstration exists; this is not a completed researcher study. The [pilot](PILOT.md) defines the overall gates and outcome criteria.

## First contact and qualification

Proposed first audience: the original requester in SLEAP issue #2816, who also authored its August example. Post one short question in that existing thread only after the exact message is approved. Do not treat the issue cross-post or follow-up as another participant.

The additional issue search found adjacent duplicate/identity reports, but did not establish two other qualified users of this exact workflow. Do not recruit those authors as though they had requested the same feature. Identify a second independent current task through an opt-in response or a separately reviewed targeted invitation. Do not contact a quota of unrelated people.

A qualifying case involves existing predicted instances, an actual duplicate-filter method/threshold decision, and a current workaround. Model-training trouble, generic identity swaps, or enthusiasm for a proposed interface alone do not qualify.

## Initial asynchronous questions

Ask whether the task still exists in their current setup, how they handle it today, and for a recent concrete example. A written answer can screen the case; it does not establish measured task duration or prove a new feature helps. Do not ask for recordings, project uploads, credentials, raw paths, or private institutional information.

Do not promise a feature, timeline, meeting availability, or a fix to the metric implementation. If an existing supported workflow solves the need, record that result and stop rather than persuading the person to want the proposed interface.

## Exact first-contact draft, not sent

Target: existing [SLEAP issue #2816](https://github.com/talmolab/sleap/issues/2816), addressed only to original requester `olinesn`.

@olinesn, is pairwise IoU/OKS inspection still a problem in your current SLEAP workflow? I'm assessing this request before proposing a GUI change.

Could you describe one recent case where you needed to choose `--filter_overlapping_method` or `--filter_overlapping_threshold`: what result you wanted, what you use today (GUI/QC, a notebook, or trial runs), and what remains difficult?

It would also help to know your SLEAP/sleap-nn versions and how often this came up in your last few analysis sessions. Unknowns or rough recollections are fine; I'm not treating them as measured timings.

No videos or project files are needed; a brief description here is enough. If a supported workflow already solves the need, that would be useful to know too.

## Optional 20-minute walkthrough

Arrange a walkthrough only after the person opts in and the facilitator, audience, and data-viewing scope are authorised. Ahmed can facilitate; no call, calendar invitation, or recording is created by these materials. The researcher keeps their project and recordings on their own machine unless a separate permission explicitly permits sharing.

| Time | Prompt or observation | Evidence to capture |
| --- | --- | --- |
| 0–2 minutes | Confirm the scope and what they are comfortable describing/showing | Task date, software versions, permitted observation scope |
| 2–7 minutes | Walk through the most recent actual duplicate-filter decision | Inputs, desired result, steps and settings, current workaround |
| 7–12 minutes | Demonstrate their best existing approach, if feasible | Active effort, waiting time separately, reruns, tools/scripts already used |
| 12–16 minutes | Explain how they knew the result was acceptable | Duplicate versus genuine overlapping animals, ambiguous cases, reference evidence |
| 16–20 minutes | Ask about recurrence and alternatives; summarise the task back | Occurrence in their last three analysis sessions, observed versus recalled burden, whether supported controls already solve it |

Keep the first walkthrough about the current task. Do not show a proposed metric card or ask leading questions about its usefulness before documenting the baseline. No numerical readout is prepared until Gate B resolves the metric contract.

## Blank task record

Make one deidentified copy of this template per qualifying task. Leave unobserved fields **unknown**, not zero. Do not commit participant answers or shared project data automatically; agree what may be retained and summarised first.

| Field | Observation |
| --- | --- |
| Participant code | Unassigned; use a non-identifying study code |
| Observation mode | Written account / live demonstration / other |
| Permission to retain a paraphrased account | Unknown |
| Date of the described task | Unknown |
| Current SLEAP / sleap-nn / sleap-io versions | Unknown |
| Existing predictions or another task type | Unknown |
| Exact decision being made | Unknown |
| Desired output and acceptance criterion | Unknown |
| Existing GUI, QC, notebook, or script workaround | Unknown |
| Ordered steps taken | Unknown |
| Method, threshold, node/visibility assumptions | Unknown |
| Active task time | Unknown; observed or recalled must be labelled |
| Compute/wait time | Unknown; separate from active work |
| Trial runs | Unknown; observed or recalled must be labelled |
| Occurred in each of last three analysis sessions | Unknown / unknown / unknown |
| Consequence of the difficulty | Unknown; no inferred scientific outcome |
| Evidence for duplicate versus genuine animals | Unknown |
| What remains ambiguous | Unknown |
| Existing supported alternative tried | Unknown |
| Independent project/workflow from other records | Unknown; do not infer from account names |
| Same task as other qualifying records | Unknown |
| Candidate feature unnecessary because | Unknown |
| Follow-up permission, if any | None assumed |

Public reports can be paraphrased as public evidence with source links; keep them distinct from consented study observations. A person's description is not an independent correctness annotation for the later comparison.

## Gate A decision sheet

**Current state:** zero confirmed study participants and zero observed qualifying task walkthroughs. One direct public requester, their follow-up, and broader related reports support asking the first question.

Continue to technical/readout work only when two independent users show the same current task and a burdensome workaround not adequately covered by supported controls or their best existing script. Use the third participant to test variation rather than inflate prevalence. The protocol's convenience sample cannot estimate population demand.

Stop/defer if the task is obsolete, the current tool already meets the need, only a different task is observed, permissions are insufficient, or no second independent case is found within the six-hour effort cap. Recruitment waiting time is calendar delay, not evidence of benefit or permission to broaden outreach.

## Later outcome worksheet, not yet in use

Gate B must fix the actual metric path and its directional/NaN/order semantics before any intervention. Gate C compares the best existing workflow with a verified readout using counterbalanced matched cases. Record per case:

| Measure | Baseline | Readout condition | Evidence type |
| --- | --- | --- | --- |
| Active seconds | Not measured | Not measured | Timed, excluding compute wait |
| Compute-wait seconds | Not measured | Not measured | Timed separately |
| Trial runs | Not measured | Not measured | Observed |
| Genuine instances incorrectly removed | Not assessed | Not assessed | Independent reference review |
| Duplicate instances retained | Not assessed | Not assessed | Independent reference review |
| Ambiguous cases | Not assessed | Not assessed | Preserve uncertainty |
| Chosen settings and explanation | Not collected | Not collected | Participant account |

The provisional 25% median active-time target and no-additional-erroneous-removal criterion come from the pilot, not from collected results. Do not calculate an improvement from blank or recalled values, change criteria after observing outcomes, or treat a correct metric calculation as researcher benefit.

## Publication and implementation boundary

These are study-preparation artifacts only. The first public question needs exact-text/audience approval. Additional contacts, calls, data access, computation, implementation, account creation, spending, pushes, PRs, and merges retain their applicable approval requirements. Keep the earlier movement contributions separate.
