"""Validate the curated lab catalogue and build an offline hub and research pages."""

from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
RECORDS = SITE / "records"


def slug(path):
    return path.removesuffix(".md").replace("/", "--") + ".html"


def movement_upstream_comparison():
    project = ROOT / "projects/movement-edit-filtering"
    profile = json.loads((project / "upstream-1190-profile.json").read_text())
    results = [
        json.loads((project / f"upstream-1190-{mode}.json").read_text())
        for mode in ["base", "head"]
    ]
    for mode, result in zip(["base", "head"], results):
        assert result["source_revision"] == profile[f"{mode}_revision"]
        assert result["convert_sha256"] == profile[f"{mode}_convert_sha256"]
        assert (
            result["runner_sha256"]
            == hashlib.sha256(
                (project / "verify_upstream_1190.py").read_bytes()
            ).hexdigest()
        )
        assert (
            result["profile_sha256"]
            == hashlib.sha256(
                (project / "upstream-1190-profile.json").read_bytes()
            ).hexdigest()
        )
        assert result["local_patch_applied"] is False
        assert result["rendered"][
            "positions_confidence_and_time_preserved_after_reexport"
        ]
        assert result["rendered"][
            "never_detected_and_unscored_controls_not_marked_edited"
        ]
    rows = []
    for suite, label in [
        ("independent", "Existing Kufu deletion/control cases"),
        (
            "upstream_conversion",
            "Selected upstream conversion tests, including the PR’s four new cases",
        ),
    ]:
        rows.append(
            [
                label,
                *[
                    f"{r['suites'][suite]['passed']}/{r['suites'][suite]['tests']} pass"
                    for r in results
                ],
            ]
        )
    rows.append(
        ["Deleted-point flag after the second Qt Save", "Edit variable absent", "true"]
    )
    rows.append(["Deleted-point flag in final Qt loader", "false", "true"])
    assert results[0]["rendered"]["flag_after_second_save"] is None
    assert results[0]["rendered"]["flag_in_final_loader"] is False
    assert results[1]["rendered"]["flag_after_second_save"] is True
    assert results[1]["rendered"]["flag_in_final_loader"] is True
    return (
        '<p>On 3 November, devanshc777 opened <a href="https://github.com/neuroinformatics-unit/movement/pull/1190">draft movement PR #1190</a>. Kufu tested its exact base and head independently, without applying the local Kufu repair. The PR head passes all 64 selected cases and the rendered deletion/save/reopen replay. This is local verification of a draft, not a merged or released fix.</p>'
        + '<div class="table-scroll"><table id="movementUpstreamComparison"><caption>Pinned upstream base versus contributor’s draft head</caption><thead><tr><th scope="col">Check</th><th scope="col">PR base</th><th scope="col">PR head</th></tr></thead><tbody>'
        + "".join(
            "<tr>"
            + "".join("<td>" + html.escape(value) + "</td>" for value in row)
            + "</tr>"
            for row in rows
        )
        + "</tbody></table></div><p>The base fails six independent deletion cases and the four new upstream regression cases. The head preserves provenance through one, two and four native reopen cycles, including mixed edits, while preserving numeric data and never-detected controls. The rendered run uses an actual canvas click, Delete key and Save/Load buttons.</p>"
        + "<p>The comparison used a cached Linux arm64 CPU runtime with network access disabled. It does not cover the full napari suite, reset/re-add interactions, recordings or measured researcher benefit. Re-adding points remains separate issue #1060 work.</p>"
        + '<p><a href="../projects/movement-edit-filtering/upstream-1190-base.json">Base results</a> · <a href="../projects/movement-edit-filtering/upstream-1190-head.json">Draft-head results</a> · <a href="../projects/movement-edit-filtering/upstream-1190-profile.json">Pinned source and licence identities</a> · <a href="../projects/movement-edit-filtering/verify_upstream_1190.py">Comparison implementation</a></p>'
    )


