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
const mneReports = ["baseline", "patched"].map((mode) =>
  JSON.parse(
    fs.readFileSync(`.runs/contracts/mne/parameterized-${mode}/report.json`),
  ),
);
const mneFixture = {
  recipe: "mne",
  comparisons: summarize(...mneReports, "mne"),
};
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
    let identity = {
      sign_in_available: true,
      signed_in: false,
      owner_override: false,
    };
    let failSubmitOnce = false;
    let jobState = "queued";
    const created = new Date(Date.now() - 20000).toISOString();
    const started = new Date(Date.now() - 15000).toISOString();
    const phaseStarted = new Date(Date.now() - 5000).toISOString();
    const completed = new Date().toISOString();
    function progressFixture() {
      const events = [
        {
          label: "Waiting for a worker",
          started_at: created,
          outcome: jobState === "queued" ? "active" : "completed",
          ...(jobState !== "queued" ? { finished_at: started } : {}),
        },
      ];
      if (jobState !== "queued") {
        events.push({
          label: "Starting isolated Python runtime",
          started_at: started,
          finished_at: phaseStarted,
          outcome: "completed",
        });
        events.push({
          label: "Installing pinned dependencies",
          started_at: phaseStarted,
          outcome:
            jobState === "completed"
              ? "completed"
              : jobState === "failed"
                ? "failed"
                : "active",
          ...(["completed", "failed"].includes(jobState)
            ? { finished_at: completed }
            : {}),
        });
      }
      return {
        created_at: created,
        started_at: jobState === "queued" ? null : started,
        updated_at: jobState === "queued" ? created : phaseStarted,
        ...(["completed", "failed"].includes(jobState)
          ? { finished_at: completed }
          : {}),
        events,
      };
    }
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
      if (id && jobState === "unavailable")
        return route.fulfill({
          status: 503,
          json: { error: "Status service unavailable." },
        });
      return route.fulfill({
        json: id
          ? {
              id,
              status: jobState,
              recipe: submitted?.recipe || "nwb",
              cases: submitted?.cases,
              ...(jobState === "completed"
                ? submitted?.recipe === "mne"
                  ? mneFixture
                  : fixture
                : {}),
              progress: progressFixture(),
            }
          : { enabled: available, recipes: ["nwb", "mne"], access: identity },
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
      document.querySelector("#runStatus").textContent.includes("queued"),
    );
    assert.equal(
      await page.locator("#runTimeline .phase-state").last().textContent(),
      "Waiting",
    );
    jobState = "running";
    await page.waitForFunction(
      () =>
        document.querySelector("#progressSummary").textContent ===
        "Installing pinned dependencies",
    );
    assert.equal(
      await page
        .locator('#runTimeline [aria-current="step"]')
        .textContent()
        .then((text) => text.includes("Installing pinned dependencies")),
      true,
    );
    assert.equal(await page.locator("#runResults table").count(), 0);
    const beforeTick = await page.locator("#runElapsed").textContent();
    await page.waitForFunction(
      (before) => document.querySelector("#runElapsed").textContent !== before,
      beforeTick,
    );
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    fs.mkdirSync(output, { recursive: true });
    await page
      .locator("#runProgress")
      .screenshot({ path: path.join(output, "progress-running-mobile.png") });
    await page.setViewportSize({ width: 1440, height: 1100 });
    await page
      .locator("#runProgress")
      .screenshot({ path: path.join(output, "progress-running-desktop.png") });
    jobState = "completed";
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
    );
    assert.equal(
      await page.locator("#runTimeline .phase-completed").count(),
      3,
    );
    assert.equal(await page.locator("#runTimeline [aria-current]").count(), 0);
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
    assert.equal(
      await page.locator("#runTimeline .phase-completed").count(),
      3,
      "Reload must retain recorded stages",
    );
    jobState = "running";
    await page.reload();
    await page.waitForFunction(
      () =>
        document.querySelector("#progressSummary").textContent ===
        "Installing pinned dependencies",
    );
    jobState = "unavailable";
    await page.waitForFunction(() =>
      document
        .querySelector("#progressSummary")
        .textContent.includes("Status unavailable"),
    );
    assert.equal(await page.locator("#runTimeline [aria-current]").count(), 0);
    assert.equal(
      await page.locator("#runTimeline .phase-state").last().textContent(),
      "Last reported running",
    );
    jobState = "failed";
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("failed"),
    );
    assert.equal(await page.locator("#runTimeline .phase-failed").count(), 1);
    assert.equal(await page.locator("#runResults table").count(), 0);
    jobState = "interrupted";
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("interrupted"),
    );
    assert.equal(
      await page.locator("#runTimeline .phase-interrupted").count(),
      1,
    );
    jobState = "completed";
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
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
    const beforeMne = submissions;
    jobState = "queued";
    await page.goto(base + "/lab.html?recipe=mne");
    await page.waitForFunction(
      () => !document.querySelector("#runExperiment").disabled,
    );
    assert.equal(await page.locator("#experimentRecipe").inputValue(), "mne");
    assert.equal(await page.locator("#nwbInputs").isVisible(), false);
    await page
      .getByLabel("Annotation time origin", { exact: true })
      .selectOption("utc");
    await page
      .getByLabel("MNE experiment set", { exact: true })
      .selectOption("reference");
    await page.getByRole("button", { name: "Generate input plan" }).click();
    const mnePlan = JSON.parse(await page.locator("#inputPlan").textContent());
    assert.deepEqual(
      mnePlan,
      mneReports[0].cases.map((value) => value.input),
    );
    assert.equal(
      submissions,
      beforeMne,
      "Recipe selection and planning must not submit compute",
    );
    await page
      .getByRole("button", { name: "Run on Vercel", exact: true })
      .click();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("queued"),
    );
    assert.equal(submitted.recipe, "mne");
    assert.deepEqual(submitted.cases, mnePlan);
    assert.equal(await page.locator("#experimentRecipe").isDisabled(), true);
    jobState = "completed";
    await page.waitForFunction(
      () =>
        document.querySelector("#runResults table")?.querySelector("tbody")
          .children.length === 3,
    );
    assert.equal(await page.locator("#runResults table").count(), 4);
    assert.match(
      await page.locator("#runResults").textContent(),
      /Rounded lookup is an existing workaround/,
    );
    assert.equal(await page.locator("#downloadRun").isVisible(), true);
    await page.reload();
    await page.waitForFunction(() =>
      document.querySelector("#runStatus").textContent.includes("completed"),
    );
    assert.equal(submissions, beforeMne + 1, "Reloading MNE must not resubmit");
    assert.equal(await page.locator("#experimentRecipe").inputValue(), "mne");
    assert.equal(await page.locator('[name="origin"]').inputValue(), "utc");
    assert.deepEqual(
      JSON.parse(await page.locator("#inputPlan").textContent()),
      mnePlan,
    );
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    await page.screenshot({
      path: path.join(output, "mne-mobile.png"),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 1100 });
    await page.screenshot({
      path: path.join(output, "mne-desktop.png"),
      fullPage: true,
    });
    const beforeAccountChanges = submissions;
    assert.match(
      await page.locator("#accountAction").textContent(),
      /Sign in with Vercel/,
    );
    assert.match(
      await page.locator("#accountAction").getAttribute("href"),
      /^\/api\/auth\/signin\?/,
    );
    identity = {
      sign_in_available: true,
      signed_in: true,
      owner_override: true,
    };
    await page.goto(base + "/lab.html?recipe=mne");
    await page.waitForFunction(() =>
      document
        .querySelector("#accountStatus")
        .textContent.includes("Daily submission cap waived"),
    );
    assert.match(
      await page.locator("#experimentLimits").textContent(),
      /exempt from the daily submission cap/,
    );
    assert.match(
      await page.locator("#accountAction").textContent(),
      /Sign out/,
    );
    await page.screenshot({
      path: path.join(output, "owner-account.png"),
      fullPage: true,
    });
    identity = {
      sign_in_available: true,
      signed_in: true,
      owner_override: false,
    };
    await page.reload();
    await page.waitForFunction(() =>
      document
        .querySelector("#accountStatus")
        .textContent.includes("standard daily submission limit"),
    );
    assert.match(
      await page.locator("#experimentLimits").textContent(),
      /10 submissions per UTC day/,
    );
    assert.equal(
      submissions,
      beforeAccountChanges,
      "Reading account state cannot submit compute",
    );
    identity = {
      sign_in_available: false,
      signed_in: false,
      owner_override: false,
    };
    available = false;
    await page.goto(base + "/lab.html");
    await page.waitForFunction(() =>
      document
        .querySelector("#labAvailability")
        .textContent.includes("not enabled"),
    );
    assert.equal(await page.locator("#runExperiment").isDisabled(), true);
    assert.equal(await page.locator("#accountAction").isVisible(), false);
    assert.deepEqual(errors, []);
    console.log(
      "Lab browser flow passed: live queued/running stages and elapsed time, reload persistence, failed/interrupted stages, stale-status handling, generated inputs, explicit submission, actual-report rendering, downloads and mobile layout. Queue/API responses were local test doubles; this check launched no hosted compute.",
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
