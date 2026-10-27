# Scientific software opportunities

Research date: 26 October 2026. Status: exploratory research; no project selected and no prototype built.

## Purpose and current finding

Explore a sustainable software contribution, potentially released free and open source, with observable human benefit, an intellectually difficult problem, or a clearly identifiable individual contribution. These are alternative sources of satisfaction; a project does not have to maximise all three. This investigation does not assume that starting a business or obtaining a new degree is necessary.

Microscopy offers the clearest first experiment using public data. Behavioural neuroscience has the strongest connection to understanding the brain, but needs a collaborator to define a useful task. Biomedical evidence retrieval fits existing software and product skills, although it is competitive. None of these rankings establishes an unmet product need.

Research support can help scientists directly while its eventual effect on patients remains indirect and difficult to attribute. Assess whether the work itself is satisfying rather than relying on a future medical breakthrough to justify it.

The [next-steps plan](PLAN.md) defines evidence checks, selection criteria, and a bounded pilot. It is proposed for review; recommendations in this record are not commitments to build.

## Evidence and interpretation

- **Observed:** a primary source describes a problem, dataset, challenge, existing feature, or research priority.
- **Proposed:** a possible software contribution or integration inferred from those sources.
- **Unverified:** user demand, superiority to existing software, current issue reproducibility, installation, compute requirements, and adoption have not been established unless explicitly stated.

The work so far is online desk research. No researchers or patients have been interviewed, no challenge datasets downloaded, and no software evaluated hands-on. Challenge participation, public dataset availability, and clinical usefulness are separate questions. An old priority or completed competition does not establish that its problem remains open today.

## Where to find documented problems

