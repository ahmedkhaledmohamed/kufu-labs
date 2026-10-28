# Preserve zero-valued age metadata

Status: source-discovered defect and patch with a constructed SRA-to-worker metadata workflow verified in Linux CI. No affected public sample, user complaint, production impact or upstream acceptance has been established. [Cross-domain investigation](../../research/opportunity-discovery/VALIDATION-BATCH.md).

## Problem and possible consequence

The pinned refine.bio harmoniser converts age values to floats and then tests their truthiness before retaining them. Its model metadata method also replaces a zero age with an empty value. A valid numeric zero can therefore be lost at either boundary. Researchers reusing harmonised sample metadata could receive a missing annotation where a submitted source value was zero. The frequency and downstream effect have not been measured.

This is a finding from inspected source and constructed inputs, not a newly reported user need. The related [metadata completeness study](https://link.springer.com/article/10.1186/s13059-025-03725-0) motivates investigating data reuse but does not establish this specific defect's prevalence.

## Actual before and after

At refine.bio [7b809b7](https://github.com/AlexsLemonade/refinebio/tree/7b809b7cae8d8a16f635febda80ac0c7336de9d7), the replay imports the real `Harmonizer` class with cloud access disabled and network connections blocked. It exercises its full sample-harmonisation method on constructed metadata. The harmoniser replay has no database. A second offline replay exercises the actual `Sample.to_metadata_dict` method on unsaved model instances with an empty in-memory SQLite annotation table, inert cloud clients and production readiness hooks disabled. This is not a running ingestion service.

| Constructed case | Baseline | Patched |
| --- | --- | --- |
| Zero age: 4 representations across 4 recognised keys | Missing in 16/16 cases | Retained as 0.0 in 16/16 cases |
| Positive age: 4 keys | Retained | Retained |
| Empty or unknown age: 8 cases | Absent | Absent |
| Title and sex annotations; input metadata | Preserved | Preserved |

The [baseline](baseline.json) and [patched](patched.json) records contain all 28 cases, source hashes and runtime versions. Five harmoniser regression methods and three model-metadata methods, including subcases, pass with the patch. The [model baseline](export-baseline.json) and [model patched](export-patched.json) records show the additional five-case handoff check. The scope deliberately does not change age units, resolve conflicting values, repair missing unpublished facts or infer a biological age.

## Implementation and reproduction

The [patch](preserve-zero.patch) changes the two value-retention conditions in the existing harmoniser and the model metadata age fallback, with targeted tests for both. It accepts a value when it is neither `None` nor an empty string, preserving numeric zero without converting unknown values to zero. The [upstream BSD licence](UPSTREAM-LICENSE) is retained.

Use Python 3.10 and install the [minimal pinned requirements](requirements.txt) into an isolated environment. Create separate baseline and feature worktrees from commit `7b809b7cae8d8a16f635febda80ac0c7336de9d7`; apply the patch only to the feature worktree. Then run, from the lab root:

```sh
python projects/refinebio-zero-age/verify.py --checkout /path/to/pinned-clean-refinebio --expect baseline --output /tmp/zero-age-baseline.json
python projects/refinebio-zero-age/verify.py --checkout /path/to/pinned-patched-refinebio --expect patched --output /tmp/zero-age-patched.json
```

To exercise model metadata as well, install the [model-fixture requirements](requirements-model.txt) in a separate environment and use [verify_export.py](verify_export.py) with the same `--checkout`, `--expect` and `--output` arguments. It imports the actual models and creates only an empty annotation table. It does not save a Sample or run production signals.

The runners reject a different upstream revision. It configures Django without cloud logging, prevents socket connections, compares input metadata before/after, and runs the patch's regression tests for the patched expectation. The raw input annotations are entirely constructed.

## PostgreSQL persistence check

The [private-cluster replay](verify_postgres.py) adds real save/reload coverage using PostgreSQL 16.2. It builds the actual Django model schema in a new empty database, harmonises constructed metadata, saves a Sample, reloads it and calls the real metadata method. The [baseline](postgres-baseline.json) loses zero; the [patched result](postgres-patched.json) preserves `0.000` through persistence and metadata output. Positive and missing-value controls remain unchanged. The upstream's existing Sample metadata-key test also passes on each revision.

The final CSV column is a standard-library serialization sanity check, not execution of the production export service. Production readiness hooks remain disabled, cloud clients are inert, and no public sample is involved. Model-defined schema creation does not establish migration compatibility.

With the model-fixture dependencies installed and PostgreSQL binaries available, run:

```sh
python projects/refinebio-zero-age/verify_postgres.py --postgres-bin /path/to/postgresql/bin --clean-checkout /path/to/pinned-clean-refinebio --patched-checkout /path/to/pinned-patched-refinebio --output-dir /tmp/zero-age-postgres
```

The launcher creates only temporary databases in a private Unix-socket cluster, disables TCP listening, ignores inherited PostgreSQL connection settings, verifies the data-directory identity and empty databases before schema creation, then stops and removes the cluster. It does not use an existing database. The child `--postgres-socket` arguments are fixture internals. The tested macOS ARM64 runtime came from [pgserver 0.1.4](https://pypi.org/project/pgserver/); its wheel checksum is recorded in verification. No binaries are distributed in the lab. Other platforms and PostgreSQL versions remain untested.

## Official migration and startup-hook follow-up

The PostgreSQL runner now accepts `--migrations`. It applies all 91 official migrations in each empty fixture database, verifies no migration remains pending, and loads the real CommonAppConfig startup hook. The S3 pre-delete handler is verified as registered; its cloud operation is not invoked. Both the [baseline](migrations-baseline.json) and [patched](migrations-patched.json) pass the constructed model cases and existing Sample regression. This is an empty-database installation check, not a populated-production upgrade test.

## SRA record-creation replay

The [baseline](ingestion-baseline.json) and [patched](ingestion-patched.json) results now exercise the actual `SraSurveyor._generate_sample` method with five constructed metadata cases. The real harmoniser, sample/original-file records, experiment associations, saves, reloads and metadata method execute after official migrations. Only the ENA file-report HTTP response is supplied by the fixture; all other Python socket connections are blocked. No research file is downloaded and no job is dispatched. The positive/missing-value controls and upstream Sample regression pass. The launcher also repeats the 28-case harmoniser comparison and its five new test methods.

Use the PostgreSQL command above with `--workflow ingestion`. This enables official migrations and startup-hook registration automatically. For a source-only fresh checkout, `python projects/refinebio-zero-age/prepare.py` fetches the exact revision with a blob filter and sparse source paths, excludes both test-volume directories, checks hashes in [workflow-lock.json](workflow-lock.json), and applies the unchanged patch. It refuses to overwrite existing checkouts. The fresh checkouts passed the local replay.

## Actual Linux worker-export result

[CI run 40763058912](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40763058912), at lab commit `43eae2c`, passed the real SRA record-creation and worker metadata replay. It built the hash-checked upstream Linux base with R 3.4.4, installed worker/common dependency files in upstream order, and used PostgreSQL 14.24. The local PostgreSQL 16.2 checks remain separate evidence. This metadata image does not restore expression-processing Bioconductor libraries; that processing is outside the selected workflow.

| Input age | Baseline actual TSV | Patched actual TSV |
| --- | --- | --- |
| `0` | Empty | `0.000` |
| `0.0` | Empty | `0.000` |
| `2` | `2.000` | `2.000` |
| Empty | Empty | Empty |
| `unknown` | Empty | Empty |

All three supported aggregation branches (ALL, EXPERIMENT and SPECIES) produce those values. The [baseline](postgres-baseline.json) and [patched](postgres-patched.json) results retain exact TSV text, file hashes, actual Python package versions and R/PostgreSQL versions. The CI artifact retains original output files and diagnostics. Independent checks matched all 26 output-file hashes and TSV text across both revisions. Five existing upstream metadata-export regressions, the existing Sample regression and 91 official migrations pass per revision. The patched source also passes the five harmoniser and three model regression methods.

The runtime uses an unprivileged container, disabled networking, read-only source mounts and isolated temporary PostgreSQL databases. The real `SraSurveyor._generate_sample` creates the constructed records; only the ENA file-report HTTP response is supplied by the fixture. `write_non_data_files` executes `compile_metadata`, `write_tsv_json`, database lookups, README/licence copying and actual TSV/JSON serialization. No recording is downloaded, expression matrix processed, job dispatched or output uploaded. The real startup hook is loaded and its deletion handler registered, but the cloud deletion operation is not executed.

To reproduce the CI path on an authorised Linux Docker host, run source preparation, build the pinned upstream `common/dockerfiles/Dockerfile.base` as `kufu/refinebio-base:7b809b7`, then build the lab's [worker recipe](https://github.com/ahmedkhaledmohamed/kufu-labs/blob/main/projects/refinebio-zero-age/Worker.Dockerfile) with the clean source checkout as context. The exact commands and runtime isolation flags are maintained in [the workflow](https://github.com/ahmedkhaledmohamed/kufu-labs/blob/main/.github/workflows/lab-delivery.yml). The launcher option is `--workflow export`; the metadata image must use R 3.4.4. The new gate is required by both the web build and deployment. The Validation page reads fresh results from that same CI run and displays the actual before/after values.

Two initial CI attempts exposed infrastructure/harness problems: floating wheel 0.48.0 conflicts with upstream packaging 23.0, and worker imports read container-relative assets. The current recipe pins compatible wheel 0.41.3 while retaining `pip check`, and enters the worker root before importing exporter/test modules. These corrections change neither the scientific patch nor its acceptance assertions. The local managed container sign-in policy was not bypassed; no managed credentials or policy changes were used.

## Validation limits and next decision

The component and model environments use Python 3.10.16 and the repository's declared core dependency versions. They are not the complete locked service environment. Selected model persistence now passes on PostgreSQL 16.2; live surveyor APIs, expression processing, dispatch/upload and the full Django suite have not run. Constructed SRA record creation and actual metadata-file generation now pass in CI. Official migrations now pass on empty fixture databases; the production deletion hook is registered but not executed. A preservation result does not establish researcher benefit.

Current source already retrieves BioSample metadata. The earlier generic proposal to add BioSample enrichment is therefore deferred rather than duplicated. The project's open [production-data-flow issue #3595](https://github.com/AlexsLemonade/refinebio/issues/3595) is a separate operational concern; an independent app would not resolve it.

The next step is review of the supported contribution boundary and its remaining service/integration limits. Refresh competing work before an upstream proposal. Do not expand this into an enrichment platform. No upstream message, fork push or PR is included. The local ingestion replay and maintained Linux metadata-export gate pass. Lab publication requires exact-diff approval; upstream outreach remains deferred.
