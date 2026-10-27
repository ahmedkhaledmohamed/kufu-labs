// Promote only the tested prebuilt static artifact, with verified owner/protection.
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
const api = (endpoint, method = "GET", data) =>
  JSON.parse(
    execFileSync(
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
    ),
  );
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
  assert.equal(web.pages, 5);
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
  // Production-target deployment is staged without a domain, then promoted only after verification.
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
  ]) {
    const response = await fetch(deployment + resource, { redirect: "manual" });
    assert.ok(
      [301, 302, 303, 307, 308, 401, 403].includes(response.status),
      "Unauthenticated content exposed",
    );
  }
  target();
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
    execFileSync(cli, ["promote", deployment, "--yes", ...cliContextArgs], {
      cwd: root,
      env,
      stdio: "inherit",
    });
  }
  let productionUrl = null;
  if (mode === "production") {
    const details = api("/v13/deployments/" + new URL(deployment).host);
    const aliases = api(
      "/v2/deployments/" + (details.id || details.uid) + "/aliases",
    ).aliases;
    assert.ok(aliases?.length, "Promotion did not assign a production domain");
    productionUrl = "https://" + aliases[0].alias;
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
