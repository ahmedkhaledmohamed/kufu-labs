// Real RSA signatures, local service doubles and no hosted scientific execution.
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const vm = require("node:vm");
const { POLICY, CI_LIMIT, verifyToken, ciAccess } = require("./ci.cjs");
const { DEFAULT } = require("./contracts.cjs");
const commit = "a".repeat(40);
(async () => {
  const { generateKeyPair, exportJWK, SignJWT, createLocalJWKSet } =
    await import("jose");
  const pair = await generateKeyPair("RS256");
  const publicKey = await exportJWK(pair.publicKey);
  const keySet = createLocalJWKSet({
    keys: [{ ...publicKey, kid: "fixture", alg: "RS256", use: "sig" }],
  });
  const now = Math.floor(Date.now() / 1000);
  const claims = {
    iss: POLICY.issuer,
    aud: POLICY.audience,
    sub: `${POLICY.subject}:environment:preview`,
    environment: "preview",
    repository: POLICY.repository,
    repository_id: POLICY.repositoryId,
    repository_owner_id: POLICY.ownerId,
    sha: commit,
    workflow_sha: commit,
    workflow_ref: `${POLICY.repository}/${POLICY.workflow}@refs/pull/42/merge`,
    ref: "refs/pull/42/merge",
    event_name: "pull_request",
    runner_environment: "github-hosted",
    run_id: "123456789",
    run_attempt: "1",
    iat: now,
    nbf: now - 1,
    exp: now + 300,
  };
  async function sign(changes = {}, key = pair.privateKey, typ = "JWT") {
    return new SignJWT({ ...claims, ...changes })
      .setProtectedHeader({ alg: "RS256", typ, kid: "fixture" })
      .sign(key);
  }
  const token = await sign();
  assert.deepEqual(
    await verifyToken(token, commit, "preview", keySet, async (number, sha) => {
      assert.equal(number, "42");
      assert.equal(sha, commit);
      return true;
    }),
    { run_id: claims.run_id, run_attempt: "1" },
  );
  let rejected = 0;
  for (const change of [
    { iss: "https://untrusted.invalid" },
    { aud: "other" },
    { aud: [POLICY.audience, "other"] },
    { sub: `repo:${POLICY.repository}:environment:preview` },
    { environment: "production" },
    { repository: "other/repo" },
    { repository_id: "0" },
    { repository_owner_id: "0" },
    { sha: "b".repeat(40) },
    { workflow_sha: "b".repeat(40) },
    {
      workflow_ref: `${POLICY.repository}/.github/workflows/other.yml@${claims.ref}`,
    },
    { event_name: "pull_request_target" },
    { runner_environment: "self-hosted" },
    { ref: "refs/heads/main" },
    { job_workflow_ref: "other/repo/workflow.yml@main" },
    { run_id: "" },
    { run_attempt: "0" },
    { exp: now - 30 },
    { nbf: now + 60 },
    { iat: now - 700, exp: now + 1 },
    { exp: now + 1000 },
    { iat: undefined },
  ]) {
    await assert.rejects(
      verifyToken(
        await sign(change),
        commit,
        "preview",
        keySet,
        async () => true,
      ),
    );
    rejected++;
  }
  await verifyToken(
    await sign({
      job_workflow_ref: claims.workflow_ref,
      job_workflow_sha: commit,
    }),
    commit,
    "preview",
    keySet,
    async () => true,
  );
  const symmetric = await new SignJWT(claims)
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .sign(crypto.randomBytes(32));
  await assert.rejects(verifyToken(symmetric, commit, "preview", keySet));
  const other = await generateKeyPair("RS256");
  await assert.rejects(
    verifyToken(await sign({}, other.privateKey), commit, "preview", keySet),
  );
  await assert.rejects(
    verifyToken(
      await sign({}, pair.privateKey, "other"),
      commit,
      "preview",
      keySet,
    ),
  );
  await assert.rejects(verifyToken(token, "b".repeat(40), "preview", keySet));
  await assert.rejects(verifyToken(token, commit, "production", keySet));
  await assert.rejects(
    verifyToken(token, commit, "preview", keySet, async () => false),
  );
  await assert.rejects(
    ciAccess({ headers: { "x-kufu-ci-token": [token] } }, commit, "preview"),
    { name: "CiIdentityError" },
  );
  assert.equal(
    await ciAccess(
      { headers: { "x-kufu-ci-verified": "true" } },
      commit,
      "preview",
    ),
    null,
  );
  const production = {
    environment: "production",
    sub: `${POLICY.subject}:environment:production`,
    ref: "refs/heads/main",
    event_name: "push",
    workflow_ref: `${POLICY.repository}/${POLICY.workflow}@refs/heads/main`,
  };
  await verifyToken(await sign(production), commit, "production", keySet);
  await verifyToken(
    await sign({ ...production, event_name: "workflow_dispatch" }),
    commit,
    "production",
    keySet,
  );
  await assert.rejects(
    verifyToken(
      await sign({ ...production, event_name: "pull_request" }),
      commit,
      "production",
      keySet,
    ),
  );
  const branch = {
    ref: "refs/heads/experiment",
    event_name: "workflow_dispatch",
    workflow_ref: `${POLICY.repository}/${POLICY.workflow}@refs/heads/experiment`,
  };
  await verifyToken(await sign(branch), commit, "preview", keySet);
  await assert.rejects(
    verifyToken(
      await sign({ ...branch, event_name: "push" }),
      commit,
      "preview",
      keySet,
    ),
  );

  const originalFetch = global.fetch;
  let pullReads = 0;
  try {
    global.fetch = async (url, options) => {
      pullReads++;
      assert.equal(
        url,
        `https://api.github.com/repos/${POLICY.repository}/pulls/42`,
      );
      assert.equal(options.redirect, "error");
      return new Response(
        JSON.stringify({
          state: "open",
          merge_commit_sha: commit,
          head: { repo: { id: 7 } },
          base: { repo: { id: Number(POLICY.repositoryId) } },
        }),
      );
    };
    await assert.rejects(verifyToken(token, commit, "preview", keySet));
    global.fetch = async () => {
      pullReads++;
      return new Response(
        JSON.stringify({
          state: "open",
          merge_commit_sha: commit,
          head: { repo: { id: Number(POLICY.repositoryId) } },
          base: { repo: { id: Number(POLICY.repositoryId) } },
        }),
      );
    };
    await verifyToken(token, commit, "preview", keySet);
    await verifyToken(token, commit, "preview", keySet);
    assert.equal(pullReads, 2, "Positive same-commit PR proof is cached");
  } finally {
    global.fetch = originalFetch;
  }

  // Exercise the actual store's atomic allocation across independent deployments.
  const blobs = new Map();
  function loadStore(environment) {
    const module = { exports: {} };
    vm.runInNewContext(fs.readFileSync(`${__dirname}/store.cjs`, "utf8"), {
      module,
      exports: module.exports,
      KUFU_SOURCE: { commit },
      process: { env: { VERCEL_ENV: environment } },
      Buffer,
      Response,
      require: (name) =>
        name === "@vercel/blob"
          ? {
              BlobPreconditionFailedError: class extends Error {},
              get: async () => null,
              put: async (key, data, options) => {
                assert.equal(options.allowOverwrite, false);
                if (blobs.has(key)) {
                  const error = new Error("exists");
                  error.name = "BlobAlreadyExistsError";
                  throw error;
                }
                blobs.set(key, data);
                return {};
              },
            }
          : require(name),
    });
    return module.exports;
  }
  const previewStore = loadStore("preview"),
    productionStore = loadStore("production");
  const allocated = await Promise.all(
    Array.from({ length: 35 }, (_, i) =>
      (i % 2 ? previewStore : productionStore).reserveDailySlot(
        crypto.randomUUID(),
        "ci",
      ),
    ),
  );
  assert.equal(allocated.filter(Boolean).length, CI_LIMIT);
  assert.equal(blobs.size, 20);
  assert.ok(
    [...blobs.keys()].every((key) =>
      /^kufu-lab\/ci-budget\/\d{4}-\d\d-\d\d\/\d+\.json$/.test(key),
    ),
  );
  const ordinary = await Promise.all(
    Array.from({ length: 15 }, () =>
      previewStore.reserveDailySlot(crypto.randomUUID()),
    ),
  );
  assert.equal(ordinary.filter(Boolean).length, 10);
  assert.equal(blobs.size, 30);
  await assert.rejects(
    previewStore.reserveDailySlot(crypto.randomUUID(), "owner"),
  );

  // Real signed CI proof reaches the API's CI bucket, never a caller-supplied flag.
  const submissions = new Map(),
    reservations = [];
  let ciAvailable = true,
    sent = 0;
  const store = {
    build: { commit },
    readJSON: async (id, name) =>
      name === "submission.json" ? submissions.get(id) : null,
    reserveDailySlot: async (id, pool) => {
      reservations.push(pool);
      return pool === "ci" ? ciAvailable : false;
    },
    writeJSON: async (id, name, value) => submissions.set(id, value),
    existsError: () => false,
  };
  const module = { exports: {} };
  vm.runInNewContext(fs.readFileSync(`${__dirname}/api.cjs`, "utf8"), {
    module,
    exports: module.exports,
    URL,
    Buffer,
    console,
    process: {
      env: {
        VERCEL_ENV: "preview",
        KUFU_LAB_ENABLED: "1",
        BLOB_STORE_ID: "fixture",
      },
    },
    require: (name) =>
      name === "./store.cjs"
        ? store
        : name === "./auth.cjs"
          ? {
              access: async () => ({ owner_override: false }),
            }
          : name === "./ci.cjs"
            ? {
                CI_LIMIT,
                ciAccess: async (req) => {
                  if (req.headers["x-kufu-ci-token"] === undefined) return null;
                  try {
                    return await verifyToken(
                      req.headers["x-kufu-ci-token"],
                      commit,
                      "preview",
                      keySet,
                      async () => true,
                    );
                  } catch {
                    const error = new Error("Invalid CI proof");
                    error.name = "CiIdentityError";
                    throw error;
                  }
                },
              }
            : name === "@vercel/queue"
              ? {
                  QueueClient: function () {
                    this.send = async () => sent++;
                  },
                }
              : require(name),
  });
  async function call(
    method,
    proof,
    id = crypto.randomUUID(),
    extra = {},
    url = "/api/experiments",
  ) {
    const req = {
      method,
      url,
      body: { id, cases: [DEFAULT], ci_verified: true },
      headers: {
        host: "lab.test",
        origin: "https://lab.test",
        "content-type": "application/json",
        ...extra,
        ...(proof ? { "x-kufu-ci-token": proof } : {}),
      },
    };
    const res = {
      setHeader() {},
      end(value) {
        this.body = JSON.parse(value);
      },
    };
    await module.exports(req, res);
    return res;
  }
  assert.equal((await call("GET", token)).body.daily_limit, 20);
  assert.equal((await call("GET")).body.daily_limit, 10);
  const id = crypto.randomUUID();
  assert.equal((await call("POST", token, id)).statusCode, 202);
  assert.equal(submissions.get(id).quota_policy, "ci-daily");
  assert.equal(submissions.get(id).ci_identity.run_id, claims.run_id);
  const status = await call("GET", token, id, {}, `/api/experiments?id=${id}`);
  assert.equal(status.body.quota_policy, "ci-daily");
  assert.equal(status.body.ci_identity.run_id, claims.run_id);

  assert.equal((await call("POST", token, id)).statusCode, 202);
  assert.deepEqual(reservations, ["ci"]);
  ciAvailable = false;
  assert.equal((await call("POST", token)).statusCode, 429);
  assert.deepEqual(reservations, ["ci", "ci"]);
  const before = reservations.length;
  assert.equal((await call("POST", "forged")).statusCode, 403);
  assert.equal(reservations.length, before);
  assert.equal(
    (
      await call("POST", token, crypto.randomUUID(), {
        origin: "https://other.test",
      })
    ).statusCode,
    403,
  );
  assert.equal(reservations.length, before);
  assert.equal(
    (
      await call("POST", undefined, crypto.randomUUID(), {
        "x-kufu-ci-verified": "true",
      })
    ).statusCode,
    429,
  );
  assert.equal(reservations.at(-1), "daily");
  assert.equal(
    sent,
    2,
    "Retries keep the existing queue behavior without a new reservation",
  );

  // The CI client refreshes expiring proof without persisting it or using a long-lived secret.
  let clock = Date.now(),
    fetched = 0;
  const client = { exports: {} };
  vm.runInNewContext(fs.readFileSync(`${__dirname}/ci-token.cjs`, "utf8"), {
    module: client,
    exports: client.exports,
    require,
    URL,
    Buffer,
    AbortSignal,
    Date: { now: () => clock },
    process: {
      env: {
        GITHUB_ACTIONS: "true",
        ACTIONS_ID_TOKEN_REQUEST_URL:
          "https://tokens.actions.githubusercontent.com/identity",
        ACTIONS_ID_TOKEN_REQUEST_TOKEN: "fixture-only",
      },
    },
    fetch: async (url, options) => {
      fetched++;
      assert.equal(url.searchParams.get("audience"), POLICY.audience);
      assert.equal(options.headers.Authorization, "Bearer fixture-only");
      const value = `header.${Buffer.from(JSON.stringify({ exp: Math.floor(clock / 1000) + 300 })).toString("base64url")}.signature`;
      return { ok: true, json: async () => ({ value }) };
    },
  });
  const first = await client.exports.ciToken();
  assert.equal(await client.exports.ciToken(), first);
  assert.equal(fetched, 1);
  clock += 280000;
  assert.notEqual(await client.exports.ciToken(), first);
  assert.equal(fetched, 2);
  // Exercise the actual bundled Function, including its fixed remote-key resolver.
  const bundleCommit = JSON.parse(
    fs.readFileSync(`${__dirname}/../dist/build-info.json`),
  ).source_commit;
  const savedEnvironment = Object.fromEntries(
    ["VERCEL_ENV", "KUFU_LAB_ENABLED", "BLOB_STORE_ID"].map((name) => [
      name,
      process.env[name],
    ]),
  );
  const bundledProof = await sign({
    sha: bundleCommit,
    workflow_sha: bundleCommit,
  });
  try {
    process.env.VERCEL_ENV = "preview";
    process.env.KUFU_LAB_ENABLED = "1";
    process.env.BLOB_STORE_ID = "fixture";
    global.fetch = async (url) => {
      if (String(url) === `${POLICY.issuer}/.well-known/jwks`) {
        return new Response(
          JSON.stringify({
            keys: [{ ...publicKey, kid: "fixture", alg: "RS256", use: "sig" }],
          }),
        );
      }
      assert.equal(
        String(url),
        `https://api.github.com/repos/${POLICY.repository}/pulls/42`,
      );
      return new Response(
        JSON.stringify({
          state: "open",
          merge_commit_sha: bundleCommit,
          head: { repo: { id: Number(POLICY.repositoryId) } },
          base: { repo: { id: Number(POLICY.repositoryId) } },
        }),
      );
    };
    const bundledApi = require("../dist-backend/functions/api/experiments.func/index.cjs");
    async function capability(proof) {
      const req = {
        method: "GET",
        url: "/api/experiments",
        headers: {
          host: "lab.test",
          ...(proof ? { "x-kufu-ci-token": proof } : {}),
        },
      };
      const response = {
        statusCode: 200,
        setHeader() {},
        end(value) {
          this.body = JSON.parse(value);
        },
      };
      await bundledApi(req, response);
      return response;
    }
    const verified = await capability(bundledProof);
    assert.equal(verified.statusCode, 200);
    assert.equal(verified.body.ci_verified, true);
    assert.equal(verified.body.daily_limit, 20);
    assert.equal((await capability()).body.daily_limit, 10);
    const invalid = await capability(
      await sign({ sha: "b".repeat(40), workflow_sha: "b".repeat(40) }),
    );
    assert.equal(invalid.statusCode, 403);
    assert.equal(invalid.body.ci_error, "claim-commit");
  } finally {
    global.fetch = originalFetch;
    for (const [name, value] of Object.entries(savedEnvironment)) {
      if (value === undefined) delete process.env[name];
      else process.env[name] = value;
    }
  }
  console.log(
    JSON.stringify({
      passed: true,
      signed_claim_mutations_rejected: rejected,
      concurrent_ci_slots: 20,
      ordinary_slots: 10,
      fork_rejected: true,
      api_policy_and_retry_verified: true,
      client_refresh_verified: true,
      bundled_function_verified: true,
    }),
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
