// Contract checks use in-memory service doubles; they never launch hosted compute.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const { Readable } = require("node:stream");
const { NodejsLambda, sanitizeConsumerName } = require("@vercel/build-utils");
const {
  DEFAULT,
  MNE_DEFAULT,
  validateRecipe,
  validateCases,
  summarize,
} = require("./contracts.cjs");
const values = new Map();
const files = new Map();
let sent = 0;
let reserved = 0;
let executions = 0;
const build = { commit: "test-commit" };
const store = {
  build,
  key: (id, name) => `${id}/${name}`,
  readJSON: async (id, name) => values.get(`${id}/${name}`) || null,
  read: async (key) => files.get(key) || null,
  write: async (key, value) => files.set(key, value),
  writeJSON: async (id, name, value) => {
    const key = `${id}/${name}`;
    if (values.has(key)) {
      const error = new Error("exists");
      error.exists = true;
      throw error;
    }
    values.set(key, JSON.parse(JSON.stringify(value)));
  },
  writeProgress: async (id, value) =>
    values.set(`${id}/progress.json`, JSON.parse(JSON.stringify(value))),
  reserveDailySlot: async () => ++reserved <= 10,
  existsError: (error) => error.exists,
};
const queue = {
  send: async () => {
    sent++;
  },
  handleNodeCallback: (handler) => handler,
};
function load(name, extra = {}) {
  const module = { exports: {} };
  vm.runInNewContext(
    fs.readFileSync(`${__dirname}/${name}.cjs`, "utf8"),
    {
      module,
      exports: module.exports,
      require: (key) =>
        key === "./store.cjs"
          ? store
          : key === "@vercel/queue"
            ? {
                QueueClient: function () {
                  return queue;
                },
              }
            : extra[key] ||
              (/\.(py|patch|txt)$/.test(key)
                ? fs.readFileSync(
                    require("node:path").resolve(__dirname, key),
                    "utf8",
                  )
                : require(key)),
      KUFU_SOURCE: build,
      process: { env: { KUFU_LAB_ENABLED: "1", BLOB_STORE_ID: "test-store" } },
      URL,
      Buffer,
      console,
    },
    { filename: name },
  );
  return module.exports;
}
const api = load("api");
async function request(
  method,
  data,
  headers = {},
  path = "/api/experiments",
  parsed = false,
) {
  const req = Readable.from(data && !parsed ? [JSON.stringify(data)] : []);
  if (parsed) req.body = data;
  Object.assign(req, {
    method,
    url: path,
    headers: {
      host: "lab.test",
      origin: "https://lab.test",
      "content-type": "application/json",
      ...headers,
    },
  });
  const response = {
    statusCode: 200,
    headers: {},
    setHeader(key, value) {
      this.headers[key] = value;
    },
    end(value) {
      this.body = Buffer.isBuffer(value)
        ? value
        : value
          ? JSON.parse(value)
          : null;
    },
  };
  await api(req, response);
  return {
    code: response.statusCode,
    body: response.body,
    headers: response.headers,
  };
}
(async () => {
  const id = "12345678-1234-4123-8123-123456789abc";
  assert.throws(() => validateCases([{ ...DEFAULT, rows: 2001 }]));
  assert.throws(() => validateCases([{ ...DEFAULT, code: "bad" }]));
  assert.throws(() => validateCases(Array(5).fill(DEFAULT)));
  assert.equal((await request("GET")).code, 200);
  assert.equal(sent, 0, "Opening the lab cannot start work");
  assert.equal(
    (
      await request(
        "POST",
        { id, cases: [DEFAULT] },
        { origin: "https://other.test" },
      )
    ).code,
    403,
  );
  assert.equal(
    (await request("POST", { id, cases: [{ ...DEFAULT, seed: "42" }] })).code,
    400,
  );
  assert.equal(sent, 0);
  assert.equal((await request("POST", { id, cases: [DEFAULT] })).code, 202);
  assert.equal(reserved, 1);
  assert.equal(
    (
      await request(
        "POST",
        { id, cases: [DEFAULT] },
        {},
        "/api/experiments",
        true,
      )
    ).code,
    202,
    "Vercel launcher-parsed bodies must work",
  );
  assert.equal((await request("POST", { id, cases: [DEFAULT] })).code, 202);
  assert.equal(
    reserved,
    1,
    "Same submission must not consume another daily slot",
  );
  assert.equal(
    (await request("POST", { id, cases: [{ ...DEFAULT, rows: 2 }] })).code,
    409,
  );
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${id}`)).body.status,
    "queued",
  );
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${id}`)).body.progress
      .events[0].outcome,
    "active",
  );
  const worker = load("worker", {
    "./run.cjs": {
      execute: async (_cases, report) => {
        executions++;
        await report("Installing pinned dependencies");
        const running = (
          await request("GET", null, {}, `/api/experiments?id=${id}`)
        ).body;
        assert.equal(running.status, "running");
        assert.equal(
          running.progress.events.at(-1).label,
          "Installing pinned dependencies",
        );
        assert.equal(running.progress.events.at(-1).outcome, "active");
        assert.ok(running.progress.events[0].finished_at);
        await report("Running baseline and fresh uninspected controls");
        return {
          archive: Buffer.from("zip"),
          record: { comparisons: [] },
          logs: [],
        };
      },
    },
  });
  await worker.processRun({ id, source_commit: build.commit });
  await worker.processRun({ id, source_commit: build.commit });
  assert.equal(
    executions,
    1,
    "Duplicate queue delivery must not launch another Sandbox",
  );
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${id}`)).body.status,
    "completed",
  );
  const finished = (await request("GET", null, {}, `/api/experiments?id=${id}`))
    .body.progress;
  assert.ok(
    finished.events.every(
      (event) => event.outcome === "completed" && event.finished_at,
    ),
  );
  assert.equal(finished.events.at(-1).label, "Saving result bundle");
  assert.ok(finished.finished_at);
  const failureId = "12345678-1234-4123-8123-123456789abd";
  await request("POST", { id: failureId, cases: [DEFAULT] });
  const failingWorker = load("worker", {
    "./run.cjs": {
      execute: async (_cases, report) => {
        await report("Running patched and fresh uninspected controls");
        throw new Error("deliberate fixture failure");
      },
    },
  });
  await failingWorker.processRun({
    id: failureId,
    source_commit: build.commit,
  });
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${failureId}`)).body
      .status,
    "failed",
  );
  const failedProgress = (
    await request("GET", null, {}, `/api/experiments?id=${failureId}`)
  ).body.progress;
  assert.equal(
    failedProgress.events.at(-1).label,
    "Running patched and fresh uninspected controls",
  );
  assert.equal(failedProgress.events.at(-1).outcome, "failed");
  const control = {
    input_sha256: "same",
    values_equal: true,
    shape_equal: true,
    dtype_equal: true,
    inspection_errors: [],
  };
  const baseline = {
    cases: [
      {
        input: DEFAULT,
        control,
        inspected: { ...control, values_equal: false },
      },
    ],
  };
  const patched = { cases: [{ input: DEFAULT, control, inspected: control }] };
  assert.equal(summarize(baseline, patched)[0].outcome, "patch-preserved");
  assert.equal(summarize(patched, patched)[0].outcome, "both-preserved");
  assert.equal(summarize(patched, baseline)[0].outcome, "patch-changed-data");
  assert.throws(() =>
    summarize(baseline, {
      cases: [
        {
          ...patched.cases[0],
          inspected: { ...control, input_sha256: "different" },
        },
      ],
    }),
  );
  assert.equal(validateRecipe(), "nwb");
  for (const invalid of [null, "other", "__proto__"])
    assert.throws(() => validateRecipe(invalid));
  for (const input of [
    { ...MNE_DEFAULT, sfreq: 127 },
    { ...MNE_DEFAULT, sfreq: 8193 },
    { ...MNE_DEFAULT, sample: -1 },
    { ...MNE_DEFAULT, sample: 1025 },
    { ...MNE_DEFAULT, sample: true },
    { ...MNE_DEFAULT, origin: "url" },
    { ...MNE_DEFAULT, code: "bad" },
  ])
    assert.throws(() => validateCases([input], "mne"));
  assert.deepEqual(validateCases([MNE_DEFAULT], "mne"), [MNE_DEFAULT]);
  const mneId = "12345678-1234-4123-8123-123456789aee";
  assert.equal(
    (
      await request("POST", {
        id: mneId,
        recipe: "other",
        cases: [MNE_DEFAULT],
      })
    ).code,
    400,
  );
  assert.equal(
    (await request("POST", { id: mneId, recipe: "mne", cases: [MNE_DEFAULT] }))
      .code,
    202,
  );
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${mneId}`)).body
      .recipe,
    "mne",
  );
  assert.equal(
    (await request("POST", { id: mneId, recipe: "nwb", cases: [DEFAULT] }))
      .code,
    409,
  );
  const mneWorker = load("worker", {
    "./run.cjs": {
      execute: async (_cases, report, _credentials, recipe) => {
        assert.equal(recipe, "mne");
        await report(
          "Running patched annotation attachment and timestamp controls",
        );
        return {
          archive: Buffer.from("mne-zip"),
          record: { comparisons: [] },
          logs: [],
        };
      },
    },
  });
  await mneWorker.processRun({ id: mneId, source_commit: build.commit });
  const mneDone = (
    await request("GET", null, {}, `/api/experiments?id=${mneId}`)
  ).body;
  assert.equal(mneDone.status, "completed");
  assert.equal(mneDone.recipe, "mne");
  const download = await request(
    "GET",
    null,
    {},
    `/api/experiments?id=${mneId}&download=1`,
  );
  assert.equal(download.code, 200);
  assert.match(download.headers["Content-Disposition"], /kufu-mne-/);
  assert.equal(download.body.toString(), "mne-zip");
  const legacyId = "12345678-1234-4123-8123-123456789aff";
  values.set(`${legacyId}/submission.json`, {
    cases: [DEFAULT],
    created_at: new Date().toISOString(),
  });
  const slotsBeforeLegacy = reserved;
  assert.equal(
    (await request("POST", { id: legacyId, cases: [DEFAULT] })).code,
    202,
  );
  assert.equal(reserved, slotsBeforeLegacy);
  assert.equal(
    (await request("GET", null, {}, `/api/experiments?id=${legacyId}`)).body
      .recipe,
    "nwb",
  );
  const mneReports = ["baseline", "patched"].map(
    (mode) => `.runs/contracts/mne/parameterized-${mode}/report.json`,
  );
  if (mneReports.every((file) => fs.existsSync(file))) {
    const reports = mneReports.map((file) => JSON.parse(fs.readFileSync(file)));
    const comparisons = summarize(...reports, "mne");
    assert.equal(comparisons.length, 4);
    assert.ok(
      comparisons.every((value) =>
        ["patch-preserved", "both-preserved"].includes(value.outcome),
      ),
    );
    const invalid = structuredClone(reports[1]);
    invalid.cases[0].controls.signal_unchanged = false;
    assert.equal(
      summarize(reports[0], invalid, "mne")[0].outcome,
      "invalid-comparison",
    );
    const changed = structuredClone(reports[1]);
    changed.cases[0].attached.onset_seconds += 0.01;
    assert.equal(
      summarize(reports[0], changed, "mne")[0].outcome,
      "patch-changed-data",
    );
    const mismatched = structuredClone(reports[1]);
    mismatched.cases[0].input_sha256 = "other";
    assert.throws(() => summarize(reports[0], mismatched, "mne"));
    const edges = ["baseline", "patched"].map((mode) =>
      JSON.parse(
        fs.readFileSync(`.runs/contracts/mne/boundary-${mode}/report.json`),
      ),
    );
    assert.ok(
      summarize(...edges, "mne").every((value) =>
        ["patch-preserved", "both-preserved"].includes(value.outcome),
      ),
      "MNE boundary cases must preserve patched timestamps and controls",
    );
  } else if (process.env.CI)
    throw new Error("CI is missing actual MNE experiment reports");
  const reports = ["baseline", "patched"].map(
    (mode) => `.runs/contracts/nwb/parameterized-${mode}/report.json`,
  );
  if (reports.every((file) => fs.existsSync(file))) {
    const actual = summarize(
      ...reports.map((file) => JSON.parse(fs.readFileSync(file))),
    );
    assert.equal(actual.length, 4);
    assert.ok(
      actual.every((c) =>
        ["patch-preserved", "both-preserved"].includes(c.outcome),
      ),
      "Parameterized real-software comparisons must preserve controls and patched outputs",
    );
    console.log("Four real parameterized NWB comparisons passed.");
  } else if (process.env.CI)
    throw new Error("CI is missing parameterized scientific reports");
  for (const recipe of ["nwb", "mne"]) {
    const paths = ["baseline", "patched"].map(
      (mode) => `.runs/contracts/${recipe}/parameterized-${mode}/report.json`,
    );
    const actualReports = paths.map((file) =>
      JSON.parse(fs.readFileSync(file)),
    );
    let stopped = 0;
    let denied = false;
    const commands = [];
    const sandbox = {
      name: "fixture-sandbox",
      writeFiles: async () => {},
      update: async ({ networkPolicy }) => {
        denied = networkPolicy === "deny-all";
      },
      runCommand: async (command) => {
        commands.push(command);
        if (command.args.includes("--mode"))
          assert.equal(
            denied,
            true,
            "Network must be denied before scientific execution",
          );
        return {
          exitCode: 0,
          stdout: async () => "fixture",
          stderr: async () => "",
        };
      },
      readFileToBuffer: async ({ path }) =>
        path === "results.zip"
          ? Buffer.from("fixture-archive")
          : Buffer.from(
              JSON.stringify(actualReports[path.includes("baseline") ? 0 : 1]),
            ),
      stop: async () => {
        stopped++;
      },
    };
    const runner = load("run", {
      "@vercel/sandbox": {
        Sandbox: {
          create: async (options) => {
            assert.equal(options.persistent, false);
            assert.equal(options.resources.vcpus, 1);
            assert.equal(options.timeout, 240000);
            return sandbox;
          },
        },
      },
    });
    const inputs = actualReports[0].cases.map((value) => value.input);
    const result = await runner.execute(inputs, async () => {}, {}, recipe);
    assert.equal(result.record.recipe, recipe);
    assert.equal(result.record.sandbox_stopped, true);
    assert.equal(stopped, 1);
    assert.equal(result.record.comparisons.length, inputs.length);
    assert.equal(
      commands.some((command) => command.args.includes("-e")),
      recipe === "nwb",
    );
    sandbox.runCommand = async () => ({
      exitCode: 2,
      stdout: async () => "",
      stderr: async () => "fixture failure",
    });
    await assert.rejects(
      () => runner.execute(inputs, async () => {}, {}, recipe),
      /failed/,
    );
    assert.equal(stopped, 2, "A failed setup command must stop the Sandbox");
    sandbox.runCommand = async () => ({
      exitCode: 0,
      stdout: async () => "fixture",
      stderr: async () => "",
    });
    await assert.rejects(
      () =>
        runner.execute(
          inputs,
          async (label) => {
            if (label === "Stopping isolated runtime")
              throw new Error("progress unavailable");
          },
          {},
          recipe,
        ),
      /progress unavailable/,
    );
    assert.equal(
      stopped,
      3,
      "A progress-storage failure must not prevent Sandbox cleanup",
    );
  }
  for (const name of ["experiments", "experiment-worker"]) {
    const config = JSON.parse(
      fs.readFileSync(
        `dist-backend/functions/api/${name}.func/.vc-config.json`,
      ),
    );
    assert.equal(config.launcherType, "Nodejs");
    assert.equal(config.runtime, "nodejs22.x");
    new NodejsLambda({ ...config, files: {} });
    if (name === "experiment-worker") {
      assert.equal(config.experimentalTriggers[0].maxConcurrency, 1);
      assert.equal(
        config.experimentalTriggers[0].consumer,
        sanitizeConsumerName("api/experiment-worker"),
      );
      const invalid = {
        ...config,
        experimentalTriggers: [{ ...config.experimentalTriggers[0] }],
      };
      delete invalid.experimentalTriggers[0].consumer;
      assert.throws(
        () => new NodejsLambda({ ...invalid, files: {} }),
        /consumer is required/,
      );
    }
  }
  console.log(
    "Execution API validation, CSRF protection, idempotency, worker failures and result classification passed. No hosted compute launched by these contract checks.",
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
