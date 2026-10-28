# Neuroinformatics implementation and learning plan

Prepared 27 October 2026. Working plan with an initial local implementation; publication and upstream submission remain separate gates. Read alongside the [cross-domain plan](PLAN.md) and [NWB stream-integrity experiment](../../projects/nwb-stream-integrity/README.md).

## Intended outcome

Build a useful scientific-software contribution while developing enough neuroscience understanding to explain the data, assumptions and scientific purpose. Keep Kufu's cross-domain discovery open. Neuroinformatics has explicit personal interest and earns an active experiment; it does not become the lab's exclusive subject.

The immediate engineering outcome is to prevent an inspection operation from changing data subsequently saved by a neuroscience conversion workflow. The learning outcome is to understand the difference between measured neural signals, data representations, analysis results and biological explanations. Neither outcome requires committing to a degree now.

## Work allocation and decision rules

Maintain one implementation at a time, supported by a small comparison of alternatives. Spend the majority of agent effort reproducing, implementing and testing the selected task. Keep evidence research bounded to decisions that could change that work. Company discovery and course browsing should not displace implementation.

Select work using documented task severity, evidence of an unsupported case, personal scientific interest, a supported integration route, reproducibility and maintenance. A small API change can be valuable if it prevents a consequential failure. A polished demonstration alone does not establish usefulness.

### Candidate comparison at this milestone