| Resource | What it establishes | Limits and use |
| --- | --- | --- |
| [Convergent Research Gap Map](https://www.gap-map.org/) | Scientific bottlenecks connected to capabilities, publications, roadmaps, and relevant groups | Illustrative infrastructure map, not a comprehensive survey or ranked roadmap; entries mix research and proposals. Start with its [methodology](https://www.gap-map.org/about/). |
| [James Lind Alliance partnerships](https://www.jla.nihr.ac.uk/priority-setting-partnerships) | Patient, carer, and clinician priorities developed through evidence checking and prioritisation | Priorities can be broad and become dated. Check each partnership's report and evidence cutoff. [Method](https://www.jla.nihr.ac.uk/about-priority-setting-partnerships). |
| [OpenChallenges](https://challenges.synapse.org/openchallenges) | Aggregated biomedical computational challenge descriptions and links to original organisers | Documentation completeness varies; registry presence is not proof of an unresolved problem. The portal requires JavaScript; original organiser pages were used for detailed follow-up. [Platform paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13576655/). |
| [Grand Challenge](https://grand-challenge.org/challenges/) | Defined medical and biological imaging tasks, datasets, and evaluations | Distinguish active, upcoming, and completed phases; benchmark progress alone does not establish clinical benefit. |
| [NIH challenges](https://www.nih.gov/challenges) | Official requests for biomedical methods and tools | Verify dates, eligibility, licences, and deliverables on the individual competition page. |
| [AI4Life open-call retrospective](https://ai4life.eurobioimaging.eu/in-retrospect-ai4life-open-calls/) | Examples of image-analysis needs submitted by scientists and resulting workflows | Historical cases; the [project has ended](https://ai4life.eurobioimaging.eu/), so do not treat the old calls as open. |
| [Neurostars](https://neurostars.org/) | Practical questions from neuroscience researchers and developers | Individual requests are leads to investigate, not evidence of widespread demand. |

No single authoritative board covering all unsolved scientific and medical problems was found. Challenge.gov is also no longer an active discovery platform: its [official notice](https://www.challenge.gov/) records retirement on 30 March 2026.

## Concrete research shortlist

### 1. Label-free microscopy prediction

**Observed need:** fluorescence labelling takes resources and can perturb the cells being studied. France BioImaging's [Light My Cells](https://lightmycells.grand-challenge.org/) programme asks whether fluorescence channels can be predicted from transmitted-light images. Its [dataset paper](https://www.nature.com/articles/s41597-026-07004-w) describes public OME-TIFF images with structured metadata. A [second challenge](https://lightmycells2.grand-challenge.org/) extends the task. The second challenge was discoverable in search, but a subsequent direct fetch returned 403; registration, downloads, and phase status are not independently confirmed here.

**Proposed contribution:** reproduce an existing baseline and investigate one failure mode across acquisition conditions. Only consider a viewer integration after a researcher identifies an actual use for the predictions.

**Integration:** Python analysis first; a napari panel could later display observed input, predicted channels, and limitations as distinct layers, exporting results with model and parameter versions. This uses napari's supported extension surface, not a verified integration with a particular baseline.

**Success evidence:** performance and errors on held-out acquisition conditions, reproducible results, and usefulness for a specific research task. Check grouping by acquisition/study to avoid leakage between related images. Visually plausible predictions are insufficient and must remain labelled as predictions.

**Unknowns:** existing baseline quality, biological validity for the intended measurement, data licence and grouping details, installation effort, hardware, and whether deployment is a useful contribution.

### 2. Behavioural data linked to neural activity

**Observed need:** Gap Map identifies [quantitative behavioural datasets linked to neural activity](https://www.gap-map.org/capabilities/datasets-that-quantitatively-capture-the-full-space-of-behavior/) as an enabling capability. This is a broad scientific agenda rather than a validated request for a plugin.

**Proposed contribution:** with a lab, identify one recurring difficulty reviewing tracking errors or ambiguous behavioural events and measuring their effect on a neural analysis. Check current tools before proposing a new interface.

**Integration:** consume the lab's existing tracking outputs, timestamps, and neural data in a notebook. [NWB](https://github.com/NeurodataWithoutBorders/nwb-overview/blob/main/docs/source/intro_to_nwb/2_file_structure.rst) provides established structures for neurophysiology and behaviour. An NWB-compatible output is a possible boundary; no particular tracking export or timestamp mapping has been tested.

**Success evidence:** less review effort at equivalent accuracy, or an identified analysis error that a collaborator confirms matters. Preserve the distinction between better measurements and a new biological discovery.

**Unknowns:** collaborator, task, accessible representative data, current annotation/review capabilities, and whether the gap is scientific, organisational, or technical.

### 3. Biomedical evidence retrieval and verification

**Observed need:** NLM's [SPARK announcement](https://www.nlm.nih.gov/pubs/techbull/so26/so26_spark_challenge.html), posted September 2026, requests improvements to literature and research-data discovery. Its [exploratory evidence-synthesis task](https://repository.niddk.nih.gov/data-challenge/challenges/199) calls for grounded answers, valid citations, and relevant passages.

**Proposed contribution:** choose one question type and evaluate whether retrieved studies and passages support it, including population, intervention, and outcome alignment. Investigate existing retrieval systems before building another general question-answering interface.

**Integration:** a Python library returning structured evidence, passages, and source identifiers; a researcher-facing interface only after workflow observation. Potential document-manager or editor integrations remain uninvestigated.

**Success evidence:** independently assessed retrieval and citation support, correct handling of unanswered questions, and a repeatable comparison against an existing baseline. Automated scoring alone is insufficient.

**Unknowns:** novelty, evaluation resources, expert review capacity, full-text reuse conditions, compute cost, and challenge participation requirements.

### 4. Drug-safety property modelling

**Observed need:** [OpenADMET blind challenges](https://www.openadmet.org/blindchallenges/) evaluate predictions against experimental drug-discovery datasets. The reviewed CYP challenge concerns enzyme inhibition; its page lists a final submission date of 3 November 2026. This is a dated listing, not a commitment to compete on that timetable.

**Proposed contribution:** reproduce one endpoint baseline, examine failure cases, or improve a narrowly missing evaluation capability in the existing project. Do not assume a new predictor is needed.

**Integration:** the existing [OpenADMET Models Python library and notebooks](https://docs.openadmet.org/en/latest/) already support model training and evaluation. Prefer a contribution there if maintainers confirm the need.

**Success evidence:** reliable evaluation on genuinely held-out chemistry and interpretation with a qualified collaborator. A benchmark improvement does not establish clinical safety.

**Unknowns:** chemistry expertise, data terms, compute, existing model strengths, and meaningful remaining gaps. This has a higher scientific learning cost than the first three options.

### 5. Epilepsy evidence access

**Observed need:** the [Ontario Brain Institute/EpLink partnership](https://braininstitute.ca/resources/setting-research-priorities/epilepsy-psp) separates unanswered priorities from questions already partly or fully addressed by research. Its [answered-questions report](https://braininstitute.ca/docs/EpLink-Answered-Questions-Report.pdf) documents a knowledge-translation opportunity alongside the [Top 10 priorities](https://braininstitute.ca/img/JLA-Epilepsy-Top-10.pdf).

**Proposed contribution:** with a patient organisation, improve navigation through reviewed answers, retaining sources, uncertainty, and review dates. This is an evidence-access hypothesis, not a diagnostic or treatment recommendation product.

**Integration:** the organisation's existing website and editorial process, rather than an isolated patient app. No partner or publishing agreement exists.

**Success evidence:** users find and understand relevant reviewed information more accurately, without increased misunderstanding. A clinical editor and maintenance ownership would be prerequisites for a public pilot.

**Unknowns:** the underlying priority-setting exercise began around 2020; current gaps and report contents require a fresh review. Existing information services may already meet the need.

## Earlier ideas retained for comparison

| Candidate | Evidence and existing alternatives | Possible contribution; unresolved issue |
| --- | --- | --- |
| Assistive-device reliability | [Makers Making Change](https://www.neilsquire.ca/individual-programs-services/makers-making-change/), [LipSync](https://github.com/makersmakingchange/LipSync), and its [issue list](https://github.com/makersmakingchange/LipSync/issues) | Fix a user-confirmed reliability or independence barrier. Issue status, reproducibility, and contributor suitability require confirmation. |
| Biomedical sample-metadata repair | [2025 GEO completeness study](https://link.springer.com/article/10.1186/s13059-025-03725-0); existing [refine.bio harmonisation](https://docs.refine.bio/en/latest/main_text.html) and [MetaHQ](https://arxiv.org/abs/2602.07805), the latter reviewed as a preprint | Reconcile a lab's needed annotations with source evidence. Missing unpublished facts cannot be recovered by an interface. |
| Accessible scientific workflows | [Notebook accessibility study](https://arxiv.org/abs/2308.03241), existing [Olli](https://mitvis.github.io/olli/) and [Data Navigator](https://dig.cmu.edu/data-navigator/getting-started/), plus [2026 Jupyter improvements](https://blog.jupyter.org/posts/2026/jupyterlab-4-6-and-notebook-7-6-are-out/) | Make one student or researcher's actual task independently usable. Historical findings must be retested against current tools. |
| Hospital-discharge handover | Existing [AHRQ IDEAL materials](https://www.ahrq.gov/patient-safety/patients-families/engagingfamilies/strategy4/index.html) and [Lotsa Helping Hands](https://lotsahelpinghands.com/) | Clarify responsibilities and unanswered questions from reviewed instructions. Requires clinical collaboration; missing services are not a software problem. |
| Microscopy parameter sensitivity | [Independent-analysis variability study](https://pubmed.ncbi.nlm.nih.gov/41111557/) and existing [iterseg assessment](https://napari-hub.org/plugins/iterseg) | Show how a measurement changes across scientifically justified settings. Requires an agreed analysis plan to avoid outcome-driven tuning. |
| Experimental-unit checks | [SuperPlots paper](https://rupress.org/jcb/article/219/6/e202001064/151717/SuperPlots-Communicating-reproducibility-and) | Help describe nested measurements and detect mismatched independence assumptions. Experimental design cannot be inferred reliably from column names. |
| EEG event verification | Existing [LSL synchronisation](https://labstreaminglayer.readthedocs.io/info/time_synchronization.html) and [MNE realignment](https://mne.tools/stable/generated/mne.preprocessing.realign_raw.html) | Inspect missing markers, timing discrepancies, or discontinuities in one setup. Physical stimulus timing may require hardware evidence. |
| Biomedical ML leakage checks | Existing [scikit-learn guidance](https://scikit-learn.org/stable/common_pitfalls) and [DataSAIL](https://datasail.readthedocs.io/en/latest/) | One dataset-specific audit or adapter. Cannot certify arbitrary notebooks without identifiers and processing history. |
| Microplate layout checks | Existing [PlateDesigner](https://pmc.ncbi.nlm.nih.gov/articles/PMC6821189/) and [PLAID](https://www.sciencedirect.com/science/article/pii/S266731852300017X) | Improve one lab's constraints or verified instrument export. A connector may be sufficient. |

Generic caregiver coordination, general health-record timelines, biological dataset explorers, and universal paper-reproduction platforms were deprioritised as starting points. Existing tools are substantial; useful remaining gaps need to be demonstrated. For example, [Guava already supports records and timelines](https://guavahealth.com/article/guava-ultimate-guide). Computational execution also does not prove scientific validity.

## Integration and sustainability principles

| Existing environment | Plausible delivery route | Verified foundation |
| --- | --- | --- |
| napari | Panel using existing image layers; reader/writer where needed | [Plugin system](https://napari.org/plugins/) |
| Fiji/ImageJ | Command plugin distributed through an update site | [Development](https://imagej.net/develop/plugins), [distribution](https://imagej.net/contribute/distributing) |
| RStudio | R package, optionally an add-in that leaves readable analysis code | [Add-in documentation](https://docs.posit.co/ide/user/ide/guide/productivity/add-ins.html) |
| MNE-Python | Explicit function returning annotations or a report section | [Events](https://mne.tools/stable/api/events.html), [reports](https://mne.tools/stable/generated/mne.Report.html) |
| EEGLAB | Extension using the host's data structures | [Extension distribution](https://eeglab.org/others/EEGLAB_Extensions.html) |
| Jupyter or a Python script | Ordinary library function before an editor extension | Validate against the selected lab's installed environment |
| Instrument software | Verified sample-sheet import/export for one instrument | No universal vendor interface or format has been established |

These are supported extension surfaces, not completed compatibility checks. Prefer an explicit action on selected data to a plugin claiming to understand an entire analysis. Start with one host and one workflow; record assumptions, versions, and transformations, preserve original data, and provide portable output.

Free availability does not remove setup, learning, support, or maintenance costs. Prefer local execution where practical and an established project/community where appropriate. [OpenAAC's developer guidance](https://www.openaac.org/considerations) illustrates the consequences of abandoning software people depend on.

## Investigation outcome: 26 October 2026

The completed [comparative audit](AUDIT.md) favours a small contribution to movement: let confidence filtering use its existing manual-edit provenance. This is a documented upstream request with a specific remaining API gap, rather than a proposal for another tracking application. The [pilot specification](../../projects/movement-edit-filtering/PILOT.md) defines the baseline, integration, acceptance cases, resource limits, and reasons to stop.

Microscopy already has pretrained models and inference interfaces. Biomedical retrieval already has substantial retrieval and citation software. Neither audit established a sufficiently specific missing feature to justify a new application. These domains remain options for later scientific collaboration.

The approved local pilot now passes 97 targeted synthetic tests, including native save/reload; [results and limits](../../projects/movement-edit-filtering/PILOT.md) and the [full patch](../../projects/movement-edit-filtering/movement-pilot.patch) are available for review. No maintainer has been contacted. Manual editing does not itself establish biological correctness. The pilot demonstrates software behaviour; scientific usefulness, adoption, and patient benefit remain unestablished.

## Continuation

- Research preservation PR: [#228](https://github.com/ahmedkhaledmohamed/Personal/pull/228). The approved initial snapshot is commit `23e44fdb29ab57f20b3d3e464df08264a5406cf6`.
- The audit, pilot implementation artifacts, and results are subsequent local drafts, pending full-diff review; they have not been pushed.
- Autonomous research milestone: a decision-ready proposal is prepared. The approved technical pilot has also completed; real-workflow benefit remains unvalidated.
- Next decision: review the implementation diff. Outreach and publication require their applicable approval. See [the plan](PLAN.md) for the handoff.
