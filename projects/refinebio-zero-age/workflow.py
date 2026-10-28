"""Exercise upstream SRA record creation and worker metadata export with constructed inputs."""

import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch


def create_sample(index, value):
    from data_refinery_common.models import Experiment, Organism, SurveyJob
    from data_refinery_foreman.surveyor.sra import SraSurveyor
    from requests import Response

    organism, _ = Organism.objects.get_or_create(
        name="CONSTRUCTED_SPECIES", defaults={"taxonomy_id": 0}
    )
    experiment, _ = Experiment.objects.get_or_create(
        accession_code="CONSTRUCTED_EXPERIMENT",
        defaults={"protocol_description": "Protocol was never provided."},
    )
    metadata = {
        "run_accession": f"constructed-{index}",
        "scientific_name": organism.name,
        "instrument_platform": "ILLUMINA",
        "instrument_model": "CONSTRUCTED_INSTRUMENT",
        "library_layout": "SINGLE",
        "title": "constructed sample",
        "age": value,
    }
    requests = []

    def file_report(session, request, **kwargs):
        assert request.method == "GET"
        assert request.url.startswith(
            "https://www.ebi.ac.uk/ena/portal/api/filereport/"
        )
        assert f"accession=constructed-{index}" in request.url
        requests.append("constructed ENA file report")
        response = Response()
        response.status_code = 200
        response.url = request.url
        response._content = b"[]"
        return response

    # Only the external HTTP response is constructed. The surveyor, metadata
    # application, original-file records, associations and saves remain real.
    with patch("requests.sessions.Session.send", file_report):
        sample = SraSurveyor(SurveyJob(pk=1))._generate_sample(experiment, metadata)
    sample.refresh_from_db()
    assert sample.organism_id == organism.pk
    assert sample.experiments.filter(pk=experiment.pk).exists()
    assert sample.original_files.count() == 1
    assert len(requests) == 1
    return sample


def export_metadata(checkout, samples, output):
    from data_refinery_common.models import Dataset, Experiment

    dataset = Dataset.objects.create(
        data={"CONSTRUCTED_EXPERIMENT": [sample.accession_code for sample in samples]},
        aggregate_by="ALL",
        quantile_normalize=False,
    )
    results = []
    previous = Path.cwd()
    try:
        os.chdir(checkout / "workers")
        from data_refinery_workers.processors import smashing_utils
        from rpy2.robjects import r

        # Verify the real embedded runtime; do not stub R or load a substitute module.
        r_version = str(r('paste(R.version$major, R.version$minor, sep=".")')[0])
        assert r_version == "3.4.4", r_version
        assert (
            Path(smashing_utils.__file__).resolve()
            == (
                checkout / "workers/data_refinery_workers/processors/smashing_utils.py"
            ).resolve()
        )
        for aggregate_by in ["ALL", "EXPERIMENT", "SPECIES"]:
            dataset.aggregate_by = aggregate_by
            dataset.save()
            directory = output / aggregate_by
            directory.mkdir(parents=True, exist_ok=False)
            context = {
                "dataset": dataset,
                "experiments": Experiment.objects.filter(
                    accession_code="CONSTRUCTED_EXPERIMENT"
                ),
                "filtered_samples": {},
                "output_dir": str(directory) + os.sep,
                "group_by_keys": ["CONSTRUCTED_SPECIES"],
            }
            # Executes compile_metadata, DB lookups, real TSV/JSON writers and
            # README/licence copying. No scheduler, expression processing or upload.
            smashing_utils.write_non_data_files(context)
            rows = []
            for path in directory.rglob("*.tsv"):
                with path.open(newline="") as stream:
                    rows.extend(csv.DictReader(stream, delimiter="\t"))
            assert len(rows) == len(samples)
            by_accession = {row["refinebio_accession_code"]: row for row in rows}
            assert set(by_accession) == {sample.accession_code for sample in samples}
            ages = {}
            for sample in samples:
                age = by_accession[sample.accession_code]["refinebio_age"]
                expected = "" if sample.age is None else str(sample.age)
                assert age == expected, (
                    aggregate_by,
                    sample.accession_code,
                    age,
                    expected,
                )
                ages[sample.accession_code] = age
            aggregate = json.loads((directory / "aggregated_metadata.json").read_text())
            assert len(aggregate["samples"]) == len(samples)
            for sample in samples:
                value = aggregate["samples"][sample.accession_code]["refinebio_age"]
                assert value == ("" if sample.age is None else float(sample.age))
            results.append(
                {
                    "aggregate_by": aggregate_by,
                    "tsv_age_by_accession": ages,
                    "tsv_files": {
                        str(path.relative_to(output)): path.read_text()
                        for path in sorted(directory.rglob("*.tsv"))
                    },
                    "files": {
                        str(path.relative_to(output)): hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
                        for path in sorted(directory.rglob("*"))
                        if path.is_file()
                    },
                }
            )
    finally:
        os.chdir(previous)
    return {
        "r_version": r_version,
        "export_modes": results,
        "python_packages": {
            distribution.metadata["Name"]: distribution.version
            for distribution in importlib.metadata.distributions()
        },
    }


def run_export_regressions(checkout):
    import sys
    import unittest

    previous = Path.cwd()
    try:
        # Both smasher and smashing_utils read container-relative assets at
        # import time, so establish the host working directory before imports.
        os.chdir(checkout / "workers")
        sys.path.insert(0, str(checkout / "workers"))
        import tests.utils

        assert (
            Path(tests.utils.__file__).resolve()
            == (checkout / "workers/tests/utils.py").resolve()
        )
        spec = importlib.util.spec_from_file_location(
            "upstream_metadata_tests",
            checkout / "workers/tests/processors/test_smasher.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        selected = [
            "test_columns",
            "test_all_samples",
            "test_experiment",
            "test_unicode_writer",
            "test_species",
        ]
        suite = unittest.TestSuite(
            module.AggregationTestCase(method) for method in selected
        )
        result = unittest.TextTestRunner().run(suite)
    finally:
        os.chdir(previous)
    assert result.wasSuccessful()
    return result.testsRun
