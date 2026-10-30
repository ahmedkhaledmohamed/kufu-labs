const { Sandbox } = require("@vercel/sandbox");
const {
  summarize,
  hash,
  validateCases,
  validateRecipe,
} = require("./contracts.cjs");
// Only these two reviewed payloads can run; requests supply parameters, not code.
const recipes = {
  nwb: {
    project: "projects/nwb-stream-integrity",
    patch: "non-consuming-shape.patch",
    metadata: "verification.json",
    checkout: "nwb",
    sourceSuffix: "/src",
    moduleHash: "shape_module_sha256",
    inputKind: "Synthetic int16 signals; no neural recordings",
    payload: {
      "experiment.py": require("../projects/nwb-stream-integrity/experiment.py"),
      "prepare.py": require("../projects/nwb-stream-integrity/prepare.py"),
      "non-consuming-shape.patch": require("../projects/nwb-stream-integrity/non-consuming-shape.patch"),
      "requirements.txt": require("../projects/nwb-stream-integrity/requirements.txt"),
      "verification.json": JSON.stringify(
        require("../projects/nwb-stream-integrity/verification.json"),
      ),
    },
  },
  mne: {
    project: "projects/mne-annotation-onsets",
    patch: "preserve-interior-onsets.patch",
    metadata: "profile.json",
    checkout: "mne",
    sourceSuffix: "",
    moduleHash: "annotations_sha256",
    inputKind:
      "Constructed one-channel linear ramp; no neural recordings or neural simulation",
    payload: {
      "experiment.py": require("../projects/mne-annotation-onsets/experiment.py"),
      "prepare.py": require("../projects/mne-annotation-onsets/prepare.py"),
      "preserve-interior-onsets.patch": require("../projects/mne-annotation-onsets/preserve-interior-onsets.patch"),
      "requirements.txt": require("../projects/mne-annotation-onsets/requirements.txt"),
      "profile.json": JSON.stringify(
        require("../projects/mne-annotation-onsets/profile.json"),
      ),
    },
  },
};
async function execute(
  cases,
  onProgress = async () => {},
  credentials = {},
  recipe = "nwb",
) {
  validateRecipe(recipe);
  validateCases(cases, recipe);
  const config = recipes[recipe];
  const { project, payload } = config;
  const upstream = JSON.parse(payload[config.metadata]);
  const started = Date.now();
  let sandbox;
  let failed = false;
  const logs = [];
  const record = {
    lab_source_commit: KUFU_SOURCE.commit,
    recipe,
    provider: "Vercel Sandbox",
    upstream_commit: upstream.upstream_commit || upstream.source_revision,
    patch_sha256: hash(payload[config.patch]),
    experiment_sha256: hash(payload["experiment.py"]),
    requirements_sha256: hash(payload["requirements.txt"]),
    input_kind: config.inputKind,
    cases,
  };
  async function command(label, cmd, args, env = {}) {
    await onProgress(label);
    const result = await sandbox.runCommand({
      cmd,
      args,
      cwd: "/vercel/sandbox",
      env,
    });
    const stdout = await result.stdout();
    const stderr = await result.stderr();
    logs.push({
      phase: label,
      exit_code: result.exitCode,
      stdout: stdout.slice(-24000),
      stderr: stderr.slice(-24000),
    });
    if (result.exitCode !== 0)
      throw new Error(`${label} failed (exit ${result.exitCode}).`);
  }
  try {
    await onProgress("Starting isolated Python runtime");
    sandbox = await Sandbox.create({
      ...credentials,
      runtime: "python3.13",
      persistent: false,
      resources: { vcpus: 1 },
      timeout: 240000,
      networkPolicy: {
        allow: [
          "github.com",
          "release-assets.githubusercontent.com",
          "pypi.org",
          "files.pythonhosted.org",
        ],
      },
    });
    record.sandbox_name = sandbox.name;
    record.runtime = "CPython 3.13.9, managed by uv 0.9.5";
    await sandbox.writeFiles(
      Object.entries(payload)
        .map(([name, content]) => ({
          path: `${project}/${name}`,
          content: Buffer.from(content),
        }))
        .concat([
          { path: "inputs.json", content: Buffer.from(JSON.stringify(cases)) },
        ]),
    );
    await command(
      "Preparing pinned upstream sources",
      "python3",
      [`${project}/prepare.py`],
      { GIT_LFS_SKIP_SMUDGE: "1" },
    );
    // Vercel's legacy Python runtime lacks _bz2. Install a complete pinned
    // interpreter rather than silently dropping Zarr or changing its codecs.
    await command("Installing pinned Python bootstrap", "python3", [
      "-m",
      "pip",
      "install",
      "--disable-pip-version-check",
      "--index-url",
      "https://pypi.org/simple",
      "uv==0.9.5",
    ]);
    await command("Preparing complete CPython 3.13.9", "python3", [
      "-m",
      "uv",
      "venv",
      "--python",
      "3.13.9",
      "/vercel/sandbox/venv",
    ]);
    await command("Installing pinned dependencies", "python3", [
      "-m",
      "uv",
      "pip",
      "install",
      "--python",
      "/vercel/sandbox/venv/bin/python",
      "--index-url",
      "https://pypi.org/simple",
      "-r",
      `${project}/requirements.txt`,
    ]);
    if (recipe === "nwb") {
      await command("Installing upstream package metadata", "python3", [
        "-m",
        "uv",
        "pip",
        "install",
        "--python",
        "/vercel/sandbox/venv/bin/python",
        "--index-url",
        "https://pypi.org/simple",
        "--no-deps",
        "-e",
        `.external/${config.checkout}-patched`,
      ]);
    }
    await sandbox.update({ networkPolicy: "deny-all" });
    for (const mode of ["baseline", "patched"])
      await command(
        `Running ${mode} ${recipe === "mne" ? "annotation attachment and timestamp controls" : "and fresh uninspected controls"}`,
        "/vercel/sandbox/venv/bin/python",
        [
          `${project}/experiment.py`,
          "--mode",
          mode,
          "--input",
          "inputs.json",
          "--output",
          `outputs/${mode}`,
        ],
        {
          PYTHONPATH: `/vercel/sandbox/.external/${config.checkout}-${mode === "baseline" ? "clean" : "patched"}${config.sourceSuffix}`,
          NWBI_SKIP_NETWORK_TESTS: "1",
        },
      );
    const baseline = JSON.parse(
      (
        await sandbox.readFileToBuffer({ path: "outputs/baseline/report.json" })
      ).toString(),
    );
    const patched = JSON.parse(
      (
        await sandbox.readFileToBuffer({ path: "outputs/patched/report.json" })
      ).toString(),
    );
    record.comparisons = summarize(baseline, patched, recipe);
    record.environment = {
      baseline: baseline.versions,
      patched: patched.versions,
      python: patched.python,
      baseline_module_sha256: baseline[config.moduleHash],
      patched_module_sha256: patched[config.moduleHash],
    };
    await sandbox.writeFiles([
      {
        path: "outputs/manifest.json",
        content: Buffer.from(JSON.stringify(record, null, 2)),
      },
      {
        path: "outputs/logs.json",
        content: Buffer.from(JSON.stringify(logs, null, 2)),
      },
    ]);
    await command("Packaging actual arrays and reports", "python3", [
      "-c",
      "import shutil; shutil.make_archive('/vercel/sandbox/results', 'zip', '/vercel/sandbox/outputs')",
    ]);
    const archive = await sandbox.readFileToBuffer({ path: "results.zip" });
    if (!archive || archive.length > 3000000)
      throw new Error("Result bundle exceeds the lab limit.");
    record.bundle_sha256 = hash(archive);
    return { record, archive, logs };
  } catch (error) {
    failed = true;
    error.labLogs = logs;
    throw error;
  } finally {
    if (sandbox) {
      try {
        if (!failed) await onProgress("Stopping isolated runtime");
      } finally {
        // A progress-storage outage must never prevent VM cleanup.
        await sandbox.stop();
      }
      record.sandbox_stopped = true;
      record.elapsed_seconds = Number(
        ((Date.now() - started) / 1000).toFixed(3),
      );
    }
  }
}
module.exports = { execute };
