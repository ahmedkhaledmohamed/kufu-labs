"use strict";
const $ = (id) => document.getElementById(id);
function node(tag, text, className) {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (className) n.className = className;
  return n;
}
function link(title, href) {
  const a = node("a", title);
  a.href = href;
  if (/^https:\/\//.test(href)) {
    a.target = "_blank";
    a.rel = "noopener noreferrer";
  }
  return a;
}
const record = (p) => CATALOG.documents[p];
const problemById = (id) => CATALOG.problems.find((p) => p.id === id);
function options(id, values, all) {
  const s = $(id);
  s.append(new Option(all, ""));
  values.forEach(([v, t]) => s.append(new Option(t, v)));
}
if ($("problemList")) {
  options(
    "domain",
    [...new Set(CATALOG.problems.map((p) => p.domain))]
      .sort()
      .map((v) => [v, v]),
    "All domains",
  );
  options(
    "stage",
    [...new Set(CATALOG.problems.map((p) => p.stage))].map((v) => [v, v]),
    "All states",
  );
  options(
    "sourceFilter",
    CATALOG.boards.map((b) => [b.id, b.title]),
    "All source boards",
  );
  function field(title, text) {
    const f = node("div", undefined, "field");
    f.append(node("h4", title), node("p", text));
    return f;
  }
  const problemNodes = [];
  for (const p of CATALOG.problems) {
    const d = node("details", undefined, "problem");
    d.id = "problem-" + p.id;
    const summary = node("summary");
    summary.append(
      node("span", p.title, "title"),
      node("span", p.domain, "domain"),
      node("span", p.stage, "stage"),
      node("span", p.evidence, "evidence"),
    );
    d.append(summary);
    const body = node("div", undefined, "body");
    body.append(
      field("Reported need / starting concept", p.need),
      field("Possible contribution", p.proposal),
      field("Existing tools and counterevidence", p.baseline),
      field("Integration route", p.integration),
      field("Limits and unresolved assumptions", p.unknown),
      field("Next validation action", p.next),
    );
    const sources = node("div", undefined, "field");
    sources.append(node("h4", "Primary reports and existing alternatives"));
    if (p.sources.length) {
      const ul = node("ul");
      for (const s of p.sources) {
        const li = node("li");
        li.append(link(s.title, s.url));
        ul.append(li);
      }
      sources.append(ul);
    } else
      sources.append(
        node(
          "p",
          "No direct primary problem report selected. Retained as an unvalidated concept.",
        ),
      );
    body.append(sources);
    const boards = node("div", undefined, "field");
    boards.append(node("h4", "Discovery boards"));
    if (p.boards.length) {
      const ul = node("ul");
      for (const id of p.boards) {
        const b = CATALOG.boards.find((b) => b.id === id),
          li = node("li");
        li.append(link(b.title, b.url));
        ul.append(li);
      }
      boards.append(ul);
    } else
      boards.append(
        node(
          "p",
          "No specific board established; see the linked research record.",
        ),
      );
    body.append(boards);
    const foot = node("div", undefined, "recordlink");
    foot.append(
      link("Read the full investigation", record(p.record)),
      document.createTextNode(
        ` · Evidence reviewed ${p.reviewed}. Resolution is not established by this work state.`,
      ),
    );
    body.append(foot);
    d.append(body);
    $("problemList").append(d);
    problemNodes.push([p, d]);
  }
  function applyFilters() {
    const query = $("search").value.trim().toLowerCase(),
      domain = $("domain").value,
      stage = $("stage").value,
      source = $("sourceFilter").value;
    let count = 0;
    for (const [p, d] of problemNodes) {
      const match =
        (!query || JSON.stringify(p).toLowerCase().includes(query)) &&
        (!domain || p.domain === domain) &&
        (!stage || p.stage === stage) &&
        (!source || p.boards.includes(source));
      d.hidden = !match;
      if (match) count++;
    }
    $("empty").hidden = count !== 0;
    $("problemCount").textContent =
      `${count} of ${CATALOG.problems.length} problems shown`;
  }
  $("filters").addEventListener("submit", (e) => e.preventDefault());
  for (const id of ["search", "domain", "stage", "sourceFilter"])
    $(id).addEventListener("input", applyFilters);
  $("filters").addEventListener("reset", (e) => {
    e.preventDefault();
    for (const id of ["search", "domain", "stage", "sourceFilter"])
      $(id).value = "";
    applyFilters();
  });
  function openHash() {
    if (location.hash.startsWith("#problem-")) {
      const target = document.getElementById(location.hash.slice(1));
      if (target) {
        $("filters").reset();
        target.open = true;
        target.scrollIntoView({ block: "start" });
      }
    }
  }
  const requestedSource = new URLSearchParams(location.search).get("source");
  if (requestedSource) $("sourceFilter").value = requestedSource;
  applyFilters();
  openHash();
  window.addEventListener("hashchange", openHash);
}
if ($("sourceList"))
  for (const b of CATALOG.boards) {
    const article = node("article", undefined, "sourceboard"),
      h = node("h3");
    h.append(link(b.title, b.url));
    article.append(
      node("div", b.kind, "kind"),
      h,
      node("p", b.scope),
      node("p", b.limit, "limit"),
      node("p", b.access, "date"),
    );
    const button = node("button", "Show related problems");
    button.type = "button";
    button.addEventListener("click", () => {
      location.href = "problems.html?source=" + encodeURIComponent(b.id);
    });
    article.append(button);
    $("sourceList").append(article);
  }