def ecephys_walkthrough():
    project = ROOT / "projects/nwb-stream-integrity"
    result = json.loads((project / "ecephys-result.json").read_text())
    assert result["passed"] and len(result["cases"]) == 12
    assert (
        result["runner_sha256"]
        == hashlib.sha256((project / "verify_ecephys.py").read_bytes()).hexdigest()
    )
    example_hash = hashlib.sha256((project / "ecephys.py").read_bytes()).hexdigest()
    assert all(case["example_sha256"] == example_hash for case in result["cases"])
    small = {
        case["expectation"]: case
        for case in result["cases"]
        if case["input"]["rows"] == 16384 and case["inspected"]
    }
    before, after = small["baseline"], small["patched"]
    assert before["expected_sha256"] == after["expected_sha256"]
    assert before["metadata"] == after["metadata"] and after["values_preserved"]
    body = (
        "<p>A recording converter needs to preserve both the samples and their meaning: which electrode each column belongs to, how integer acquisition counts become volts, and when each sample occurred. This example follows PyNWB’s existing ElectricalSeries workflow using 16 constructed channels. The values and electrode identities are software fixtures, not neural recordings.</p>"
        + "<h3>Understand the inputs</h3><ul>"
        + "<li><strong>Electrodes and channels:</strong> each data column references an electrode-table row. The example deliberately uses reversed table order, so the check verifies the actual links.</li>"
        + "<li><strong>Acquisition counts and volts:</strong> stored integers are multiplied by a voltage conversion and a per-channel factor. The chosen fixture scale is 0.1 microvolt per count; it is not a real device calibration.</li>"
        + "<li><strong>Sampling rate:</strong> 20,000 samples per second gives a 50-microsecond interval. The file stores that rate and a 0.25-second start time.</li>"
        + "<li><strong>Buffers:</strong> the source generates 4,096 time rows at a time. Inspection should ask about its shape while leaving those rows available for writing.</li></ul>"
        + "<h3>Follow the conversion</h3><p>The script creates electrode metadata and a buffered integer source, runs the installed Inspector, writes a real HDF5 NWB file, then reopens it. Every value is compared in blocks, and electrode links, voltage factors and timing are checked separately.</p>"
    )
    rows = [
        [
            "Buffers consumed during inspection",
            *[
                case["iterator_buffers_requested"]["inspection"]
                for case in [before, after]
            ],
        ],
        [
            "Writer’s first row index",
            *[case["first_requested_row"]["writing"] for case in [before, after]],
        ],
        ["Rows with changed values", before["changed_rows"], after["changed_rows"]],
        ["Electrode links, voltage scale and timing", "Preserved", "Preserved"],
        [
            "Inspector ERROR messages",
            len(before["inspection_errors"]),
            len(after["inspection_errors"]),
        ],
        [
            "File-schema errors after writing",
            before["schema_validation_errors"],
            after["schema_validation_errors"],
        ],
    ]
    body += (
        '<div class="table-scroll"><table id="ecephysComparison"><caption>16,384 time rows × 16 channels after inspection, writing and reopening</caption><thead><tr><th scope="col">Check</th><th scope="col">Baseline wheel</th><th scope="col">Experimental repair</th></tr></thead><tbody>'
        + "".join(
            "<tr>"
            + "".join("<td>" + html.escape(str(value)) + "</td>" for value in row)
            + "</tr>"
            for row in rows
        )
        + "</tbody></table></div>"
    )
    original = after["first_sample_example"]["expected_counts"][0]
    body += (
        '<p id="ecephysResultMeaning">Both files still have all 16,384 row positions. However, baseline inspection consumes three buffers before the writer starts, and '
        + str(before["changed_rows"])
        + " rows contain different values. For the first channel at row zero, the generated count is "
        + str(original)
        + ", the baseline saves "
        + str(before["first_sample_example"]["saved_counts"][0])
        + ", and the repair saves "
        + str(after["first_sample_example"]["saved_counts"][0])
        + ". Legitimate zeros also occur in the input, so a zero alone is not treated as evidence of corruption.</p>"
        + "<p>Both files pass schema validation, which checks the file’s structure. The separate value comparison establishes whether this conversion preserved the generated input. Neither check establishes that a biological experiment is valid.</p>"
    )
    scaling = []
    for size in result["sizes_bytes"]:
        cases = {
            case["expectation"]: case
            for case in result["cases"]
            if case["array_bytes"] == size and case["inspected"]
        }
        scaling.append(
            [
                f"{size / 1048576:g}",
                cases["baseline"]["changed_rows"],
                cases["patched"]["changed_rows"],
                f"{cases['patched']['peak_rss_bytes'] / 1048576:.1f}",
            ]
        )
    body += (
        '<details class="reproduction"><summary>Memory measurements with larger generated inputs</summary><p>Generation and readback use bounded blocks. Total process memory also includes Python, NumPy, PyNWB and HDF5. Memory rose with input size; these measurements do not establish constant-memory behavior or a guarantee for larger recordings.</p><div class="table-scroll"><table><caption>Separate-process measurements with inspected inputs</caption><thead><tr>'
        + "".join(
            '<th scope="col">' + value + "</th>"
            for value in [
                "Array size (MiB)",
                "Baseline changed rows",
                "Repair changed rows",
                "Repair peak RSS (MiB)",
            ]
        )
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>"
            + "".join("<td>" + html.escape(str(value)) + "</td>" for value in row)
            + "</tr>"
            for row in scaling
        )
        + "</tbody></table></div><p>The comparison runner allows 120 seconds per case and rejects results with peak process RSS at or above 512 MiB or generated files at or above 160 MiB. Larger files are removed after comparison; the four small files are retained.</p></details>"
    )
    archive = result["small_archive"]
    assert (
        archive["filename"] == "ecephys-example.zip" and len(archive["nwb_files"]) == 4
    )
    file = project / "builds" / archive["filename"]
    if file.exists():
        assert hashlib.sha256(file.read_bytes()).hexdigest() == archive["sha256"]
        body += '<p><a id="ecephysArchive" download href="../projects/nwb-stream-integrity/builds/ecephys-example.zip">Download the four small constructed NWB files and results</a></p>'
    else:
        body += "<p>The source-only build has no generated file bundle. The local command below creates a constructed NWB file.</p>"
    body += (
        '<h3>Run the example</h3><p><a href="#installable-builds">Install the experimental repaired wheel</a> in a separate environment, then run this from the lab checkout. The same script can run in an existing notebook whose kernel uses that environment. The output directory must be new.</p><div class="reproduction"><pre><code>'
        + html.escape(
            ".venv-nwb-experiment/bin/python projects/nwb-stream-integrity/ecephys.py --expect patched --retain --output .runs/ecephys-example"
        )
        + "</code></pre></div><p>The output includes constructed_ecephys.nwb and result.json. Open the native file with PyNWB or an NWB-compatible viewer. This page displays retained local/CI results; the complete electrode conversion runs in Python, while the existing hosted lab remains the separate generic stream replay.</p>"
        + '<p><a href="../projects/nwb-stream-integrity/ecephys.py">Runnable conversion example</a> · <a href="../projects/nwb-stream-integrity/verify_ecephys.py">Comparison runner</a> · <a href="../projects/nwb-stream-integrity/ecephys-result.json">Download all measured results (JSON)</a> · <a href="https://pynwb.readthedocs.io/en/stable/tutorials/domain/ecephys.html">PyNWB electrophysiology guide</a></p>'
    )
    return body


