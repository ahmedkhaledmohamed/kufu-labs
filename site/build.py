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


def refinebio_comparison():
    project = ROOT / "projects/refinebio-zero-age"
    reports = [
        json.loads((project / f"postgres-{mode}.json").read_text())
        for mode in ["baseline", "patched"]
    ]
    links = '<a href="projects/refinebio-zero-age/postgres-baseline.json">Baseline result</a> · <a href="projects/refinebio-zero-age/postgres-patched.json">Patched result</a>'
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
        '<p id="zeroAgeWorkflowStatus">Actual SRA sample creation, official migrations and worker metadata export executed with constructed inputs. All three aggregation modes agree; five existing export regressions passed per revision.</p><table id="zeroAgeWorkflowComparison"><caption>Age in actual exported TSV files</caption><thead><tr><th>Input age</th><th>Baseline TSV</th><th>Patched TSV</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table><p>"
        + links
        + "</p><p>Results include the unmodified TSV text. ENA file reports are constructed responses. No expression processing, dispatch, upload, live-data assessment or researcher benefit is established.</p>"
    )


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

    css = 'body{font:16px/1.7 "Trebuchet MS",Arial,sans-serif;color:#203b50;background:#f4f7fb;margin:0}header,main{max-width:1000px;margin:auto;padding:25px}header{border-bottom:1px solid #d8e2ec}a{color:#3156a0;text-underline-offset:3px}:focus-visible{outline:3px solid #397eaa;outline-offset:3px}main{background:white}h1{font:30px/1.3 Georgia,serif}h2{font-size:23px;margin-top:35px}h3{font-size:19px}p,li{max-width:78ch}pre{background:#eaf0f7;padding:20px;overflow:auto;border-radius:6px}code{font-size:13px;overflow-wrap:anywhere}table{border-collapse:collapse;font-size:14px;min-width:600px}th,td{text-align:left;vertical-align:top;border:1px solid #d8e2ec;padding:10px}.table{overflow:auto}ul{padding-left:25px;margin:8px 0}.note{font-size:13px;color:#64788a}img{max-width:100%}'
    for name, source in paths.items():
        title = source.read_text().splitlines()[0].lstrip("# ")
        page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head><body><header><a href="../../index.html">Kufu Labs</a><p class="note">Research record. Read the current hub validation ledger before interpreting historical decisions.</p></header><main>{render(source)}</main></body></html>\n'
        (RECORDS / slug(name)).write_text(page)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    pages = {
        "index": "Home",
        "explorations": "Explorations",
        "problems": "Problems",
        "sources": "Sources",
        "validation": "Validation",
    }
    template = (SITE / "template.html").read_text()
    for filename, title in pages.items():
        view = "home" if filename == "index" else filename
        content = (SITE / "views" / f"{view}.html").read_text()
        content = content.replace(
            "<!--__ZERO_AGE_WORKFLOW__-->", refinebio_comparison()
        )
        # Cross-page links are ordinary documents, never section navigation.
        content = content.replace('href="#validation"', 'href="validation.html"')
        page = (
            template.replace("__TITLE__", title)
            .replace("<!--__CONTENT__-->", content)
            .replace("/*__CATALOG__*/", "const CATALOG = " + payload + ";")
        )
        (ROOT / f"{filename}.html").write_text(page)
    report = {
        "pages": list(pages),
        "demonstrations": len(data["demonstrations"]),
        "problems": len(ids),
        "boards": len(boards),
        "explorations": len(data["explorations"]),
        "research_pages": len(paths),
        "catalog_sha256": hashlib.sha256(
            (SITE / "catalog.json").read_bytes()
        ).hexdigest(),
    }
    (SITE / "build-result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
