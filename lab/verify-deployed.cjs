// Runs only after an approved PR has produced a protected Vercel deployment.
// Both scientific recipes execute on Vercel, including when CI invokes this check.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { DEFAULT, MNE_DEFAULT } = require("./contracts.cjs");
const deployment = process.env.HUB_URL;
const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
const manifest = require("../dist/build-info.json");
async function request(suffix = "", options = {}) {
  const response = await fetch(`${deployment}/api/experiments${suffix}`, {
    ...options,
    headers: { "x-vercel-protection-bypass": secret, ...options.headers },
    signal: AbortSignal.timeout(30000),
  });
  assert.ok(response.ok, `Execution API returned ${response.status}`);
  return response;
}
async function verifyRecipe(recipe, cases) {
  const id = crypto.randomUUID();
  await request("", {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: deployment },
    body: JSON.stringify({ id, recipe, cases }),
  });
  const deadline = Date.now() + 330000;
  let result;
  while (Date.now() < deadline) {
    result = await (await request(`?id=${id}`)).json();
    assert.ok(
      !["failed", "interrupted"].includes(result.status),
      `Hosted ${recipe} run ${id} ${result.status}`,
    );
    if (result.status === "completed") break;
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
  assert.equal(
    result?.status,
    "completed",
    "The Vercel queue did not finish within the deadline",
  );
  assert.equal(result.recipe, recipe);
  assert.equal(result.provider, "Vercel Sandbox");
  assert.equal(result.source_commit, manifest.source_commit);
  assert.equal(result.lab_source_commit, manifest.source_commit);
  assert.equal(result.sandbox_stopped, true);
  assert.ok(
    result.progress?.finished_at,
    "Completed runs must retain timestamped progress",
  );
  assert.ok(
    result.progress.events.every(
      (event) => event.outcome === "completed" && event.finished_at,
    ),
  );
  for (const phase of [
    `Running baseline ${recipe === "mne" ? "annotation attachment and timestamp controls" : "and fresh uninspected controls"}`,
    `Running patched ${recipe === "mne" ? "annotation attachment and timestamp controls" : "and fresh uninspected controls"}`,
    "Stopping isolated runtime",
    "Saving result bundle",
  ])
    assert.ok(
      result.progress.events.some((event) => event.label === phase),
      `Missing actual worker phase: ${phase}`,
    );
  assert.equal(result.comparisons.length, 2);
  assert.deepEqual(
    result.comparisons.map((value) => value.input),
    cases,
  );
  if (recipe === "nwb") {
    assert.ok(
      result.comparisons.every((value) => value.outcome === "patch-preserved"),
    );
    assert.deepEqual(
      result.comparisons.map((value) => value.baseline.changed_rows),
      [300, 51],
    );
    assert.ok(
      result.comparisons.every((value) => value.patched.changed_rows === 0),
    );
  } else {
    assert.deepEqual(
      result.comparisons.map((value) => value.outcome),
      ["patch-preserved", "both-preserved"],
    );
    assert.deepEqual(
      result.comparisons.map((value) => value.baseline.floor_index),
      [0, 1],
    );
    assert.deepEqual(
      result.comparisons.map((value) => value.patched.floor_index),
      [1, 1],
    );
    assert.ok(
      result.comparisons.every(
        (value) =>
          value.patched.onset_seconds === value.reference.onset_seconds,
      ),
    );
    assert.ok(
      result.comparisons.every((value) =>
        [value.baseline, value.patched].every(
          (run) => run.rounded_index === value.input.sample,
        ),
      ),
    );
  }
  const archive = Buffer.from(
    await (await request(`?id=${id}&download=1`)).arrayBuffer(),
  );
  assert.equal(
    crypto.createHash("sha256").update(archive).digest("hex"),
    result.bundle_sha256,
  );
  const output = path.resolve(".runs/deployed-lab");
  fs.mkdirSync(output, { recursive: true });
  fs.writeFileSync(
    path.join(output, recipe === "nwb" ? "result.json" : "mne-result.json"),
    JSON.stringify({ deployment, ...result }, null, 2) + "\n",
  );
  console.log(
    `Verified actual ${recipe} queue → Sandbox → private result → download: ${id}`,
  );
}
(async () => {
  assert.ok(
    secret && /^https:\/\/[a-z0-9.-]+\.vercel\.app$/.test(deployment),
    "A protected Vercel URL and verification credential are required",
  );
  const capability = await (await request()).json();
  assert.equal(
    capability.enabled,
    true,
    "Enable the lab and connect its private Blob store before deploying",
  );
  assert.equal(capability.source_commit, manifest.source_commit);
  assert.deepEqual(capability.recipes, ["nwb", "mne"]);
  assert.equal(capability.daily_limit, 10);
  await verifyRecipe("nwb", [
    DEFAULT,
    {
      ...DEFAULT,
      rows: 51,
      channels: 3,
      buffer: 25,
      pattern: "random",
      backend: "zarr",
      iterator: "generic",
    },
  ]);
  await verifyRecipe("mne", [
    MNE_DEFAULT,
    { ...MNE_DEFAULT, sfreq: 1000, origin: "utc" },
  ]);
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