def nwb_build_downloads():
    project = ROOT / "projects/nwb-stream-integrity"
    result = json.loads((project / "wheel-result.json").read_text())
    profile = json.loads((project / "released-profile.json").read_text())
    assert result["passed"]
    manifest = result["manifest"]
    assert manifest["upstream_commit"] == profile["upstream_commit"]
    assert manifest["patch_sha256"] == profile["patch_sha256"]
    files = [
        project / "builds" / manifest["builds"][mode]["filename"]
        for mode in ["baseline", "patched"]
    ]
    available = all(file.is_file() for file in files)
    assert available or not any(file.exists() for file in files), (
        "Partial NWB build downloads"
    )
    rows = []
    for mode, label, file in zip(
        ["baseline", "patched"],
        ["Baseline: reproduces data loss", "Experimental repair"],
        files,
    ):
        entry = manifest["builds"][mode]
        expected = f"0.7.2+kufu.{'baseline1' if mode == 'baseline' else 'stream1'}"
        assert (
            entry["version"] == expected
            and entry["filename"] == f"nwbinspector-{expected}-py3-none-any.whl"
        )
        observed = result["results"][mode]
        assert observed["installed_build"]["editable"] is False
        assert observed["installed_build"]["source_imports"] is False
        assert observed["installed_build"]["wheel_sha256"] == entry["sha256"]
        if available:
            assert hashlib.sha256(file.read_bytes()).hexdigest() == entry["sha256"]
            label = (
                '<a download href="../projects/nwb-stream-integrity/builds/'
                + entry["filename"]
                + '">'
                + html.escape(label)
                + "</a>"
            )
        else:
            label = html.escape(label)
        tests = observed["unit_tests"]
        assert len(tests["failed"]) == 3 and tests["skipped"] == 5
        rows.append(
            "<tr><td>"
            + label
            + "</td><td>"
            + html.escape(entry["version"])
            + "</td><td>"
            + str(observed["inspected_preserved"])
            + "/12</td><td>"
            + str(observed["controls_preserved"])
            + "/12</td><td>"
            + str(tests["passed"])
            + " passed; 3 known failures; 5 skipped</td></tr>"
        )
    body = (
        '<p id="nwbBuildStatus">Installed-wheel verification: both builds ran in fresh Python 3.12.12 environments, using the real Inspector and HDF5/Zarr writers. Installed code, configuration files, licence and import origins were checked. These are experimental Kufu builds from the pinned release, without upstream endorsement.</p>'
        + '<div class="table-scroll"><table id="nwbBuildComparison"><caption>Data preserved after inspection, writing and reopening</caption><thead><tr>'
        + "".join(
            '<th scope="col">' + value + "</th>"
            for value in [
                "Build",
                "Version",
                "Inspected cases",
                "Uninspected controls",
                "Release unit suite",
            ]
        )
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
        + "<p>The baseline download reproduces data loss and is provided for comparison. The repaired build preserved every value in the 12 inspected constructed cases. Three pre-existing dependency-related unit failures remain on both builds. Real recordings and other environments remain unvalidated.</p>"
    )
    if not available:
        body += "<p>Wheel downloads are absent from this source-only build. Run the documented wheel build to generate them; scientific CI supplies them for deployment.</p>"
    repaired = manifest["builds"]["patched"]
    body += (
        '<details class="reproduction"><summary>Install the experimental repair in a separate environment</summary><p>Use the lab checkout, Python 3.12.12 and the repaired wheel downloaded above. This installs the pinned tested dependencies. Your conversion code uses the existing nwbinspector API.</p><pre><code>'
        + html.escape(
            "python3.12 -m venv .venv-nwb-experiment\n.venv-nwb-experiment/bin/python -m pip install --isolated --index-url https://pypi.org/simple -r projects/nwb-stream-integrity/requirements.txt ./"
            + repaired["filename"]
        )
        + "</code></pre><p>Repaired wheel SHA-256: <code>"
        + repaired["sha256"]
        + "</code></p></details>"
        + '<p><a href="../projects/nwb-stream-integrity/wheel-result.json">Download build identities, hashes and verification results (JSON)</a> · <a href="../projects/nwb-stream-integrity/build_wheels.py">Build and verification implementation</a></p>'
    )
    return body


