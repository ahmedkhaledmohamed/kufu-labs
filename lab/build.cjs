const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const esbuild = require("esbuild");
const {
  NodejsLambda,
  FileFsRef,
  sanitizeConsumerName,
} = require("@vercel/build-utils");
const root = path.resolve(__dirname, "..");
const output = path.join(root, "dist-backend");
async function main() {
  fs.rmSync(output, { recursive: true, force: true });
  const source = {
    commit: execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: root,
      encoding: "utf8",
    }).trim(),
  };
  for (const [name, entry, duration] of [
    ["experiments", "api", 30],
    ["auth", "auth-handler", 30],
    ["experiment-worker", "worker", 300],
  ]) {
    const directory = path.join(output, "functions", "api", `${name}.func`);
    fs.mkdirSync(directory, { recursive: true });
    await esbuild.build({
      entryPoints: [path.join(__dirname, `${entry}.cjs`)],
      outfile: path.join(directory, "index.cjs"),
      bundle: true,
      platform: "node",
      target: "node22",
      format: "cjs",
      loader: { ".py": "text", ".patch": "text", ".txt": "text" },
      define: { KUFU_SOURCE: JSON.stringify(source) },
    });
    const config = {
      runtime: "nodejs22.x",
      handler: "index.cjs",
      launcherType: "Nodejs",
      shouldAddHelpers: true,
      maxDuration: duration,
      regions: ["iad1"],
      ...(entry === "worker"
        ? {
            experimentalTriggers: [
              {
                type: "queue/v2beta",
                topic: "kufu-nwb",
                consumer: sanitizeConsumerName(`api/${name}`),
                maxConcurrency: 1,
                maxDeliveries: 2,
              },
            ],
          }
        : {}),
    };
    // Validate the prebuilt contract with the same class used by Vercel deploy.
    // Framework trigger input omits consumer; Build Output must include it.
    new NodejsLambda({
      ...config,
      files: {
        "index.cjs": new FileFsRef({
          fsPath: path.join(directory, "index.cjs"),
        }),
      },
    });
    fs.writeFileSync(
      path.join(directory, ".vc-config.json"),
      JSON.stringify(config),
    );
  }
  const manifestPath = path.join(root, "dist/build-info.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath));
  const files = {};
  for (const name of fs.readdirSync(output, { recursive: true })) {
    const file = path.join(output, name);
    if (fs.statSync(file).isFile())
      files[name] = crypto
        .createHash("sha256")
        .update(fs.readFileSync(file))
        .digest("hex");
  }
  manifest.backend_files = files;
  manifest.execution =
    "Static evidence pages plus explicitly requested NWB and MNE experiments in Vercel Sandbox via authenticated Functions and Queues.";
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n");
  console.log(
    `Bundled three Vercel Functions; ${Object.keys(files).length} backend assets recorded.`,
  );
}
main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
