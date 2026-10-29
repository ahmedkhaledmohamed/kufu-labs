const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const { summarize } = require("./contracts.cjs");
const root = path.resolve(__dirname, "../dist");
const output = path.resolve(__dirname, "../.runs/lab/browser");
const reports = ["baseline", "patched"].map(
  (mode) => `.runs/contracts/nwb/parameterized-${mode}/report.json`,
);
const fixture = reports.every((file) => fs.existsSync(file))
  ? {
      comparisons: summarize(
        ...reports.map((file) => JSON.parse(fs.readFileSync(file))),
      ),
    }
  : JSON.parse(fs.readFileSync(".runs/lab/vercel-result.json"));
const server = http.createServer((req, res) => {
  const file = path.join(root, new URL(req.url, "http://localhost").pathname);
  if (
    !file.startsWith(root + path.sep) ||
    !fs.existsSync(file) ||
    !fs.statSync(file).isFile()
  ) {
    res.statusCode = 404;
    return res.end();
  }
  res.setHeader(
    "Content-Type",
    file.endsWith(".js")
      ? "text/javascript"
      : file.endsWith(".css")
        ? "text/css"
        : "text/html",
  );
  res.end(fs.readFileSync(file));
});
(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME_PATH
      ? { executablePath: process.env.CHROME_PATH }
      : {}),
  });
  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1100 },
    });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    let submissions = 0;
    let submitted;
    let available = true;
    let failSubmitOnce = false;
    await page.route("**/api/experiments**", async (route) => {
      const req = route.request();
      if (req.method() === "POST") {
        submissions++;
        submitted = req.postDataJSON();
        if (failSubmitOnce) {
          failSubmitOnce = false;
          return route.abort();
        }
        return route.fulfill({
          json: { id: submitted.id, status: "queued" },
          status: 202,
        });
      }
      const id = new URL(req.url()).searchParams.get("id");
      return route.fulfill({
        json: id
          ? { id, status: "completed", ...fixture }
          : { enabled: available },
      });
    });
    await page.goto(base + "/lab.html");
    await page
      .getByRole("button", { name: "Run on Vercel", exact: true })
      .waitFor();
    await page.waitForFunction(
      () => !document.querySelector("#runExperiment").disabled,
    );
    assert.equal(
      submissions,
      0,
      "Opening or reading the page must not submit a job",
    );
    await page.getByLabel(/Experiment set/).selectOption("boundary");
    await page.getByRole("button", { name: "Generate input plan" }).click();
    const planned = JSON.parse(await page.locator("#inputPlan").textContent());
    assert.deepEqual(
      planned.map((c) => c.rows),
      [99, 100, 101, 301],
    );
    assert.equal(
      submissions,
      0,
      "Input generation must not launch hosted compute",
    );
    await page
      .getByRole("button", { name: "Run on Vercel", exact: true })
      .click();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
    );
    assert.deepEqual(submitted.cases, planned);
    assert.equal(
      await page.locator("#runResults table").count(),
      fixture.comparisons.length,
    );
    assert.equal(
      await page
        .locator("#runResults table")
        .first()
        .locator("tbody tr")
        .count(),
      4,
    );
    assert.equal(await page.locator("#downloadRun").isVisible(), true);
    assert.ok(
      (await page.locator("#downloadRun").getAttribute("href")).includes(
        "download=1",
      ),
    );
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
    );
    assert.equal(
      submissions,
      1,
      "Reload must read the same run, never resubmit it",
    );
    await page.getByLabel("Rows", { exact: true }).fill("2001");
    await page
      .getByRole("button", { name: "Run on Vercel", exact: true })
      .click();
    assert.equal(submissions, 1, "Invalid inputs must not submit a run");
    await page.getByLabel("Rows", { exact: true }).fill("500");
    failSubmitOnce = true;
    await page
      .getByRole("button", { name: "Run on Vercel", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Retry submission", exact: true })
      .waitFor();
    const uncertainId = submitted.id;
    await page
      .getByRole("button", { name: "Retry submission", exact: true })
      .click();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
    );
    assert.equal(
      submitted.id,
      uncertainId,
      "An uncertain network response must retry the same submission ID",
    );
    assert.equal(submissions, 3);
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    fs.mkdirSync(output, { recursive: true });
    await page.screenshot({
      path: path.join(output, "mobile.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 1100 });
    await page.screenshot({
      path: path.join(output, "desktop.png"),
      fullPage: true,
    });
    available = false;
    await page.goto(base + "/lab.html");
    await page.waitForFunction(() =>
      document
        .querySelector("#labAvailability")
        .textContent.includes("not enabled"),
    );
    assert.equal(await page.locator("#runExperiment").isDisabled(), true);
    assert.deepEqual(errors, []);
    console.log(
      "Lab browser flow passed: generated inputs, explicit submission, actual-report rendering, bookmarked results, downloads, invalid inputs, unavailable backend and mobile layout. Queue/API responses were local test doubles; this check launched no hosted compute.",
    );
  } finally {
    await browser.close();
  }
})()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => server.close());
