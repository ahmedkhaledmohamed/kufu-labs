// Constructed-data observations in published JupyterLab, not an assistive-technology assessment.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const base = new URL(process.env.JUPYTER_URL || "http://127.0.0.1:8897/lab");
  assert.equal(
    base.hostname,
    "127.0.0.1",
    "Use the isolated localhost fixture server",
  );
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME_PATH
      ? { executablePath: process.env.CHROME_PATH }
      : {}),
  });
  try {
    const context = await browser.newContext({
      viewport: { width: 1400, height: 1000 },
    });
    await context.route("**/*", (route) =>
      new URL(route.request().url()).origin === base.origin
        ? route.continue()
        : route.abort(),
    );
    const page = await context.newPage();
    await page.goto(base.href);
    await page.waitForFunction(() => window.jupyterapp?.restored);
    await page.evaluate(() => window.jupyterapp.restored);
    assert.equal(await page.evaluate(() => window.jupyterapp.version), "4.6.4");
    const item = page
      .locator(".jp-DirListing-item")
      .filter({ hasText: "alpha.txt" });
    await item.waitFor();
    const selected = () =>
      item.evaluate((node) => node.classList.contains("jp-mod-selected"));
    await item.click();
    assert.equal(await selected(), true);
    await page.keyboard.press("Space");
    const afterSpace = await selected();
    await page.keyboard.press("Control+Space");
    const afterControlSpace = await selected();
    assert.equal(afterSpace, true);
    assert.equal(afterControlSpace, false);

    await page.evaluate(() => {
      void window.jupyterapp.commands.execute("console:create", {
        kernelPreference: { shouldStart: false, canStart: false },
      });
    });
    await page.locator(".jp-CodeConsole").first().waitFor();
    await page
      .getByRole("button", { name: "Change Console Prompt Position" })
      .click();
    const capture = () =>
      page.evaluate(() => ({
        menuVisible: [...document.querySelectorAll(".lm-Menu")].some(
          (n) => n.getBoundingClientRect().height > 0,
        ),
        menuFocused: [...document.querySelectorAll(".lm-Menu")].some((n) =>
          n.contains(document.activeElement),
        ),
        activeMenuItems: document.querySelectorAll(
          ".lm-Menu-item.lm-mod-active",
        ).length,
      }));
    const beforeArrow = await capture();
    await page.keyboard.press("ArrowDown");
    const afterArrow = await capture();
    assert.equal(beforeArrow.menuVisible, true);
    assert.equal(afterArrow.menuVisible, true);
    assert.equal(afterArrow.menuFocused, false);
    assert.equal(afterArrow.activeMenuItems, 0);
    const report = {
      jupyterlab: "4.6.4",
      releaseCommit: "384bff3af6598b3a6348df58fe34450914b49c41",
      browser: browser.version(),
      fixture:
        "Empty text files and a console without a kernel; no real notebooks or recordings",
      fileBrowser: {
        afterSpaceSelected: afterSpace,
        afterControlSpaceSelected: afterControlSpace,
      },
      toolbarMenu: { beforeArrow, afterArrow },
      limits: "No screen reader, Firefox or patched upstream frontend tested",
    };
    fs.writeFileSync(
      process.env.JUPYTER_REPORT || "/tmp/kufu-jupyter-accessibility.json",
      JSON.stringify(report, null, 2) + "\n",
    );
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
