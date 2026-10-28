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
const problemById = (id) => CATALOG.problems.find((p) => p.id === id);
function redirectLegacy() {
  const current = location.pathname.split("/").pop();
  if (current === "problems.html" && location.hash.startsWith("#problem-")) {
    const problem = problemById(location.hash.slice("#problem-".length));
    if (problem) location.replace(problem.href);
  }
  if (current === "explorations.html" && location.hash.startsWith("#demo-")) {
    const demo = CATALOG.demonstrations.find(
      (d) => d.id === location.hash.slice(6),
    );
    if (demo) location.replace(problemById(demo.problem).href + "#try");
  }
  if (
    current === "validation.html" &&
    ["#zeroAgeWorkflowComparison", "#zeroAgeWorkflowTitle"].includes(
      location.hash,
    )
  ) {
    location.replace(problemById("zero-age-metadata").href + "#before-after");
  }
}
redirectLegacy();
window.addEventListener("hashchange", redirectLegacy);
function options(id, values, all) {
  const select = $(id);
  select.append(new Option(all, ""));
  values.forEach(([value, text]) => select.append(new Option(text, value)));
}
if ($("problemList")) {
  $("filters").hidden = false;
  options(
    "domain",
    [...new Set(CATALOG.problems.map((p) => p.domain))]
      .sort()
      .map((value) => [value, value]),
    "All domains",
  );
  options(
    "stage",
    [...new Set(CATALOG.problems.map((p) => p.stage))].map((value) => [
      value,
      value,
    ]),
    "All states",
  );
  options(
    "sourceFilter",
    CATALOG.boards.map((board) => [board.id, board.title]),
    "All source boards",
  );
  function applyFilters() {
    const query = $("search").value.trim().toLowerCase();
    let count = 0;
    for (const problem of CATALOG.problems) {
      const match =
        (!query || JSON.stringify(problem).toLowerCase().includes(query)) &&
        (!$("domain").value || problem.domain === $("domain").value) &&
        (!$("stage").value || problem.stage === $("stage").value) &&
        (!$("sourceFilter").value ||
          problem.boards.includes($("sourceFilter").value));
      $("problem-" + problem.id).hidden = !match;
      if (match) count++;
    }
    $("empty").hidden = count !== 0;
    $("problemCount").textContent =
      `${count} of ${CATALOG.problems.length} problems shown`;
  }
  $("filters").addEventListener("submit", (event) => event.preventDefault());
  for (const id of ["search", "domain", "stage", "sourceFilter"])
    $(id).addEventListener("input", applyFilters);
  $("filters").addEventListener("reset", (event) => {
    event.preventDefault();
    for (const id of ["search", "domain", "stage", "sourceFilter"])
      $(id).value = "";
    applyFilters();
  });
  const source = new URLSearchParams(location.search).get("source");
  if (source) $("sourceFilter").value = source;
  applyFilters();
}
if ($("sourceList")) {
  for (const board of CATALOG.boards) {
    const article = node("article", undefined, "sourceboard"),
      heading = node("h3");
    heading.append(link(board.title, board.url));
    article.append(
      node("div", board.kind, "kind"),
      heading,
      node("p", board.scope),
      node("p", board.limit, "limit"),
      node("p", board.access, "date"),
    );
    const button = node("button", "Show related problems");
    button.type = "button";
    button.addEventListener("click", () => {
      location.href = "problems.html?source=" + encodeURIComponent(board.id);
    });
    article.append(button);
    $("sourceList").append(article);
  }
}
if ($("explorationList")) {
  for (const demo of CATALOG.demonstrations) {
    const problem = problemById(demo.problem),
      article = node("article", undefined, "exploration"),
      heading = node("h2");
    heading.append(link(problem.page.title, problem.href));
    article.append(
      heading,
      node("span", problem.page.execution.label, "state"),
      node("p", problem.page.summary),
    );
    $("explorationList").append(article);
  }
}
if ($("validationList")) {
  for (const validation of CATALOG.validation) {
    const problem = problemById(validation.problem),
      article = node("article"),
      heading = node("h2");
    heading.append(link(problem.page?.title || problem.title, problem.href));
    article.append(heading, node("p", validation.verdict, "verdictlabel"));
    $("validationList").append(article);
  }
}
if ($("coverage")) $("coverage").textContent = CATALOG.coverage;
if ($("sourceCount"))
  $("sourceCount").textContent =
    `${CATALOG.boards.length} source boards and directories`;
if ($("maintenance"))
  $("maintenance").textContent =
    `Catalogue updated ${CATALOG.updated}. Evidence review dates are shown per problem and source board. These are recorded investigations, not a live status feed.`;