def mne_workflow_comparison():
    project = ROOT / "projects/mne-annotation-onsets"
    result = json.loads((project / "workflow-result.json").read_text())
    profile = json.loads((project / "profile.json").read_text())
    assert result["passed"] and result["cases_per_revision"] == 32
    assert result["verified_arrays"] == 256
    for mode in ["baseline", "patched"]:
        source = result["source_and_environment"][mode]
        assert source["upstream_commit"] == profile["source_revision"]
        assert source["annotations_sha256"] == profile[f"{mode}_annotations_sha256"]
        assert source["patch_sha256"] == profile["patch_sha256"]
        assert result["counts"][mode]["default_event_mismatches"] == 0
        assert result["counts"][mode]["epoch_mismatches"] == 0
    assert result["counts"]["patched"]["attachment_onset_changes"] == 0
    counts = result["counts"]
    body = (
        '<p id="mneWorkflowStatus">Actual MNE attachment → FIF save → reopen → event extraction → four-sample epochs: '
        + str(result["cases_per_revision"])
        + " constructed cases per revision, with zero/nonzero recording offsets and relative/UTC origins. "
        + str(result["verified_arrays"])
        + " exported signal/epoch arrays were reopened and checked.</p>"
        + "<p>Attachment changed "
        + str(counts["baseline"]["attachment_onset_changes"])
        + " baseline onsets and "
        + str(counts["patched"]["attachment_onset_changes"])
        + " candidate onsets. FIF serialization still changed "
        + str(counts["patched"]["serialization_onset_changes"])
        + " candidate onsets. Default rounded events and epoch contents were correct on both revisions. "
        + "This shows the precision fix's boundary; it does not demonstrate better epoch selection than the existing default.</p>"
        + "<p>FIF annotation timestamps use float32 independently of the signal's double-precision storage. "
        + "Explicit truncation can still select an earlier sample after reopening. Some nonzero-offset UTC cases "
        + "already truncate incorrectly for the unchanged reference float. The existing default rounds event indexes.</p>"
    )
    for example in result["examples"]:
        case = example["baseline"]["input"]
        assert example["patched"]["input"] == case
        expected = example["baseline"]["expected_event_sample"]
        rows = []
        for mode, label in [("baseline", "Baseline"), ("patched", "Candidate")]:
            report = example[mode]
            assert report["expected_event_sample"] == expected
            for stage, title in [
                ("attached", "Attached"),
                ("fif_stored", "Stored in FIF"),
                ("reopened", "Reopened"),
            ]:
                values = report["stages"][stage]
                rows.append(
                    "<tr>"
                    + "".join(
                        "<td>" + html.escape(str(value)) + "</td>"
                        for value in [
                            label,
                            title,
                            repr(values["onset_seconds"]),
                            values.get("default_event_sample", "Not extracted"),
                            values.get("truncating_event_sample", "Not extracted"),
                            "Exact match"
                            if values.get("epoch_matches_expected")
                            else "Not extracted",
                        ]
                    )
                    + "</tr>"
                )
        body += (
            '<div class="table-scroll"><table class="mne-workflow-comparison"><caption>'
            + html.escape(
                f"{case['sfreq']} Hz; local sample {case['sample']}; first sample {case['first_samp']}; {case['origin']} origin. Expected event sample: {expected}."
            )
            + "</caption><thead><tr>"
            + "".join(
                '<th scope="col">' + value + "</th>"
                for value in [
                    "Revision",
                    "Stage",
                    "Onset (seconds)",
                    "Default event",
                    "Truncating event",
                    "Epoch data",
                ]
            )
            + "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )
    return (
        body
        + "<p>These are retained local/CI results. This workflow is not a hosted Execution lab recipe; opening this page starts no job.</p>"
        + '<p><a href="../projects/mne-annotation-onsets/workflow-result.json">Download workflow evidence (JSON)</a> · '
        + '<a href="../projects/mne-annotation-onsets/verify_workflow.py">Workflow implementation</a></p>'
    )


def refinebio_comparison(prefix=""):
    project = ROOT / "projects/refinebio-zero-age"
    reports = [
        json.loads((project / f"postgres-{mode}.json").read_text())
        for mode in ["baseline", "patched"]
    ]
    links = f'<a href="{prefix}projects/refinebio-zero-age/postgres-baseline.json">Baseline result</a> · <a href="{prefix}projects/refinebio-zero-age/postgres-patched.json">Patched result</a>'
    if not all(report.get("worker_export") for report in reports):
        return (
            '<p id="zeroAgeWorkflowStatus">The retained results cover database preservation. The real worker export has not executed in these results; its Linux CI replay is being prepared.</p><p>'
            + links
            + "</p>"
        )
    tables = []
    for mode, report in zip(["baseline", "patched"], reports):
        assert report["expectation"] == mode and report["workflow"] == "export"
        assert report["official_migrations_applied"] == 91
        assert report["upstream_startup_hook_loaded"] is True
        assert report["worker_export"]["existing_metadata_tests_passed"] == 5
        assert len(report["cases"]) == 5
        exports = report["worker_export"]["export_modes"]
        assert [entry["aggregate_by"] for entry in exports] == [
            "ALL",
            "EXPERIMENT",
            "SPECIES",
        ]
        ages = exports[0]["tsv_age_by_accession"]
        assert all(entry["tsv_age_by_accession"] == ages for entry in exports)
        tables.append(ages)
    rows = []
    for index, case in enumerate(reports[0]["cases"]):
        assert reports[1]["cases"][index]["input_age"] == case["input_age"]
        values = [
            case["input_age"] or "(empty)",
            *[table[f"constructed-{index}"] or "(empty)" for table in tables],
        ]
        rows.append(
            "<tr>"
            + "".join("<td>" + html.escape(value) + "</td>" for value in values)
            + "</tr>"
        )
    return (
        '<p id="zeroAgeWorkflowStatus">Actual SRA sample creation, official migrations and worker metadata export executed with constructed inputs. All three aggregation modes agree; five existing export regressions passed per revision.</p><div class="table-scroll"><table id="zeroAgeWorkflowComparison"><caption>Age in actual exported TSV files</caption><thead><tr><th scope="col">Input age</th><th scope="col">Baseline TSV</th><th scope="col">Patched TSV</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div><p>"
        + links
        + "</p><p>Results include the unmodified TSV text. ENA file reports are constructed responses. No expression processing, dispatch, upload, live-data assessment or researcher benefit is established.</p>"
    )


def shell(title, content, prefix="", active=None, scripts="", head="", main_class=""):
    page = (SITE / "template.html").read_text()
    page = (
        page.replace("__TITLE__", html.escape(title))
        .replace("__ROOT__", prefix)
        .replace("__MAIN_CLASS__", main_class)
        .replace("<!--__CONTENT__-->", content)
        .replace("<!--__EXTRA_HEAD__-->", head)
        .replace("<!--__SCRIPTS__-->", scripts)
    )
    if active:
        target = f'href="{prefix}{active}"'
        page = page.replace(target + ">", target + ' aria-current="page">')
    return "\n".join(line.rstrip() for line in page.splitlines()) + "\n"


def problem_content(problem, data):
    escape = html.escape
    detail = problem.get("page")
    demo = next(
        (d for d in data["demonstrations"] if d["problem"] == problem["id"]), None
    )
    validation = next(
        (v for v in data["validation"] if v["problem"] == problem["id"]), None
    )

    def paragraph(text):
        return "<p>" + escape(text) + "</p>"

    def link(text, target, new_tab=False):
        external = target.startswith("https://")
        href = target if external or target.startswith("#") else "../" + target
        attrs = (
            ' target="_blank" rel="noopener noreferrer"' if external or new_tab else ""
        )
        return f'<a href="{escape(href, quote=True)}"{attrs}>' + escape(text) + "</a>"

    def section(title, content, anchor):
        return (
            f'<section id="{anchor}"><h2>'
            + escape(title)
            + "</h2>"
            + content
            + "</section>"
        )

    title = detail["title"] if detail else problem["title"]
    heading = "<h1>" + escape(title) + "</h1>"
    heading += (
        '<p class="problem-lede">'
        + escape(detail["summary"] if detail else problem["need"])
        + "</p>"
    )
    state = (
        validation["verdict"]
        if validation
        else "Research only; no Kufu solution implemented"
    )
    heading += '<p class="problem-state">' + escape(state) + "</p>"
    story = [
        section(
            "Who encounters it and why it matters",
            paragraph(problem["audience"]) + paragraph(problem["value"]),
            "people",
        )
    ]
    if detail:
        terms = (
            '<dl class="problem-terms">'
            + "".join(
                "<dt>" + escape(term) + "</dt><dd>" + escape(meaning) + "</dd>"
                for term, meaning in detail["terms"]
            )
            + "</dl>"
        )
        story.append(
            section(
                "Science and terms", paragraph(detail["science"]) + terms, "science"
            )
        )
        workflow = (
            '<ol class="problem-workflow">'
            + "".join(
                "<li><strong>"
                + escape(step)
                + "</strong>"
                + paragraph(description)
                + "</li>"
                for step, description in detail["workflow"]
            )
            + "</ol>"
        )
        story.append(section("Where the problem appears", workflow, "workflow"))
    sources = (
        "<ul>"
        + "".join(
            "<li>" + link(source["title"], source["url"]) + "</li>"
            for source in problem["sources"]
        )
        + "</ul>"
        if problem["sources"]
        else paragraph(
            "No direct primary problem report is selected. This remains an unvalidated concept."
        )
    )
    story.append(
        section(
            "Evidence and existing tools",
            paragraph(problem["baseline"]) + sources,
            "evidence",
        )
    )
    if detail:
        story.append(
            section(
                "The solution being tested",
                paragraph(detail["solution"]) + paragraph(problem["integration"]),
                "solution",
            )
        )
        if problem["id"] == "zero-age-metadata":
            comparison = refinebio_comparison("../")
        else:
            rows = detail["comparison"]
            if problem["id"] == "nwb-stream-integrity":
                # Present values from the retained real round trips, including CI refreshes.
                reports = [
                    json.loads(
                        (
                            ROOT / f"projects/nwb-stream-integrity/{mode}.json"
                        ).read_text()
                    )
                    for mode in ["baseline", "patched"]
                ]
                rows = [rows[0]]
                for size in [50, 100, 500]:
                    counts = []
                    for report in reports:
                        values = {
                            case["rows_replaced_by_zeros"]
                            for case in report["cases"]
                            if case["rows"] == size and case["inspect_before_write"]
                        }
                        assert len(values) == 1
                        counts.append(str(values.pop()))
                    rows.append([str(size), *counts])
            if problem["id"] == "deleted-flags":
                reports = [
                    json.loads(
                        (
                            ROOT
                            / f"projects/movement-edit-filtering/deletion-{mode}.json"
                        ).read_text()
                    )
                    for mode in ["baseline", "patched"]
                ]
                rows = [rows[0]]
                for name, label in [
                    ("deletion_only", "Deletion only"),
                    ("deletion_and_move", "Deletion plus move"),
                    ("never_detected", "Never detected"),
                ]:
                    flags = [
                        report["observations"][name]["flag_second"]
                        for report in reports
                    ]
                    rows.append(
                        [
                            label,
                            *[
                                "No edit variable"
                                if flag is None
                                else str(flag).lower()
                                for flag in flags
                            ],
                        ]
                    )
                for field, label in [
                    ("flag_after_first_save", "Qt deletion: first Save"),
                    (
                        "flag_after_second_save",
                        "Qt deletion: second Save after reopening",
                    ),
                    ("flag_in_final_loader", "Qt deletion: flag in final loader"),
                ]:
                    flags = [report["rendered"][field] for report in reports]
                    rows.append(
                        [
                            label,
                            *[
                                "No edit variable"
                                if value is None
                                else str(value).lower()
                                for value in flags
                            ],
                        ]
                    )
                for mode, source, filename in [
                    (1, "before-delete.png", "deletion-before.png"),
                    (1, "after-delete.png", "deletion-after-delete.png"),
                    (0, "after-reexport-reload.png", "deletion-baseline-reloaded.png"),
                    (1, "after-reexport-reload.png", "deletion-patched-reloaded.png"),
                ]:
                    image = ROOT / "projects/movement-edit-filtering" / filename
                    assert (
                        hashlib.sha256(image.read_bytes()).hexdigest()
                        == reports[mode]["rendered"]["captures"][source]
                    )
            if problem["id"] == "eeg-events":
                reports = [
                    json.loads(
                        (
                            ROOT / f"projects/mne-annotation-onsets/{mode}.json"
                        ).read_text()
                    )
                    for mode in ["baseline", "patched"]
                ]
                rows = [rows[0]]
                assert len(reports[0]["observations"]) == len(
                    reports[1]["observations"]
                )
                for before, after in zip(
                    reports[0]["observations"], reports[1]["observations"]
                ):
                    assert before["sfreq_hz"] == after["sfreq_hz"]
                    assert (
                        before["sample_index_before"]
                        == after["sample_index_before"]
                        == 1
                    )
                    assert (
                        before["sample_index_with_rounding"]
                        == after["sample_index_with_rounding"]
                        == 1
                    )
                    rows.append(
                        [
                            str(before["sfreq_hz"]),
                            str(before["sample_index_after"]),
                            str(after["sample_index_after"]),
                            "1",
                        ]
                    )
            comparison = (
                '<div class="table-scroll"><table><caption>'
                + escape(detail["comparisonTitle"])
                + "</caption><thead><tr>"
                + "".join(
                    '<th scope="col">' + escape(value) + "</th>" for value in rows[0]
                )
                + "</tr></thead><tbody>"
                + "".join(
                    "<tr>"
                    + "".join("<td>" + escape(value) + "</td>" for value in row)
                    + "</tr>"
                    for row in rows[1:]
                )
                + "</tbody></table></div>"
            )
        story.append(
            section(
                detail["comparisonTitle"],
                paragraph(detail["comparisonNote"]) + comparison,
                "before-after",
            )
        )
        if problem["id"] == "deleted-flags":
            story.append(
                section(
                    "Upstream draft validation",
                    movement_upstream_comparison(),
                    "upstream-validation",
                )
            )
        if problem["id"] == "nwb-stream-integrity":
            story.append(
                section(
                    "Electrode recording conversion example",
                    ecephys_walkthrough(),
                    "electrode-conversion",
                )
            )
        if problem["id"] == "nwb-stream-integrity":
            story.append(
                section(
                    "Installable experimental builds",
                    nwb_build_downloads(),
                    "installable-builds",
                )
            )
        if problem["id"] == "eeg-events":
            story.append(
                section(
                    "Save, reopen and select analysis samples",
                    mne_workflow_comparison(),
                    "host-workflow",
                )
            )
        execution = detail["execution"]
        actions = link(
            execution["action"],
            demo["href"] if demo["href"] else demo["verifiedRun"],
            new_tab=True,
        )
        actions += link("Saved result (JSON)", demo["result"], new_tab=True)
        if demo["href"]:
            actions += link("View verified run", demo["verifiedRun"])
        runtime = (
            '<p class="execution-kind">'
            + escape(execution["label"])
            + "</p>"
            + paragraph(execution["summary"])
            + '<div class="problem-actions">'
            + actions
            + "</div>"
        )
        runtime += (
            '<details class="reproduction"><summary>How to reproduce locally</summary>'
            + paragraph(demo["runtime"])
            + paragraph(
                "These are instructions for your own environment. Opening this section does not execute the command."
            )
            + "<pre><code>"
            + escape(demo["command"])
            + "</code></pre>"
            + link(
                "Full environment and reproduction record",
                data["documents"][demo["record"]],
            )
            + "</details>"
        )
        story.append(section("Try or reproduce", runtime, "try"))
    else:
        no_fix = (
            "No corrective patch is implemented for this reproduced defect."
            if validation
            else "No Kufu implementation or demonstration is available for this candidate."
        )
        story.append(
            section(
                "Proposed direction",
                paragraph(problem["proposal"])
                + paragraph(no_fix)
                + paragraph(problem["integration"]),
                "solution",
            )
        )
        if validation:
            runtime = paragraph(
                "Recorded failure; no corrective patch. The existing CI replay reproduces the defect. Opening this page starts no workflow or background computation."
            )
            runtime += link(
                "View the failure reproduction run",
                data["demonstrations"][0]["verifiedRun"],
            )
        else:
            runtime = paragraph(
                "Research only. This page describes an investigation; it starts no software workflow or background computation."
            )
        story.append(section("What runs here", runtime, "try"))
    if validation:
        result = (
            paragraph(validation["observed"])
            + "<h3>What remains unverified</h3>"
            + paragraph(validation["remaining"])
            + "<h3>What would count as resolving it</h3>"
            + paragraph(validation["criterion"])
        )
    else:
        result = paragraph(problem["unknown"]) + paragraph(
            "A source, challenge or plausible idea does not establish a missing software capability or a useful new product. No successful Kufu intervention is claimed."
        )
    story.append(section("Validation and limits", result, "validation"))
    story.append(
        section(
            "Next step",
            paragraph(validation["next"] if validation else problem["next"]),
            "next",
        )
    )
    records = list(
        dict.fromkeys(
            [
                problem["record"],
                *[
                    entry["record"]
                    for entry in data["explorations"]
                    if entry["problem"] == problem["id"]
                ],
            ]
        )
    )
    technical = ""
    if demo:
        technical += (
            "<ul><li>"
            + link("Code implementation", demo["implementation"])
            + "</li><li>"
            + link("Replay and verification code", demo["verificationCode"])
            + "</li><li>"
            + link("All verification runs", data["verificationRuns"])
            + "</li></ul>"
        )
    technical += (
        "<ul>"
        + "".join(
            "<li>"
            + link(
                "Detailed record: "
                + (ROOT / name).read_text().splitlines()[0].lstrip("# "),
                data["documents"][name],
            )
            + "</li>"
            for name in records
        )
        + "</ul>"
    )
    story.append(
        section(
            "Implementation and research records" if demo else "Research records",
            technical,
            "records",
        )
    )
    context = (
        "<h2>At a glance</h2><dl><dt>Domain</dt><dd>"
        + escape(problem["domain"])
        + "</dd><dt>Work state</dt><dd>"
        + escape(problem["stage"])
        + "</dd><dt>Evidence basis</dt><dd>"
        + escape(problem["evidence"])
        + "</dd><dt>Source review</dt><dd>"
        + escape(problem["reviewed"])
        + "</dd></dl>"
    )
    context += '<p class="context-note">The website explains the work and displays saved evidence. It does not start Python or a scientific service when you open a page.</p>'
    if problem["boards"]:
        context += "<h3>Where this was investigated</h3><ul>"
        for board_id in problem["boards"]:
            board = next(board for board in data["boards"] if board["id"] == board_id)
            context += "<li>" + link(board["title"], board["url"]) + "</li>"
        context += "</ul>"
    if detail and detail.get("related"):
        context += "<h3>Related problems</h3><ul>"
        for related_id in detail["related"]:
            related = next(p for p in data["problems"] if p["id"] == related_id)
            context += (
                "<li>"
                + link(
                    related.get("page", {}).get("title", related["title"]),
                    related["href"],
                )
                + "</li>"
            )
        context += "</ul>"
    return (SITE / "views/problem.html").read_text().replace(
        "<!--__PROBLEM_HEADING__-->", heading
    ).replace("<!--__PROBLEM_STORY__-->", "\n".join(story)).replace(
        "<!--__PROBLEM_CONTEXT__-->", context
    ), title


def main():
    data = json.loads((SITE / "catalog.json").read_text())
    docs = sorted([*ROOT.glob("research/**/*.md"), *ROOT.glob("projects/**/*.md")])
    docs += [
        ROOT / "README.md",
        ROOT / "WORKSPACE.md",
        SITE / "README.md",
        SITE / "VALIDATION.md",
        SITE / "DELIVERY.md",
    ]
    paths = {p.relative_to(ROOT).as_posix(): p for p in docs}
    data["documents"] = {name: "site/records/" + slug(name) for name in paths}
    ids = [p["id"] for p in data["problems"]]
    assert len(set(ids)) == len(ids), "Duplicate problem IDs"
    boards = {b["id"] for b in data["boards"]}
    assert len(boards) == len(data["boards"]), "Duplicate board IDs"
    for p in data["problems"]:
        assert set(p["boards"]) <= boards, p["id"]
        assert p["record"] in paths, p["record"]
        assert p["stage"] != "Solved", "Resolution needs independent evidence"
        assert re.fullmatch(r"[a-z0-9-]+", p["id"])
        assert p["href"] == f"problems/{p['id']}.html"
        for s in p["sources"]:
            assert urlsplit(s["url"]).scheme == "https", s
    for b in data["boards"]:
        assert urlsplit(b["url"]).scheme == "https", b
    for e in data["explorations"]:
        assert (ROOT / e["href"]).is_file(), e["href"]
        assert e["record"] in paths and e["problem"] in ids
    for v in data["validation"]:
        assert v["problem"] in ids
    for demo in data["demonstrations"]:
        assert demo["record"] in paths
        assert demo["problem"] in ids
        assert next(p for p in data["problems"] if p["id"] == demo["problem"]).get(
            "page"
        )
        assert (ROOT / demo["result"]).is_file()
        if demo["href"]:
            assert (ROOT / urlsplit(demo["href"]).path).is_file()
    RECORDS.mkdir(exist_ok=True)
    for generated in RECORDS.glob("*.html"):
        generated.unlink()

    def href(raw, source):
        parsed = urlsplit(raw)
        if parsed.scheme:
            return raw if parsed.scheme == "https" else "#unsupported-link"
        if raw.startswith("#"):
            return raw
        target = posixpath.normpath(str(source.parent.relative_to(ROOT) / parsed.path))
        assert not target.startswith("../"), (source.name, raw)
        tail = ("#" + parsed.fragment) if parsed.fragment else ""
        if target in paths:
            return slug(target) + tail
        return "../../" + target + tail

    def inline(text, source):
        # Escape all raw HTML. Interpret only Markdown links, code and emphasis.
        parts = re.split(r"(`[^`]+`|\[[^\]]+\]\([^\s)]+\))", text)
        rendered = []
        for part in parts:
            if part.startswith("`") and part.endswith("`"):
                rendered.append("<code>" + html.escape(part[1:-1]) + "</code>")
            elif match := re.fullmatch(r"\[([^\]]+)\]\(([^\s)]+)\)", part):
                destination = html.escape(href(match[2], source), quote=True)
                rendered.append(f'<a href="{destination}">{html.escape(match[1])}</a>')
            else:
                escaped = html.escape(part)
                rendered.append(
                    re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
                )
        return "".join(rendered)

    def render(source):
        blocks, paragraph, table = [], [], []
        fenced = False
        code = []

        def flush():
            if paragraph:
                blocks.append("<p>" + inline(" ".join(paragraph), source) + "</p>")
                paragraph.clear()
            if table:
                rows = [row.strip().strip("|").split("|") for row in table]
                blocks.append('<div class="table"><table>')
                for i, row in enumerate(rows):
                    if all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in row):
                        continue
                    cell = "th" if i == 0 else "td"
                    blocks.append(
                        "<tr>"
                        + "".join(
                            f"<{cell}>" + inline(c.strip(), source) + f"</{cell}>"
                            for c in row
                        )
                        + "</tr>"
                    )
                blocks.append("</table></div>")
                table.clear()

        for line in source.read_text().splitlines():
            if line.startswith("```"):
                flush()
                if fenced:
                    blocks.append(
                        "<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"
                    )
                    code.clear()
                fenced = not fenced
            elif fenced:
                code.append(line)
            elif not line.strip():
                flush()
            elif line.startswith("|"):
                if paragraph:
                    flush()
                table.append(line)
            elif m := re.match(r"^(#{1,6})\s+(.*)", line):
                flush()
                level = len(m[1])
                anchor = re.sub(r"[^\w\s-]", "", m[2].lower()).replace(" ", "-")
                blocks.append(
                    f'<h{level} id="{anchor}">' + inline(m[2], source) + f"</h{level}>"
                )
            elif re.match(r"^(- |\d+\. )", line):
                flush()
                # Individual list items retain semantics without inferring nesting.
                item = re.sub(r"^(- |\d+\. )", "", line)
                blocks.append("<ul><li>" + inline(item, source) + "</li></ul>")
            else:
                if table:
                    flush()
                paragraph.append(line)
        flush()
        return "\n".join(blocks)

    css = "main.research-document{max-width:1000px;background:white}main.research-document h1{font:30px/1.3 Georgia,serif}main.research-document h2{margin-top:35px}main.research-document pre{background:#eaf0f7;padding:20px;overflow:auto}main.research-document table{border-collapse:collapse;font-size:14px;min-width:600px}main.research-document th,main.research-document td{text-align:left;vertical-align:top;border:1px solid #d8e2ec;padding:10px}main.research-document .table{overflow:auto}main.research-document img{max-width:100%}"
    for name, source in paths.items():
        title = source.read_text().splitlines()[0].lstrip("# ")
        content = (
            '<p class="record-note">Research record. Current problem pages explain the result and its limits; older decisions below are retained as history.</p>'
            + render(source)
        )
        page = shell(
            title,
            content,
            "../../",
            head="<style>" + css + "</style>",
            main_class="research-document",
        )
        (RECORDS / slug(name)).write_text(page)
    problem_directory = ROOT / "problems"
    problem_directory.mkdir(exist_ok=True)
    for generated in problem_directory.glob("*.html"):
        generated.unlink()
    for problem in data["problems"]:
        content, title = problem_content(problem, data)
        (ROOT / problem["href"]).write_text(
            shell(title, content, "../", "problems.html", main_class="problem-detail")
        )
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    pages = {
        "index": "Home",
        "explorations": "Explorations",
        "problems": "Problems",
        "sources": "Sources",
        "validation": "Validation",
        "lab": "Execution lab",
    }
    for filename, title in pages.items():
        view = "home" if filename == "index" else filename
        content = (SITE / "views" / f"{view}.html").read_text()
        if filename == "problems":
            rows = []
            for problem in data["problems"]:
                title_text = problem.get("page", {}).get("title", problem["title"])
                fields = [
                    title_text,
                    problem["domain"],
                    problem["stage"],
                    problem["evidence"],
                ]
                spans = "".join(
                    '<span class="' + cls + '">' + html.escape(value) + "</span>"
                    for cls, value in zip(
                        ["title", "domain", "stage", "evidence"], fields
                    )
                )
                rows.append(
                    '<a class="problem problem-row" id="problem-'
                    + problem["id"]
                    + '" href="'
                    + problem["href"]
                    + '">'
                    + spans
                    + "</a>"
                )
            content = content.replace("<!--__PROBLEM_ROWS__-->", "".join(rows))
        scripts = (
            "<script>const CATALOG = "
            + payload
            + ';</script><script src="site/app.js"></script>'
        )
        active = (
            filename + ".html"
            if filename in ["index", "problems", "sources", "lab"]
            else None
        )
        (ROOT / f"{filename}.html").write_text(
            shell(title, content, active=active, scripts=scripts)
        )
    report = {
        "pages": list(pages),
        "demonstrations": len(data["demonstrations"]),
        "problems": len(ids),
        "boards": len(boards),
        "explorations": len(data["explorations"]),
        "research_pages": len(paths),
        "problem_pages": len(data["problems"]),
        "catalog_sha256": hashlib.sha256(
            (SITE / "catalog.json").read_bytes()
        ).hexdigest(),
    }
    (SITE / "build-result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
