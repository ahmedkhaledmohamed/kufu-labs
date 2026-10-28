"""Exercise actual Sample metadata export using constructed objects and an offline SQLite fixture."""

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import secrets
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--expect", choices=["baseline", "patched"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    assert revision == "7b809b7cae8d8a16f635febda80ac0c7336de9d7"
    sys.path[:0] = [str(checkout / "common"), str(checkout / "foreman")]
    os.environ["SYSTEM_VERSION"] = "0.0.0"
    from django.apps import AppConfig
    from django.conf import settings

    class OfflineCommonConfig(AppConfig):
        name = "data_refinery_common"
        path = str(checkout / "common/data_refinery_common")

    config_module = types.ModuleType("kufu_offline_config")
    config_module.OfflineCommonConfig = OfflineCommonConfig
    sys.modules[config_module.__name__] = config_module
    settings.configure(
        RUNNING_IN_CLOUD=False,
        SENTRY_DSN=None,
        USE_TZ=True,
        SECRET_KEY=secrets.token_hex(32),
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "computedfields",
            "kufu_offline_config.OfflineCommonConfig",
        ],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
    )
    with (
        patch("socket.socket.connect", side_effect=RuntimeError("Network disabled")),
        patch("boto3.client", return_value=object()),
    ):
        import django

        django.setup()
        from data_refinery_common.models import Sample, SampleAnnotation
        from data_refinery_foreman.surveyor.harmony import Harmonizer
        from django.db import connection

        with connection.schema_editor() as editor:
            editor.create_model(SampleAnnotation)
        cases = []
        for value in ["0", "0.0", "2", "", "unknown"]:
            harmonized = Harmonizer().harmonize_sample(
                {"title": "constructed sample", "age": value}
            )
            sample = Sample(pk=1, **harmonized)
            exported = sample.to_metadata_dict()["refinebio_age"]
            expected = (
                0.0
                if value in ["0", "0.0"] and args.expect == "patched"
                else 2.0
                if value == "2"
                else ""
            )
            assert exported == expected, (value, exported)
            cases.append(
                {
                    "input_age": value,
                    "harmonized_age": harmonized.get("age"),
                    "exported_age": exported,
                }
            )
        tests = None
        if args.expect == "patched":
            spec = importlib.util.spec_from_file_location(
                "zero_age_export_tests",
                checkout / "common/tests/test_sample_zero_age.py",
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = unittest.TextTestRunner().run(
                unittest.defaultTestLoader.loadTestsFromModule(module)
            )
            assert result.wasSuccessful()
            tests = result.testsRun
        connection.close()
    report = {
        "upstream_commit": revision,
        "expectation": args.expect,
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in [
                "Django",
                "boto3",
                "django-computedfields",
                "elasticsearch-dsl",
                "psycopg2-binary",
            ]
        },
        "sample_source_sha256": hashlib.sha256(
            (checkout / "common/data_refinery_common/models/sample.py").read_bytes()
        ).hexdigest(),
        "cases": cases,
        "model_test_methods_passed": tests,
        "scope": "Actual Harmonizer and Sample.to_metadata_dict; unsaved constructed model instances, empty SQLite annotation table, inert cloud clients, production AppConfig.ready hooks disabled",
        "not_validated": "Persistence, production signals, PostgreSQL migrations, live ingestion and full service tests",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