| Candidate | Current evidence | Integration and measurable result | Decision and remaining uncertainty |
| --- | --- | --- | --- |
| NWB streamed-data preservation | [Inspector #771](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771) reports recordings saved with zeros after pre-write inspection. Pinned source and a local reproduction support the mechanism. | Patch NWB Inspector's existing shape helper. Compare all saved values after actual HDF5/Zarr write and read, with uninspected controls. | Active bounded experiment. A related [HDMF dependency fix](https://github.com/hdmf-dev/hdmf/pull/1606) was open when checked; inspect it again before any upstream proposal. No adoption or prevalence measured. |
| Scientific-workflow accessibility | [JupyterLab #18815](https://github.com/jupyterlab/jupyterlab/issues/18815) provides keyboard reproduction steps, but [PR #18816](https://github.com/jupyterlab/jupyterlab/pull/18816) already proposes a fix. | A real keyboard task in the host application, followed later by affected-user assessment. | Avoid a competing fix. Another consequential current barrier would need reproduction; no new accessibility implementation selected. |
| Biological sample metadata | A [GEO completeness study](https://link.springer.com/article/10.1186/s13059-025-03725-0) documents missing annotations; [refine.bio](https://docs.refine.bio/en/latest/main_text.html#metadata) documents existing harmonisation and limitations. | A source-linked table/adapter for a field that is recoverable but missed by the selected baseline. | Retain. No specific sample/field or current implementation failure established. Do not infer unpublished information. |
| Analysis leakage checks | [DataSAIL](https://datasail.readthedocs.io/en/latest/) already offers biological data splitting against leakage. | A demonstrated dataset-specific failure and a missing adapter/check, rather than another general checker. | Retain as research; no remaining gap reproduced. |

This is a qualitative comparison of evidence currently available, not a completed hands-on audit of every domain or a ranking of scientific importance. The later [validation batch](VALIDATION-BATCH.md) records actual JupyterLab observations and a source-discovered metadata-preservation patch, including a PostgreSQL persistence follow-up. These are bounded results rather than domain-wide validation.

## Engineering milestones

Effort estimates below are planning ranges for focused agent sessions, not promised elapsed deadlines. Each milestone has an observable exit condition and can stop if the evidence changes.

| Milestone | Work | Exit condition | Status |
| --- | --- | --- | --- |
| 0. Verify the need, one session | Read the report, source, licence, competing fixes and contribution rules. Pin Inspector and dependency versions. | A reproducible failure in an existing host, an affected task and a credible mechanism. | Complete locally for NWB stream preservation. |
| 1. Implement and regress, one to two sessions | Reuse HDMF's existing shape helper, which handles the tested wrapped streams and stored resizable arrays. Test HDF5/Zarr, two iterator types, short and longer streams, and uninspected controls. | Every value preserved in the patched matrix; baseline loss reproduced; relevant existing checks remain effective. | Initial patch and replay complete; see project record for exact check scope. |
| 2. Challenge the patch, one session | Review all consumers of the shape helper, unknown dimensions, nested inputs, bare single-pass iterators and stored array behaviour. Compare the design with HDMF's existing helper and the proposed dependency fix. Verify the recorded patch reapplies cleanly and reproduces the result. | A bounded supported contract, regression evidence and explicit unsupported cases. | The original custom patch passed 343 unit tests, 5 skipped. Follow-up reuses the released helper and passes 341 tests, 5 skipped, with 11 regression cases. Both the helper-substitution experiment and the linked dependency PR preserved all 24 replay cases. Further version and independent review remain. |
| 3. Make it demonstrable, one session | Keep a one-command constructed-data replay, source pin, patch, environment and before/after output. Add the project to the hub with its runtime and limits. Integrate a pinned scientific CI replay before treating its result as a maintained release check. | A reviewer can run the actual inspection/write/read workflow and distinguish its result from a static explanation. | Local runner, outputs and hub entry exist. A follow-up now configures the pinned replay inside the existing required scientific check and passes fresh JSON results to the web build; its merged main run 40613968067 passed, with fresh production results independently verified. |
| 4. Prepare a contribution, one session | Refresh upstream and competing fixes. Prepare a concise mechanism, regression and design comparison. Keep upstream code changes in its isolated checkout and retain its licence. | Reviewable local proposal aligned with upstream's requirements. | Local [review package](../../projects/nwb-stream-integrity/REVIEW.md) prepared. Upstream guide requires issue approval before a PR; no outreach or upstream PR is authorised now. |
| 5. Assess usefulness, later | If authorised after a solid demonstration, ask an appropriate converter/researcher to assess their workflow and a maintainer to assess API compatibility. | Evidence that the contribution fits a real workflow, or a documented reason to revise/stop. | Deferred; technical tests do not establish adoption or research benefit. |

### Demonstration acceptance criteria

1. The same constructed array and parameters are used for baseline and patched runs; the source revisions and patch digest are visible.
2. The operation is the real NWB Inspector call followed by actual save and reload. Uninspected controls separate inspection effects from writer defects.
3. Compare the complete array, not only its mean or a screenshot. Preserve hashes and explicit zero-row counts because the inputs contain no zeros.
4. Short streams and multiple buffers are both covered. Preserve baseline inspection errors as observations; do not describe a locally observed error-reporting path as silently passing.
5. Clearly state that browser pages describe retained results; Python/HDF5/Zarr execution runs locally or in CI. A browser wrapper is optional and cannot replace the host replay.
6. Describe the beneficiary as researchers and engineers converting streamed neurophysiology data. Do not claim disease treatment, biological correctness, prevalence or time saved.

Stop or change direction if a released dependency already resolves the supported workflow, another accepted implementation supersedes ours, shape metadata cannot be interpreted safely, or regression evidence shows the patch weakens existing checks. A reproduction/regression contribution may remain useful even if our patch is superseded; credit the existing fix.

## Learning alongside the work

Start with approximately two 45-minute learning sessions and one 60-minute exercise each week. This is a suggested 2.5-hour weekly budget, adjustable to available time. The agent can prepare code and explanations; understanding the material requires the learner's own exercises and questions.

Use the freely accessible [Neuromatch Computational Neuroscience materials](https://compneuro.neuromatch.io/tutorials/intro.html) as the main course sequence. Its [prerequisite page](https://compneuro.neuromatch.io/prereqs/ComputationalNeuroscience.html) covers Python, mathematics and foundational neuroscience. Refresh mathematics where an exercise needs it rather than delaying all work for a complete prerequisite course. [INCF TrainingSpace](https://training.incf.org/) is a supplementary directory, not a second curriculum to finish.

| Step | Science to learn | Hands-on output | Check for understanding |
| --- | --- | --- | --- |
| Week 1: signals and measurements | Neurons, synapses and action potentials; differences between spikes, local field potentials and EEG/MEG. Use Neuromatch's introductory neuro videos. | Draw and annotate one synthetic two-channel time series, with axes, units and sampling rate. Read the NWB project explanation. | Explain what a row/channel represents and why a plotted waveform alone cannot establish a biological mechanism. |
| Week 2: time and sampling | Sampling interval, recording duration, regular versus irregular timestamps, noise and aliasing. Use the relevant Neuromatch signal-processing sampling material. | Change sample rate and timestamps in a small constructed example and predict the resulting time axis before running it. | Distinguish sample index from time and signal value from measurement unit. Explain what replacing samples with zeros could change. |
| Week 3: neuroinformatics workflow | Acquisition, metadata, conversion, NWB, HDF5/Zarr, streamed versus in-memory data, validation versus preservation. Read the [PyNWB introduction](https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_file.html) and [time-interval tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_timeintervals.html). | Run the baseline and patched replay yourself; inspect one saved constructed file and explain its schema. | Explain why validation must not consume data and why preserved bytes do not prove a valid scientific experiment. |
| Week 4: a model of a neuron | Membrane potential, integration, leak, threshold, reset and firing rate. Use Neuromatch's leaky integrate-and-fire exercise. | Run and modify a simple simulated neuron; write a prediction about how its firing changes with input before executing it. | Identify model assumptions and separate a simulation result from a claim about a measured brain. |
| Week 5: a scientific question | Model types, hypothesis, baseline, stochastic variability and uncertainty. Use Neuromatch's modelling-practice material and a targeted statistics refresher. | A short reproducible analysis answering one declared question about simulated input and firing rate, including a negative/control condition. | State what the result supports, what would falsify it and which assumptions limit it. |
| Week 6: choose the next depth | Revisit which activity was engaging: signals, models, data engineering or accessibility. | A short assessment of what was learned, what remains confusing and the next module/project. | Choose one next learning topic and one concrete contribution; avoid committing to an entire degree based on this first experiment. |

The engineering and science milestones can progress at different speeds. A utility patch may be ready before the science exercises are completed. Conversely, a useful learning experiment need not become a new product.

### Courses after the first steps

Neuromatch's [instructor-led computational neuroscience course](https://neuromatch.io/computational-neuroscience/) is an optional later step. Its page describes a three-week immersive schedule of roughly eight hours per day, five days per week, with prerequisites. That is a substantial commitment; start with its open materials now and reassess fit later. Recheck dates, fees and application requirements before considering enrolment. No account, enrolment or spending is part of this plan.

Neuroinformatics concerns the organisation, processing and sharing of neuroscience data and tools. Computational neuroscience focuses on quantitative models and explanations of neural systems. They overlap, but an engineering contribution to NWB does not on its own provide training in scientific modelling. This plan deliberately includes both a data-workflow experiment and a modelling exercise.

## FirstPrinciples and Canadian organisations to study

Reviewed 27 October 2026. These entries describe the organisations' own public positioning, not independently validated product performance, employment recommendations or evidence of an unmet software opportunity. The [Ontario Brain Institute portfolio](https://braininstitute.ca/portfolio-companies) is a useful ongoing discovery source; listed organisations span different stages and categories.

| Organisation | Publicly described work | What to learn from it |
| --- | --- | --- |
| [FirstPrinciples](https://firstprinciples.com/) | Scientific AI workflows and Theo, described as an AI physicist for fundamental science. Its [company profile](https://ca.linkedin.com/company/firstprinciplesinc) lists Toronto. | An adjacent example of software supporting scientific reasoning, tools and verification. Its stated physics focus is different from neuroinformatics. Product/research claims require assessment of underlying evidence. |
| [FirstPrinciples Foundation](https://www.firstprinciplesfoundation.org/) | A nonprofit supporting AI-assisted discovery in fundamental science, particularly physics. The company links to this foundation. | Keep the company/product and foundation descriptions separate; do not infer identical legal status from an old job listing. |
| [Cove Neurosciences](https://www.coveneuro.com/) | Brain-data analysis pipelines and applications to research and clinical trials. Also listed in the OBI ecosystem. | Study how brain measurements become analysis inputs and interpretable outputs, and which scientific expertise is needed alongside software engineering. |
| [Possibility Neurotechnologies](https://www.possneuro.com/) | Think2Switch, a brain-computer interface for controlling connected devices. Its [launch statement](https://www.possneuro.com/press-release) identifies Calgary. | A concrete intersection of neuroscience, accessible interaction and product design. Treat company use/performance claims as claims until their evidence is reviewed. |
| [Zentrela](https://zentrela.com/) | EEG-based product-effect research in non-medical settings; the site identifies a Hamilton research location. | Distinguish recording/analysis infrastructure, a classification model and the evidence required for a claim about a mental state. |

For each organisation worth a deeper look, inspect one technical publication or reproducible artifact and describe its input, method, validation and scientific limitation. Record whether open code or a suitable task actually exists. Do not infer an accessible API, collaboration opportunity or job opening from a homepage. No messages, applications, demos requiring registration or purchases will be initiated.

## Next execution sequence

The NWB CI release is verified. Review its upstream package and the [cross-domain validation batch](VALIDATION-BATCH.md), including the bounded zero-age component patch. The first learner session is the [neural-signals exercise](SIGNALS-EXERCISE.md). Company research remains a small, sourced reading list until it informs a concrete scientific or engineering question.

Publication follows the lab's full-diff and exact-commit approval process. This plan does not authorise merging, upstream outreach, patient information, research-recording or model-weight downloads, new accounts or paid services.
