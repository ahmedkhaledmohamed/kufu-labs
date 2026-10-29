// Promote only the tested static and backend artifacts, with verified owner/protection.
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "..");
const config = require("./deployment-config.json");
const cli = path.join(root, "node_modules/.bin/vercel");
// Vercel CLI 65 resolves --scope through /v2/user unless the team mapping is cached.
// A project token cannot read user/team resources (upstream issue #17506).
// Only verified non-secret scope metadata is cached. The project API still
// enforces the token, and target() checks the actual owner and protection.
const cliProfile = process.env.VERCEL_TOKEN
  ? fs.mkdtempSync(path.join(os.tmpdir(), "lab-vercel-cli-"))
  : null;
if (cliProfile)
  fs.writeFileSync(
    path.join(cliProfile, "config.json"),
    JSON.stringify({
      currentTeam: config.teamId,
      cachedTeamIds: { [config.scope]: config.teamId },
    }),
  );
const cliContextArgs = [
  "--scope",
  config.scope,
  ...(cliProfile ? ["--global-config", cliProfile] : []),
];
const env = {
  ...process.env,
  VERCEL_TELEMETRY_DISABLED: "1",
  DO_NOT_TRACK: "1",
  VERCEL_ORG_ID: config.teamId,
  VERCEL_PROJECT_ID: config.projectId,
};
const api = (endpoint, method = "GET", data) => {
  const raw = execFileSync(
    cli,
    [
      "api",
      endpoint,
      "--method",
      method,
      ...cliContextArgs,
      "--raw",
      ...(data ? ["--input", "-"] : []),
    ],
    {
      cwd: root,
      env,
      input: data ? JSON.stringify(data) : undefined,
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
    },
  );
  if (raw.trim()) return JSON.parse(raw);
  assert.notEqual(method, "GET", "Empty response from a required API read");
  return null;
};
function target() {
  const p = api("/v9/projects/" + config.projectId);
  assert.equal(p.id, config.projectId);
  assert.equal(p.name, config.projectName);
  assert.equal(p.accountId, config.teamId);
  assert.equal(
    p.ssoProtection?.deploymentType,
    "all",
    "Both preview and production must remain protected",
  );
  return p;
}
(async () => {
  const mode = process.argv[2];
  assert.ok(["preview", "production", "verify-target"].includes(mode));
  const project = target();
  if (mode === "verify-target") {
    console.log(
      "Verified personal lab project and all-deployment authentication.",
    );
    return;
  }
  assert.ok(
    process.env.VERCEL_TOKEN,
    "A project-scoped VERCEL_TOKEN is required",
  );
  assert.ok(
    process.env.VERCEL_AUTOMATION_BYPASS_SECRET,
    "A project-specific verification secret is required",
  );
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, "dist/build-info.json"), "utf8"),
  );
  for (const [file, hash] of Object.entries(manifest.files))
    assert.equal(
      crypto
        .createHash("sha256")
        .update(fs.readFileSync(path.join(root, "dist", file)))
        .digest("hex"),
      hash,
      `Artifact changed: ${file}`,
    );
  assert.equal(
    Object.keys(manifest.backend_files || {}).length,
    4,
    "Missing tested execution backend",
  );
  for (const [file, hash] of Object.entries(manifest.backend_files))
    assert.equal(
      crypto
        .createHash("sha256")
        .update(fs.readFileSync(path.join(root, "dist-backend", file)))
        .digest("hex"),
      hash,
      `Backend artifact changed: ${file}`,
    );
  if (process.env.GITHUB_SHA)
    assert.equal(manifest.source_commit, process.env.GITHUB_SHA);
  const web = JSON.parse(
    fs.readFileSync(path.join(root, ".runs/hub/results.json"), "utf8"),
  );
  assert.equal(
    web.artifactManifestSha256,
    crypto
      .createHash("sha256")
      .update(fs.readFileSync(path.join(root, "dist/build-info.json")))
      .digest("hex"),
    "Deploy only the exact browser-tested artifact",
  );
  assert.deepEqual(web.pageErrors, []);
  assert.equal(web.pages, 6);
  const vercel = path.join(root, ".vercel");
  fs.mkdirSync(vercel, { recursive: true });
  fs.writeFileSync(
    path.join(vercel, "project.json"),
    JSON.stringify({
      projectId: config.projectId,
      orgId: config.teamId,
      projectName: config.projectName,
    }),
  );
  const output = path.join(vercel, "output");
  fs.rmSync(output, { recursive: true, force: true });
  fs.mkdirSync(output, { recursive: true });
  fs.cpSync(path.join(root, "dist"), path.join(output, "static"), {
    recursive: true,
  });
  fs.cpSync(
    path.join(root, "dist-backend/functions"),
    path.join(output, "functions"),
    { recursive: true },
  );
  fs.writeFileSync(
    path.join(output, "config.json"),
    JSON.stringify({
      version: 3,
      routes: [
        {
          src: "/(.*)",
          headers: {
            "X-Content-Type-Options": "nosniff",
            "X-Robots-Tag": "noindex, nofollow",
            "Referrer-Policy": "strict-origin-when-cross-origin",
          },
          continue: true,
        },
        { handle: "filesystem" },
      ],
    }),
  );
  const args = [
    "deploy",
    "--prebuilt",
    "--yes",
    ...cliContextArgs,
    "--meta",
    `sourceCommit=${manifest.source_commit}`,
  ];
  // Skip custom domain assignment; Vercel can still assign generated aliases.
  // Only main may request explicit production promotion after remote verification.
  if (mode === "production" || !project.targets?.production)
    args.push("--prod", "--skip-domain");
  const raw = execFileSync(cli, args, {
    cwd: root,
    env,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "inherit"],
  }).trim();
  const deployment = raw
    .split(/\s+/)
    .findLast((s) => /^https:\/\/[a-z0-9.-]+\.vercel\.app\/?$/.test(s));
  assert.ok(deployment, "No deployment URL returned");
  execFileSync(process.execPath, [path.join(root, "site/verify.cjs")], {
    cwd: root,
    env: {
      ...env,
      HUB_URL: deployment,
      HUB_OUTPUT: path.join(root, ".runs/deployed"),
    },
    stdio: "inherit",
  });
  // Confirm unauthenticated users cannot read the private site or its catalogue.
  for (const resource of [
    "/",
    "/site/catalog.json",
    "/projects/overlap-inspector/index.html",
    "/api/experiments",
  ]) {
    const response = await fetch(deployment + resource, { redirect: "manual" });
    assert.ok(
      [301, 302, 303, 307, 308, 401, 403].includes(response.status),
      "Unauthenticated content exposed",
    );
  }
  target();
  const capability = await fetch(deployment + "/api/experiments", {
    headers: {
      "x-vercel-protection-bypass": process.env.VERCEL_AUTOMATION_BYPASS_SECRET,
    },
  });
  assert.equal(
    capability.status,
    200,
    "Execution API failed its read-only deployment check",
  );
  const execution = await capability.json();
  assert.equal(execution.provider, "Vercel Sandbox");
  assert.equal(execution.source_commit, manifest.source_commit);
  execFileSync(process.execPath, [path.join(root, "lab/verify-deployed.cjs")], {
    cwd: root,
    env: { ...env, HUB_URL: deployment },
    stdio: "inherit",
  });
  if (mode === "production") {
    assert.equal(
      process.env.GITHUB_REF,
      "refs/heads/main",
      "Production must originate from main",
    );
    const upstream = JSON.parse(
      execFileSync(
        "gh",
        ["api", `repos/${config.repository}/git/ref/heads/main`],
        { env, encoding: "utf8" },
      ),
    );
    assert.equal(
      upstream.object.sha,
      manifest.source_commit,
      "Refuse to promote a stale main build",
    );
    const details = api("/v13/deployments/" + new URL(deployment).host);
    const deploymentId = details.id || details.uid;
    assert.ok(deploymentId, "Missing deployment identity");
    assert.equal(details.projectId, config.projectId);
    assert.equal(details.ownerId, config.teamId);
    assert.equal(details.target, "production");
    assert.equal(details.readyState, "READY");
    assert.equal(details.meta?.sourceCommit, manifest.source_commit);
    // `promote` resolves user/team metadata even with a cached scope. Use its
    // documented project endpoint with the same project-scoped credential.
    api(
      `/v10/projects/${config.projectId}/promote/${deploymentId}`,
      "POST",
      {},
    );
    const deadline = Date.now() + 180_000;
    let completed = false;
    while (Date.now() < deadline) {
      const current = target();
      const state = current.lastAliasRequest;
      if (state?.toDeploymentId === deploymentId) {
        assert.notEqual(
          state.jobStatus,
          "failed",
          "Production promotion failed",
        );
        assert.notEqual(
          state.jobStatus,
          "skipped",
          "Production promotion skipped",
        );
      }
      // lastAliasRequest may be absent even after a successful promotion.
      // Check the authoritative current production target instead.
      const production = current.targets?.production;
      if (
        production?.id === deploymentId &&
        production.readyState === "READY" &&
        production.meta?.sourceCommit === manifest.source_commit
      ) {
        completed = true;
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    assert.ok(
      completed,
      "Production promotion did not complete within 3 minutes",
    );
  }
  let productionUrl = null;
  if (mode === "production") {
    const details = api("/v13/deployments/" + new URL(deployment).host);
    const aliasEndpoint =
      "/v2/deployments/" + (details.id || details.uid) + "/aliases";
    const aliasDeadline = Date.now() + 60_000;
    let assigned = false;
    while (Date.now() < aliasDeadline) {
      const aliases = api(aliasEndpoint).aliases;
      if (aliases?.some((a) => a.alias === config.productionHostname)) {
        assigned = true;
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    assert.ok(assigned, "Configured production domain was not assigned");
    productionUrl = "https://" + config.productionHostname;
    execFileSync(process.execPath, [path.join(root, "site/verify.cjs")], {
      cwd: root,
      env: {
        ...env,
        HUB_URL: productionUrl,
        HUB_OUTPUT: path.join(root, ".runs/production"),
      },
      stdio: "inherit",
    });
    const unauthenticated = await fetch(productionUrl + "/site/catalog.json", {
      redirect: "manual",
    });
    assert.ok(
      [301, 302, 303, 307, 308, 401, 403].includes(unauthenticated.status),
      "Production domain exposed without authentication",
    );
  }
  fs.mkdirSync(path.join(root, ".runs/deployment"), { recursive: true });
  fs.writeFileSync(
    path.join(root, ".runs/deployment/result.json"),
    JSON.stringify(
      {
        mode,
        deployment,
        source_commit: manifest.source_commit,
        protected: true,
        productionUrl,
        promoted: mode === "production",
      },
      null,
      2,
    ) + "\n",
  );
  console.log(
    `${mode === "production" ? "Promoted" : "Verified preview"}: ${deployment}`,
  );
})()
  .catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  })
  .finally(() => {
    if (cliProfile) fs.rmSync(cliProfile, { recursive: true, force: true });
  });
