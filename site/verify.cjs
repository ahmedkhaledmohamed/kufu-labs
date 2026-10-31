// Verify the packaged hub locally or at its authenticated deployment URL.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const crypto = require("node:crypto");
const path = require("node:path");
const { pathToFileURL, fileURLToPath } = require("node:url");
const root = path.resolve(
  process.env.HUB_ROOT || path.join(__dirname, "..", "dist"),
);
const output = path.resolve(
  process.env.HUB_OUTPUT || path.join(__dirname, "..", ".runs", "hub"),
);
const base = process.env.HUB_URL
  ? new URL(process.env.HUB_URL).origin + "/"
  : pathToFileURL(root + path.sep).href;
const url = (file) => new URL(file, base).href;
(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME_PATH
      ? { executablePath: process.env.CHROME_PATH }
      : {}),
  });
  const headers = process.env.VERCEL_AUTOMATION_BYPASS_SECRET
    ? {
        "x-vercel-protection-bypass":
          process.env.VERCEL_AUTOMATION_BYPASS_SECRET,
      }
    : {};
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    extraHTTPHeaders: headers,
  });
  if (!process.env.HUB_URL)
    await context.tracing.start({ screenshots: true, snapshots: true });
  const errors = [],
    unexpected = [],
    scientificRequests = [],
    capabilityRequests = [];
  context.on("page", (page) =>
    page.on("pageerror", (error) => errors.push(error.message)),
  );
  context.on("request", (request) => {
    if (["xhr", "fetch", "websocket"].includes(request.resourceType())) {
      const target = new URL(request.url());
      if (
        request.method() === "GET" &&
        target.pathname === "/api/experiments" &&
        !target.search
      )
        capabilityRequests.push(request.url());
      else scientificRequests.push(request.url());
    }
  });
  await context.route("**/*", async (route) => {
    const target = route.request().url();
    if (
      /^https?:/.test(target) &&
      (!process.env.HUB_URL || new URL(target).origin !== new URL(base).origin)
    ) {
      unexpected.push(target);
      return route.abort();
    }
    return route.continue();
  });
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(7000);
    const catalogue = JSON.parse(
      fs.readFileSync(path.join(root, "site/catalog.json"), "utf8"),
    );
    const primary = [
      ["Home", "index.html"],
      ["Problems", "problems.html"],
      ["Sources", "sources.html"],
      ["Execution lab", "lab.html"],
    ];
    const rootPages = [
      "index.html",
      "problems.html",
      "sources.html",
      "explorations.html",
      "validation.html",
      "lab.html",
    ];
    const nav = () => page.getByRole("navigation", { name: "Main navigation" });
    await page.goto(url("index.html"));
    for (const [name, file] of primary) {
      await nav().getByRole("link", { name, exact: true }).click();
      assert.equal(new URL(page.url()).pathname.endsWith("/" + file), true);
      assert.equal(
        await page.locator('nav [aria-current="page"]').textContent(),
        name,
      );
      assert.equal(await nav().getByRole("link").count(), primary.length);
    }
    await page.goto(url("problems.html"));
    assert.equal(
      await page.locator("#problemList .problem-row").count(),
      catalogue.problems.length,
    );
    await page
      .getByLabel("Search problems, evidence or tools")
      .fill("provenance");
    await page
      .getByLabel("Domain", { exact: true })
      .selectOption("Behavioural neuroscience");
    await page
      .getByLabel("Work state", { exact: true })
      .selectOption("Local patch verified");
    assert.equal(
      await page.locator("#problemList .problem-row:visible").count(),
      1,
    );
    await page
      .getByLabel("Search problems, evidence or tools")
      .fill("nothing-matches-7cf5");
    assert.equal(await page.locator("#empty").isVisible(), true);
    await page
      .getByRole("button", { name: "Clear filters", exact: true })
      .click();
    assert.equal(
      await page.locator("#problemList .problem-row:visible").count(),
      catalogue.problems.length,
    );
    await page.locator("#problem-pairwise-overlap").click();
    await page.waitForURL(url("problems/pairwise-overlap.html"));
    assert.equal(
      await page.locator("h1").textContent(),
      "Inspect why overlapping poses are removed",
    );
    assert.match(
      await page.locator("#solution").textContent(),
      /unchanged filter/,
    );
    assert.match(
      await page.locator("#try").textContent(),
      /selects those saved results/,
    );
    await nav().getByRole("link", { name: "Home", exact: true }).click();
    assert.equal(new URL(page.url()).pathname.endsWith("/index.html"), true);
    // Old problem fragments keep working, with one canonical destination each.
    for (const problem of catalogue.problems) {
      await page.goto(url("problems.html#problem-" + problem.id));
      await page.waitForURL(url(problem.href), { waitUntil: "load" });
      assert.equal(await page.locator("h1").count(), 1);
      assert.equal(await page.locator("script").count(), 0);
      assert.equal(await nav().getByRole("link").count(), primary.length);
      assert.equal(
        await page.locator('nav [aria-current="page"]').textContent(),
        "Problems",
      );
      assert.ok(await page.locator("#people").isVisible());
      assert.ok(await page.locator("#evidence").isVisible());
      assert.ok(await page.locator("#solution").isVisible());
      assert.ok(await page.locator("#validation").isVisible());
      if (problem.page) {
        assert.ok(await page.locator("#before-after").isVisible());
        assert.equal(
          await page.locator("#try .execution-kind").textContent(),
          problem.page.execution.label,
        );
        assert.ok((await page.locator("#records a").count()) >= 3);
      } else {
        assert.match(await page.locator("#try").textContent(), /Research only/);
        assert.equal(
          await page
            .getByRole("link", { name: "View verified run", exact: true })
            .count(),
          0,
        );
      }
    }
    await page.goto(url("sources.html"));
    assert.equal(
      await page.locator("#sourceList article").count(),
      catalogue.boards.length,
    );
    const board = page.locator("#sourceList article").filter({
      has: page.getByRole("heading", {
        name: "SLEAP issues and discussions",
        exact: true,
      }),
    });
    const delayedApp = async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 800));
      await route.fallback();
    };
    await page.route("**/site/app.js", delayedApp);
    await Promise.all([
      page.waitForURL(url("problems.html?source=sleap"), { waitUntil: "load" }),
      board.getByRole("button", { name: "Show related problems" }).click(),
    ]);
    await page.unroute("**/site/app.js", delayedApp);
    assert.equal(await page.locator("#sourceFilter").inputValue(), "sleap");
    assert.ok(await page.locator("#problem-pairwise-overlap").isVisible());
    await page.goto(url("explorations.html"));
    assert.equal(
      await page.locator("#explorationList article").count(),
      catalogue.demonstrations.length,
    );
    const entries = await page
      .locator("#explorationList h2 a")
      .evaluateAll((nodes) => nodes.map((node) => node.href));
    for (const entry of entries) {
      await page.goto(entry);
      assert.ok(await page.locator("#solution").isVisible());
    }
    await page.goto(url("explorations.html#demo-movement"));
    await page.waitForURL(url("problems/edit-filtering.html#try"), {
      waitUntil: "load",
    });
    await page.goto(url("validation.html"));
    assert.equal(
      await page.locator("#validationList article").count(),
      catalogue.validation.length,
    );
    await page.goto(url("validation.html#zeroAgeWorkflowComparison"));
    await page.waitForURL(url("problems/zero-age-metadata.html#before-after"), {
      waitUntil: "load",
    });
    const exportResult = JSON.parse(
      fs.readFileSync(
        path.join(root, "projects/refinebio-zero-age/postgres-patched.json"),
        "utf8",
      ),
    );
    if (exportResult.worker_export) {
      assert.deepEqual(
        await page
          .locator("#zeroAgeWorkflowComparison tbody tr")
          .evaluateAll((rows) =>
            rows.map((row) =>
              Array.from(row.cells, (cell) => cell.textContent.trim()),
            ),
          ),
        [
          ["0", "(empty)", "0.000"],
          ["0.0", "(empty)", "0.000"],
          ["2", "2.000", "2.000"],
          ["(empty)", "(empty)", "(empty)"],
          ["unknown", "(empty)", "(empty)"],
        ],
      );
    } else {
      assert.equal(await page.locator("#zeroAgeWorkflowComparison").count(), 0);
      assert.match(
        await page.locator("#zeroAgeWorkflowStatus").innerText(),
        /has not executed/,
      );
    }
    await page.goto(url("problems/edit-filtering.html"));
    assert.match(
      await page.locator("#before-after").textContent(),
      /existing default can instead keep all missing-score/,
    );
    assert.match(
      await page.locator("#validation").textContent(),
      /not the whole dedicated-array/,
    );
    await page.goto(url("problems/pairwise-overlap.html"));
    const [demo] = await Promise.all([
      context.waitForEvent("page"),
      page
        .getByRole("link", { name: "Open browser demo", exact: true })
        .click(),
    ]);
    await demo.waitForLoadState();
    assert.match(
      await demo.locator("header").textContent(),
      /Python does not run/,
    );
    await demo.locator("#scenario").selectOption("flipped");
    await demo
      .getByRole("button", { name: "Keypoint OKS", exact: true })
      .click();
    assert.match(
      await demo.locator("#resultSummary").textContent(),
      /2 retained/,
    );
    assert.match(
      await demo.locator("#baselineResult").textContent(),
      /A: retained/,
    );
    assert.equal(
      await demo.locator("#inspectionComparison").textContent(),
      await demo.locator("#explanation").textContent(),
    );
    for (const [name, destination] of [
      ...primary,
      ["About this problem", "problems/pairwise-overlap.html"],
    ]) {
      await Promise.all([
        demo.waitForURL(url(destination), { waitUntil: "load" }),
        demo
          .getByRole("navigation", { name: "Lab navigation" })
          .getByRole("link", { name, exact: true })
          .click(),
      ]);
      assert.ok(await demo.locator("h1").isVisible());
      await demo.goto(url("projects/overlap-inspector/index.html"));
    }
    await demo.close();
    assert.equal(
      new URL(page.url()).pathname.endsWith("/problems/pairwise-overlap.html"),
      true,
    );
    await page.goto(url("index.html"));
    await page.screenshot({ path: path.join(output, "desktop.png") });
    const problemFiles = catalogue.problems.map((problem) => problem.href);
    for (const id of [
      "pairwise-overlap",
      "edit-filtering",
      "deleted-flags",
      "nwb-stream-integrity",
      "eeg-events",
      "zero-age-metadata",
    ]) {
      await page.goto(url("problems/" + id + ".html"));
      if (id === "deleted-flags") {
        const row = page
          .getByRole("row")
          .filter({ hasText: "Qt deletion: second Save after reopening" });
        assert.deepEqual(await row.locator("td").allTextContents(), [
          "Qt deletion: second Save after reopening",
          "No edit variable",
          "true",
        ]);
        const loaded = page
          .getByRole("row")
          .filter({ hasText: "Qt deletion: flag in final loader" });
        assert.deepEqual(await loaded.locator("td").allTextContents(), [
          "Qt deletion: flag in final loader",
          "false",
          "true",
        ]);
      }
      await page.screenshot({ path: path.join(output, id + "-desktop.png") });
      await page
        .locator("#before-after")
        .screenshot({ path: path.join(output, id + "-comparison.png") });
    }
    await page.setViewportSize({ width: 390, height: 844 });
    for (const file of [...rootPages, ...problemFiles]) {
      await page.goto(url(file));
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        false,
        file,
      );
    }
    await page.goto(url("problems/zero-age-metadata.html"));
    await page.screenshot({
      path: path.join(output, "mobile-problem.png"),
      fullPage: false,
    });
    await page.locator("#before-after").scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(output, "mobile-comparison.png") });
    const recordFiles = fs
      .readdirSync(path.join(root, "site/records"))
      .filter((file) => file.endsWith(".html"));
    let localLinks = 0;
    for (const file of [
      ...rootPages,
      ...problemFiles,
      ...recordFiles.map((file) => "site/records/" + file),
    ]) {
      await page.goto(url(file));
      assert.equal(
        await page
          .getByRole("navigation", { name: "Main navigation" })
          .getByRole("link")
          .count(),
        primary.length,
      );
      const links = await page
        .locator("a[href]")
        .evaluateAll((nodes) => nodes.map((node) => node.href));
      for (const href of links) {
        const target = new URL(href);
        if (
          target.protocol === "file:" ||
          (target.origin === new URL(base).origin &&
            target.protocol !== "file:")
        ) {
          target.hash = "";
          target.search = "";
          if (/^\/api\/auth\/(signin|signout)$/.test(target.pathname)) {
            assert.equal(
              file,
              "lab.html",
              "Only the lab should link to runtime sign-in",
            );
            continue;
          }
          const local =
            target.protocol === "file:"
              ? fileURLToPath(target)
              : path.join(root, decodeURIComponent(target.pathname));
          assert.equal(
            fs.existsSync(local),
            true,
            `Missing local target linked from ${file}: ${target.pathname}`,
          );
          localLinks++;
        }
      }
    }
    // The catalogue and problem explanations remain readable without JavaScript.
    const noJs = await browser.newContext({
      javaScriptEnabled: false,
      extraHTTPHeaders: headers,
    });
    try {
      const reader = await noJs.newPage();
      await reader.goto(url("problems.html"));
      assert.equal(
        await reader.locator("#problemList a").count(),
        catalogue.problems.length,
      );
      await reader.locator("#problem-pairwise-overlap").click();
      assert.ok(await reader.locator("#solution").isVisible());
    } finally {
      await noJs.close();
    }
    if (process.env.HUB_URL) {
      const response = await context.request.get(url("build-info.json"));
      assert.equal(response.ok(), true);
      assert.deepEqual(
        await response.json(),
        JSON.parse(fs.readFileSync(path.join(root, "build-info.json"), "utf8")),
        "Deployed artifact must match the tested package",
      );
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(unexpected, []);
    assert.deepEqual(scientificRequests, []);
    const report = {
      artifactManifestSha256: crypto
        .createHash("sha256")
        .update(fs.readFileSync(path.join(root, "build-info.json")))
        .digest("hex"),
      browser: await browser.version(),
      node: process.versions.node,
      playwright: require("playwright/package.json").version,
      mode: process.env.HUB_URL ? "deployed" : "offline-package",
      pages: rootPages.length,
      problemPages: problemFiles.length,
      problems: catalogue.problems.length,
      sourceBoards: catalogue.boards.length,
      explorations: entries.length,
      demonstrations: catalogue.demonstrations.length,
      researchPages: recordFiles.length,
      localLinks,
      viewports: ["1440x1100", "390x844"],
      pageErrors: errors,
      externalRequests: 0,
      backgroundExecutionRequests: 0,
      readOnlyCapabilityRequests: capabilityRequests.length,
      deployedArtifactIdentityChecked: Boolean(process.env.HUB_URL),
      checks: [
        "four primary navigation destinations",
        "all canonical problem pages and legacy fragments",
        "compound filters/reset/empty state",
        "source-board query navigation with delayed script",
        "six complete solution narratives and explicit runtime labels",
        "research candidates claim no implemented solution",
        "actual before/after export values",
        "separate interactive pose demo and contextual return links",
        "unchanged filter output and explanation",
        "all mobile problem pages without overflow",
        "local targets and research-record navigation",
        "static pages readable without JavaScript",
        "no background scientific execution requests",
        "artifact identity on deployed mode",
      ],
    };
    fs.writeFileSync(
      path.join(output, "results.json"),
      JSON.stringify(report, null, 2) + "\n",
    );
    console.log(JSON.stringify(report, null, 2));
  } catch (error) {
    fs.writeFileSync(path.join(output, "failure.txt"), String(error) + "\n");
    throw error;
  } finally {
    if (!process.env.HUB_URL)
      await context.tracing.stop({ path: path.join(output, "trace.zip") });
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