if ($("validationList"))
  for (const v of CATALOG.validation) {
    const p = problemById(v.problem),
      article = node("article"),
      title = node("div"),
      h = node("h3");
    h.append(link(p.title, `problems.html#problem-${p.id}`));
    title.append(h, node("p", v.verdict, "verdictlabel"));
    const evidence = node("div");
    for (const [label, text] of [
      ["Observed", v.observed],
      ["Pinned baseline", v.baseline],
      ["Still missing", v.remaining],
      ["Resolution criterion", v.criterion],
      ["Next check", v.next],
    ]) {
      const p = node("p");
      p.append(node("strong", label), document.createTextNode(text));
      evidence.append(p);
    }
    article.append(title, evidence);
    $("validationList").append(article);
  }
if ($("coverage")) $("coverage").textContent = CATALOG.coverage;
if ($("sourceCount"))
  $("sourceCount").textContent =
    `${CATALOG.boards.length} source boards and directories`;
if ($("maintenance"))
  $("maintenance").textContent =
    `Snapshot updated ${CATALOG.updated}. The three active contribution records and selected competing PRs were checked against GitHub issue/PR APIs on this date. General candidate evidence dates are shown per problem. Broader claims remain unverified unless backed by an explicit result.`;

if ($("explorationList")) {
  for (const x of CATALOG.explorations) {
    const article = node("article", undefined, "exploration"),
      heading = node("h3");
    heading.append(link(x.title, record(x.href) || x.href));
    article.append(
      heading,
      node("span", x.state, "state"),
      node("p", x.summary),
    );
    const refs = node("div", undefined, "record");
    refs.append(
      link("Project record", record(x.record)),
      document.createTextNode(" · "),
      link("Problem and evidence", `problems.html#problem-${x.problem}`),
    );
    const demo = CATALOG.demonstrations.find((d) => d.id === x.id);
    if (demo)
      refs.append(
        document.createTextNode(" · "),
        link("Code implementation", demo.implementation),
      );
    article.append(refs);
    $("explorationList").append(article);
  }
}

if ($("demoList"))
  for (const d of CATALOG.demonstrations) {
    const a = node("article", undefined, "demo-entry");
    a.id = "demo-" + d.id;
    a.append(node("h3", d.title), node("p", d.runtime));
    for (const [label, text] of [
      ["Inputs", d.inputs],
      ["Expected result", d.expected],
      ["Verification", d.verification],
      ["Limits", d.limits],
    ]) {
      const p = node("p");
      p.append(node("strong", label + ": "), document.createTextNode(text));
      a.append(p);
    }
    const pre = node("pre", d.command);
    pre.setAttribute("aria-label", "Reproduction command");
    a.append(pre);
    const actions = node("div", undefined, "demo-actions");
    if (d.href) {
      const open = link("Open interactive demo", d.href);
      open.target = "_blank";
      open.rel = "noopener noreferrer";
      actions.append(open);
    }
    actions.append(
      link("Code implementation", d.implementation),
      link("Verification code", d.verificationCode),
      link("Reproduction and source record", record(d.record)),
      link("Recorded result", d.result),
      link("Verification runs", CATALOG.verificationRuns),
    );
    a.append(actions);
    $("demoList").append(a);
  }
const current = location.pathname.split("/").pop() || "index.html";
document.querySelectorAll("nav a").forEach((a) => {
  if (a.getAttribute("href") === current)
    a.setAttribute("aria-current", "page");
});
