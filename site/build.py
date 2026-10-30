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
            assert (ROOT / demo["href"]).is_file()
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
