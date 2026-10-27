# Scientific software lab

Private workspace for scientific-software research, reproducible experiments, upstream contributions, and early MVPs. Start with [WORKSPACE.md](WORKSPACE.md) for current work and decisions.

## Research

- [Opportunity discovery](research/opportunity-discovery/README.md): problem boards, candidate ideas, evidence, integration routes, and tradeoffs.
- [Comparative audit](research/opportunity-discovery/AUDIT.md): microscopy, behavioural neuroscience, and biomedical evidence retrieval.
- [Investigation plan](research/opportunity-discovery/PLAN.md): completed work and remaining validation gates.

## Projects

| Project | Current evidence | Next step |
| --- | --- | --- |
| [movement edit-aware filtering](projects/movement-edit-filtering/README.md) | Local patch; 97 targeted synthetic tests passed; no real-workflow validation | Review the full change, complete remaining host checks, then decide on upstream review |

## Repository structure

`research/` holds sourced investigations and cross-project decisions. `projects/<name>/` holds each project's scope, reproducibility record, source or upstream patch, and results. Add an MVP's code in its project directory when it has an approved task; do not introduce a shared build framework before projects need one.

Upstream projects keep their own Git history and implementation worktrees. Record a pinned revision, patch, provenance, and result here rather than vendoring their entire source trees. An independently maintained product can later split into its own repository while leaving its research history linked here.

Keep recordings, model weights, environments, credentials, and generated caches outside version control. Small constructed fixtures may live beside a project's code. Verify data and model reuse terms separately from software licences.

The lab is private by design. Private storage does not authorise patient-data collection, external messaging, paid services, public release, or merging. Follow the applicable project instructions and existing approval boundaries.
