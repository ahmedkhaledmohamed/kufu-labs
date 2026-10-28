# Preserve zero-valued age metadata

Status: source-discovered component defect and local patch. No affected public sample, user complaint, production impact or upstream acceptance has been established. [Cross-domain investigation](../../research/opportunity-discovery/VALIDATION-BATCH.md).

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

## Validation limits and next decision

The component and model environments use Python 3.10.16 and the repository's declared core dependency versions. They are not the complete locked service environment. Selected model persistence now passes on PostgreSQL 16.2; production signals, surveyors, official migrations, output-file generation and the full Django test suite have not run. A preservation result does not establish researcher benefit.

Current source already retrieves BioSample metadata. The earlier generic proposal to add BioSample enrichment is therefore deferred rather than duplicated. The project's open [production-data-flow issue #3595](https://github.com/AlexsLemonade/refinebio/issues/3595) is a separate operational concern; an independent app would not resolve it.

The next step is review in the complete upstream environment and a refresh for competing work. Do not expand this into an enrichment platform. No upstream message, fork push or PR is included. The replay is local and not yet a maintained lab CI gate. Lab publication requires exact-diff approval; upstream outreach remains deferred.
