// Verifies the packaged artifact locally or at an authenticated deployment URL.
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
const url = (p) => new URL(p, base).href;
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
    unexpected = [];
  try {
    const page = await context.newPage();
    page.setDefaultTimeout(7000);
    context.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
    page.on("pageerror", (e) => errors.push(e.message));
    await context.route("**/*", async (route) => {
      const u = route.request().url();
      if (
        /^https?:/.test(u) &&
        (!process.env.HUB_URL || new URL(u).origin !== new URL(base).origin)
      ) {
        unexpected.push(u);
        return route.abort();
      }
      return route.continue();
    });
    await page.goto(url("index.html"));
    const catalogue = JSON.parse(
      fs.readFileSync(path.join(root, "site/catalog.json"), "utf8"),
    );
    const pages = [
      ["Home", "index.html"],
      ["Explorations", "explorations.html"],
      ["Problems", "problems.html"],
      ["Sources", "sources.html"],
      ["Validation", "validation.html"],
    ];
    for (const [name, file] of pages) {
      await page
        .getByRole("navigation", { name: "Main navigation" })
        .getByRole("link", { name, exact: true })
        .click();
      assert.equal(new URL(page.url()).pathname.endsWith("/" + file), true);
      assert.equal(
        await page.locator('nav [aria-current="page"]').textContent(),
        name,
      );
      assert.equal(await page.locator("h1").count(), 1);
    }
    await page.goto(url("problems.html"));
    assert.equal(
      await page.locator("#problemList details").count(),
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
    assert.equal(await page.locator("#problemList details:visible").count(), 1);
    await page
      .getByLabel("Search problems, evidence or tools")
      .fill("nothing-matches-7cf5");
    assert.equal(await page.locator("#empty").isVisible(), true);
    await page
      .getByRole("button", { name: "Clear filters", exact: true })
      .click();
    assert.equal(
      await page.locator("#problemList details:visible").count(),
      catalogue.problems.length,
    );
    await page.goto(url("problems.html#problem-pairwise-overlap"));
    assert.equal(
      await page.locator("#problem-pairwise-overlap").getAttribute("open"),
      "",
    );
    assert.match(
      await page.locator("#problem-pairwise-overlap .body").textContent(),
      /one source family/i,
    );
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
    // The select exists in the HTML before app.js applies the query. Exercise a
    // slow script load so a navigation-commit-only assertion cannot pass by luck.
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
    assert.equal(new URL(page.url()).pathname.endsWith("/problems.html"), true);
    assert.equal(await page.locator("#sourceFilter").inputValue(), "sleap");
    assert.ok(await page.locator("#problem-pairwise-overlap").isVisible());
    await page.goto(url("explorations.html"));
    assert.equal(
      await page.locator("#explorationList article").count(),
      catalogue.explorations.length,
    );
    assert.equal(
      await page.locator("#demoList article").count(),
      catalogue.demonstrations.length,
    );
    const entries = await page
      .locator("#explorationList h3 a")
      .evaluateAll((ns) => ns.map((n) => n.href));
    for (const entry of entries) {
      await page.goto(entry);
      assert.ok(await page.locator("h1").first().isVisible());
    }
    await page.goto(url("explorations.html"));
    const [demo] = await Promise.all([
      context.waitForEvent("page"),
      page
        .getByRole("link", { name: "Open interactive demo", exact: true })
        .click(),
    ]);
    await demo.waitForLoadState();
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
      ["Home", "index.html"],
      ["Explorations", "explorations.html"],
      ["Problems", "problems.html"],
      ["Sources", "sources.html"],
      ["Validation", "validation.html"],
    ]) {
      await Promise.all([
        demo.waitForURL(url(destination), { waitUntil: "load" }),
        demo
          .getByRole("navigation", { name: "Lab navigation" })
          .getByRole("link", { name, exact: true })
          .click(),
      ]);
      assert.ok(await demo.locator("h1").first().isVisible());
      await demo.goto(url("projects/overlap-inspector/index.html"));
    }
    await demo.close();
    assert.equal(
      new URL(page.url()).pathname.endsWith("/explorations.html"),
      true,
    );
    await Promise.all([
      page.waitForURL(url("problems.html#problem-pairwise-overlap"), {
        waitUntil: "load",
      }),
      page
        .getByRole("link", { name: "Problem and evidence", exact: true })
        .first()
        .click(),
    ]);
    assert.equal(new URL(page.url()).pathname.endsWith("/problems.html"), true);
    assert.equal(
      await page.locator("#problem-pairwise-overlap").getAttribute("open"),
      "",
    );
    await page.goto(url("validation.html"));
    assert.match(
      await page.locator("#validationList").textContent(),
      /not the whole dedicated-array/,
    );
    assert.equal(await page.locator(".validation-levels").isVisible(), true);
    await page.goto(url("index.html"));
    await page.screenshot({ path: path.join(output, "desktop.png") });
    await page.goto(url("explorations.html"));
    await page.screenshot({
      path: path.join(output, "demonstrations.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    for (const [, file] of pages) {
      await page.goto(url(file));
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        false,
        file,
      );
    }
    await page.goto(url("problems.html#problem-label-free"));
    await page.screenshot({ path: path.join(output, "mobile-problem.png") });
    const recordFiles = fs
      .readdirSync(path.join(root, "site/records"))
      .filter((f) => f.endsWith(".html"));
    const files = [
      ...pages.map(([, f]) => f),
      ...recordFiles.map((f) => "site/records/" + f),
    ];
    let localLinks = 0;
    for (const file of files) {
      await page.goto(url(file));
      const links = await page
        .locator("a[href]")
        .evaluateAll((ns) => ns.map((n) => n.href));
      for (const href of links) {
        const u = new URL(href);
        if (
          u.protocol === "file:" ||
          (u.origin === new URL(base).origin && u.protocol !== "file:")
        ) {
          u.hash = "";
          u.search = "";
          const target =
            u.protocol === "file:"
              ? fileURLToPath(u)
              : path.join(root, decodeURIComponent(u.pathname));
          assert.equal(
            fs.existsSync(target),
            true,
            `Missing local target linked from ${file}`,
          );
          localLinks++;
        }
      }
    }
    if (process.env.HUB_URL) {
      const response = await context.request.get(url("build-info.json"));
      assert.equal(response.ok(), true);
      const remote = await response.json();
      const local = JSON.parse(
        fs.readFileSync(path.join(root, "build-info.json"), "utf8"),
      );
      assert.deepEqual(
        remote,
        local,
        "Deployed artifact must match the tested package",
      );
    }
    assert.deepEqual(errors, []);
    assert.deepEqual(unexpected, []);
    const report = {
      artifactManifestSha256: crypto
        .createHash("sha256")
        .update(fs.readFileSync(path.join(root, "build-info.json")))
        .digest("hex"),
      browser: await browser.version(),
      node: process.versions.node,
      playwright: require("playwright/package.json").version,
      mode: process.env.HUB_URL ? "deployed" : "offline-package",
      pages: pages.length,
      problems: catalogue.problems.length,
      sourceBoards: catalogue.boards.length,
      explorations: entries.length,
      demonstrations: catalogue.demonstrations.length,
      researchPages: recordFiles.length,
      localLinks,
      viewports: ["1440x1100", "390x844"],
      pageErrors: errors,
      externalRequests: 0,
      deployedArtifactIdentityChecked: Boolean(process.env.HUB_URL),
      checks: [
        "distinct page URLs and current navigation",
        "compound filters/reset/empty state",
        "cross-page problem deep links",
        "source-board query navigation",
        "all exploration targets",
        "separate interactive demo tab",
        "demo navigation back to all five lab pages",
        "unchanged filter output and inspector explanation",
        "validation levels and limits",
        "all mobile pages without overflow",
        "local document links",
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
