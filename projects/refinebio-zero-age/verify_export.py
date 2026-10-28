"""Exercise actual Sample metadata with offline SQLite or disposable PostgreSQL fixtures."""

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import io
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
    parser.add_argument(
        "--migrations",
        action="store_true",
        help="Run official migrations and the upstream startup hook in the private PostgreSQL fixture",
    )
    parser.add_argument("--workflow", choices=["ingestion", "export"])
    parser.add_argument("--postgres-socket", type=Path)
    parser.add_argument("--postgres-name", choices=["baseline", "patched"])
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.workflow:
        args.migrations = True
    postgres = args.postgres_socket is not None
    assert not args.migrations or postgres, (
        "Migrations require the disposable PostgreSQL fixture"
    )
    assert postgres == (args.postgres_name is not None)
    if postgres:
        assert args.postgres_socket.resolve().parent.name.startswith("kufu-age-pg-")
    checkout = args.checkout.resolve()
    if args.migrations:
        os.chdir(checkout)
        os.environ["S3_QN_TARGET_BUCKET_NAME"] = "constructed-no-cloud"
    if args.workflow:
        lock = json.loads(Path(__file__).with_name("workflow-lock.json").read_text())
        for name, digest in {
            **lock["source_files"],
            **lock["changed_files"][args.expect],
        }.items():
            assert (
                hashlib.sha256((checkout / name).read_bytes()).hexdigest() == digest
            ), name
    revision = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    assert revision == "7b809b7cae8d8a16f635febda80ac0c7336de9d7"
    sys.path[:0] = [
        str(checkout / "common"),
        str(checkout / "foreman"),
        str(checkout / "workers"),
    ]
    os.environ["SYSTEM_VERSION"] = "0.0.0"
    os.environ["JOB_DEFINITION_PREFIX"] = "constructed"
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
        AWS_BATCH_QUEUE_ALL_NAMES=[],
        AWS_BATCH_QUEUE_WORKERS_NAMES=[],
        SENTRY_DSN=None,
        USE_TZ=True,
        SECRET_KEY=secrets.token_hex(32),
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            *(["django.contrib.auth"] if postgres else []),
            "computedfields",
            "data_refinery_common.apps.CommonAppConfig"
            if args.migrations
            else "kufu_offline_config.OfflineCommonConfig",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": args.postgres_name,
                "USER": "kufu_fixture",
                "HOST": str(args.postgres_socket),
                "PORT": "55387",
            }
            if postgres
            else {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
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
        from django.apps import apps
        from django.db import connection

        if postgres:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT current_database(), current_user, current_setting('data_directory'), current_setting('listen_addresses')"
                )
                name, user, data_dir, addresses = cursor.fetchone()
            assert (
                name == args.postgres_name
                and user == "kufu_fixture"
                and addresses == ""
            )
            assert (
                Path(data_dir).resolve()
                == args.postgres_socket.resolve().parent / "data"
            )
            assert not connection.introspection.table_names(), (
                "Fixture database must be empty"
            )
        migration_count = None
        if args.migrations:
            from data_refinery_common.models import ComputedFile
            from data_refinery_common.signals import remove_file_from_s3
            from django.core.management import call_command
            from django.db.migrations.executor import MigrationExecutor
            from django.db.migrations.recorder import MigrationRecorder
            from django.db.models.signals import pre_delete

            assert any(
                receiver is remove_file_from_s3
                for receiver in pre_delete._live_receivers(ComputedFile)
            )
            call_command("migrate", interactive=False, verbosity=0)
            executor = MigrationExecutor(connection)
            assert not executor.migration_plan(executor.loader.graph.leaf_nodes())
            migration_count = MigrationRecorder(connection).migration_qs.count()
        else:
            with connection.schema_editor() as editor:
                if postgres:
                    for model in apps.get_models():
                        if (
                            model._meta.managed
                            and not model._meta.proxy
                            and not model._meta.swapped
                        ):
                            editor.create_model(model)
                else:
                    editor.create_model(SampleAnnotation)
        cases = []
        workflow_samples = []
        for index, value in enumerate(["0", "0.0", "2", "", "unknown"]):
            harmonized = Harmonizer().harmonize_sample(
                {"title": "constructed sample", "age": value}
            )
            sample = (
                Sample(
                    accession_code=f"constructed-{index}",
                    source_database="constructed",
                    **harmonized,
                )
                if postgres
                else Sample(pk=1, **harmonized)
            )
            if args.workflow:
                from workflow import create_sample

                sample = create_sample(index, value)
                workflow_samples.append(sample)
            if postgres:
                sample.save()
                sample.refresh_from_db()
            exported = sample.to_metadata_dict()["refinebio_age"]
            expected = (
                0.0
                if value in ["0", "0.0"] and args.expect == "patched"
                else 2.0
                if value == "2"
                else ""
            )
            assert exported == expected, (value, exported)
            case = {
                "input_age": value,
                "harmonized_age": harmonized.get("age"),
                "exported_age": str(exported) if postgres else exported,
            }
            if postgres:
                case["persisted_age"] = (
                    str(sample.age) if sample.age is not None else None
                )
                stream = io.StringIO()
                writer = csv.DictWriter(stream, fieldnames=["refinebio_age"])
                writer.writeheader()
                writer.writerow({"refinebio_age": exported})
                csv_age = next(csv.DictReader(io.StringIO(stream.getvalue())))[
                    "refinebio_age"
                ]
                expected_csv = (
                    "0.000" if expected == 0 else "2.000" if expected == 2 else ""
                )
                assert csv_age == expected_csv
                case["csv_sanity_age"] = csv_age
            cases.append(case)
        workflow_result = None
        if args.workflow == "export":
            from workflow import export_metadata, run_export_regressions

            workflow_result = export_metadata(
                checkout,
                workflow_samples,
                args.output.resolve().parent / f"files-{args.expect}",
            )
            workflow_result["existing_metadata_tests_passed"] = run_export_regressions(
                checkout
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
        original_tests = None
        if postgres:
            spec = importlib.util.spec_from_file_location(
                "upstream_sample_tests", checkout / "common/tests/models/test_sample.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = unittest.TextTestRunner().run(
                unittest.defaultTestLoader.loadTestsFromModule(module)
            )
            assert result.wasSuccessful()
            original_tests = result.testsRun
        postgres_version = connection.pg_version if postgres else None
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
        "existing_sample_test_methods_passed": original_tests,
        "postgres_version_number": postgres_version,
        "official_migrations_applied": migration_count,
        "workflow": args.workflow,
        "worker_export": workflow_result,
        "upstream_startup_hook_loaded": args.migrations,
    }
    if args.workflow:
        report["scope"] = (
            "Real SRA Sample creation with constructed ENA file-report responses, official migrations and startup-hook registration, save/reload and "
            + (
                "real worker metadata export"
                if args.workflow == "export"
                else "model metadata; worker exporter not executed"
            )
        )
        report["not_validated"] = (
            "Live service integration, S3 deletion execution, expression processing, dispatch/upload, populated-database upgrades, full upstream suite and researcher benefit"
        )
    elif args.migrations:
        report["scope"] = (
            "Actual Harmonizer, official migrations, upstream startup-hook registration, save/reload and model metadata on private PostgreSQL; cloud clients inert; CSV is only a standard-library check"
        )
        report["not_validated"] = (
            "Live ingestion, S3 deletion handler execution, full worker exporter and full upstream suite"
        )
    elif postgres:
        report["scope"] = (
            "Actual Harmonizer, model-schema creation, save/reload and Sample.to_metadata_dict on private PostgreSQL; cloud clients inert and startup hooks disabled; CSV uses the standard library"
        )
        report["not_validated"] = (
            "Production hooks, official migrations, live ingestion and full export service"
        )
    else:
        report["scope"] = (
            "Actual Harmonizer and Sample.to_metadata_dict; unsaved models and empty SQLite annotation table; cloud clients inert and startup hooks disabled"
        )
        report["not_validated"] = (
            "Persistence, production hooks, official migrations, live ingestion and full service tests"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
