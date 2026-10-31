// Real Auth.js session cryptography plus isolated API tests; no provider/compute calls.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const { Readable } = require("node:stream");
const auth = require("./auth.cjs");
const { DEFAULT } = require("./contracts.cjs");
const host = require("../site/deployment-config.json").productionHostname;
const req = (cookie = "") => ({ headers: { host, cookie } });
(async () => {
  const original = { ...process.env };
  try {
    for (const name of [
      "KUFU_VERCEL_CLIENT_ID",
      "KUFU_VERCEL_CLIENT_SECRET",
      "KUFU_AUTH_SECRET",
      "KUFU_OWNER_VERCEL_ID",
    ])
      delete process.env[name];
    assert.equal((await auth.access(req())).owner_override, false);
    Object.assign(process.env, {
      KUFU_VERCEL_CLIENT_ID: "test-client",
      KUFU_VERCEL_CLIENT_SECRET: "test-client-secret",
      KUFU_AUTH_SECRET: "test-session-secret-not-a-live-credential-0123456789",
      KUFU_OWNER_VERCEL_ID: "test-owner",
    });
    const configuredSecret = process.env.KUFU_AUTH_SECRET;
    process.env.KUFU_AUTH_SECRET = "too-short";
    assert.equal(auth.configured(), false);
    process.env.KUFU_AUTH_SECRET = configuredSecret;
    const { encode } = await import("@auth/core/jwt");
    const cookieName = "__Secure-authjs.session-token";
    async function cookie(
      subject,
      maxAge = 3600,
      secret = process.env.KUFU_AUTH_SECRET,
    ) {
      return `${cookieName}=${await encode({ token: { vercelSubject: subject }, secret, salt: cookieName, maxAge })}`;
    }
    const ownerCookie = await cookie("test-owner");
    assert.deepEqual(await auth.access(req(ownerCookie)), {
      sign_in_available: true,
      signed_in: true,
      owner_override: true,
    });
    assert.equal(
      (await auth.access(req(await cookie("other-user")))).owner_override,
      false,
    );
    assert.equal(
      (await auth.access(req(await cookie("test-owner", -3600))))
        .owner_override,
      false,
    );
    assert.equal(
      (await auth.access(req(await cookie("test-owner", 3600, "wrong-key"))))
        .owner_override,
      false,
    );
    assert.equal(
      (await auth.access(req(`${cookieName}=forged`))).owner_override,
      false,
    );
    assert.equal(
      (
        await auth.access({
          headers: { host: "attacker.example", cookie: ownerCookie },
        })
      ).owner_override,
      false,
    );
    const configuration = auth.config();
    assert.deepEqual(configuration.providers[0].checks, [
      "state",
      "pkce",
      "nonce",
    ]);
    assert.equal(
      configuration.providers[0].authorization.params.scope,
      "openid",
    );
    const token = configuration.callbacks.jwt({
      token: {},
      account: { provider: "vercel", providerAccountId: "test-owner" },
    });
    assert.equal(
      configuration.callbacks.session({ session: { expires: "test" }, token })
        .owner_override,
      true,
    );
    const otherProvider = configuration.callbacks.jwt({
      token: {},
      account: { provider: "other", providerAccountId: "test-owner" },
    });
    assert.equal(
      configuration.callbacks.session({
        session: { expires: "test" },
        token: otherProvider,
      }).owner_override,
      false,
    );
    const values = new Map();
    let reservations = 0;
    let sends = 0;
    const store = {
      build: { commit: "test" },
      readJSON: async (id) => values.get(id),
      reserveDailySlot: async () => {
        reservations++;
        return false;
      },
      writeJSON: async (id, name, value) => values.set(id, value),
    };
    const module = { exports: {} };
    vm.runInNewContext(fs.readFileSync(`${__dirname}/api.cjs`, "utf8"), {
      module,
      exports: module.exports,
      require: (name) =>
        name === "./store.cjs"
          ? store
          : name === "./auth.cjs"
            ? auth
            : name === "@vercel/queue"
              ? {
                  QueueClient: function () {
                    this.send = async () => sends++;
                  },
                }
              : require(name),
      process: { env: { KUFU_LAB_ENABLED: "1", BLOB_STORE_ID: "fixture" } },
      URL,
      Buffer,
      console,
    });
    async function call(cookieValue, data, headers = {}, method = "POST") {
      const request = Readable.from(data ? [JSON.stringify(data)] : []);
      Object.assign(request, {
        method,
        url: "/api/experiments",
        headers: {
          host,
          cookie: cookieValue,
          origin: `https://${host}`,
          "content-type": "application/json",
          ...headers,
        },
      });
      const response = {
        statusCode: 200,
        setHeader() {},
        end(text) {
          this.body = JSON.parse(text);
        },
      };
      await module.exports(request, response);
      return response;
    }
    const submission = {
      id: "12345678-1234-4123-8123-123456789abc",
      cases: [DEFAULT],
    };
    assert.equal((await call("", submission)).statusCode, 429);
    assert.equal(
      (await call(await cookie("other-user"), submission)).statusCode,
      429,
    );
    assert.equal(
      (
        await call(
          "",
          { ...submission, owner_override: true },
          { "x-vercel-user-id": "test-owner" },
        )
      ).statusCode,
      429,
    );
    assert.equal(sends, 0);
    const before = reservations;
    assert.equal(
      (
        await call(ownerCookie, {
          ...submission,
          cases: [{ ...DEFAULT, rows: 2001 }],
        })
      ).statusCode,
      400,
    );
    assert.equal(
      (await call(ownerCookie, submission, { origin: "https://other.example" }))
        .statusCode,
      403,
    );
    assert.equal((await call(ownerCookie, submission)).statusCode, 202);
    assert.equal(
      reservations,
      before,
      "Owner submissions must not consume the shared allowance",
    );
    assert.equal(values.get(submission.id).quota_policy, "owner-exempt");
    assert.equal((await call(ownerCookie, submission)).statusCode, 202);
    assert.equal(reservations, before, "Retries do not reserve a slot");
    assert.equal(sends, 2);
    const capability = await call(ownerCookie, null, {}, "GET");
    assert.equal(capability.body.daily_limit, null);
    assert.equal(capability.body.access.owner_override, true);
    assert.equal((await call("", null, {}, "GET")).body.daily_limit, 10);
    async function authRequest(url, method = "GET", headers = {}, body) {
      const request = Readable.from([]);
      if (body) request.body = body;
      Object.assign(request, { url, method, headers: { host, ...headers } });
      const response = {
        statusCode: 200,
        headers: {},
        setHeader(key, value) {
          this.headers[key] = value;
        },
        end(value) {
          this.body = String(value || "");
        },
      };
      await auth.handler(request, response);
      return response;
    }
    assert.equal((await authRequest("/api/auth/signin")).statusCode, 200);
    assert.equal(
      (await authRequest("https://other.example/api/auth/signin")).statusCode,
      503,
    );
    const bundledAuth = require("../dist-backend/functions/api/auth.func/index.cjs");
    const bundledReq = {
      method: "GET",
      url: "/api/auth/session",
      headers: { host, cookie: ownerCookie },
    };
    const bundledResponse = {
      statusCode: 200,
      headers: {},
      setHeader(key, value) {
        this.headers[key] = value;
      },
      end(value) {
        this.body = JSON.parse(String(value));
      },
    };
    await bundledAuth(bundledReq, bundledResponse);
    assert.equal(bundledResponse.statusCode, 200);
    assert.equal(bundledResponse.body.owner_override, true);
    await bundledAuth(
      { ...bundledReq, url: "/api/auth?__kufu_auth_path=session" },
      bundledResponse,
    );
    assert.equal(bundledResponse.body.owner_override, true);
    assert.ok(Array.isArray(bundledResponse.headers["Set-Cookie"]));
    const bundledApi = require("../dist-backend/functions/api/experiments.func/index.cjs");
    await bundledApi(
      { ...bundledReq, url: "/api/experiments" },
      bundledResponse,
    );
    assert.equal(bundledResponse.body.daily_limit, null);
    assert.equal(
      (
        await authRequest("/api/auth/signout", "POST", {
          origin: "https://other.example",
        })
      ).statusCode,
      403,
    );
    const signout = await authRequest("/api/auth/signout", "POST", {
      origin: `https://${host}`,
      "content-type": "application/x-www-form-urlencoded",
    });
    assert.match(signout.headers.location, /MissingCSRF/);
    const csrf = await authRequest("/api/auth/csrf", "GET", {
      cookie: ownerCookie,
    });
    const csrfCookie = csrf.headers["Set-Cookie"]
      .map((value) => value.split(";")[0])
      .join("; ");
    const signedOut = await authRequest(
      "/api/auth/signout",
      "POST",
      {
        origin: `https://${host}`,
        "content-type": "application/x-www-form-urlencoded",
        cookie: `${ownerCookie}; ${csrfCookie}`,
      },
      {
        csrfToken: JSON.parse(csrf.body).csrfToken,
        callbackUrl: `https://${host}/lab.html`,
      },
    );
    assert.equal(signedOut.statusCode, 302);
    assert.ok(
      signedOut.headers["Set-Cookie"].some(
        (value) =>
          value.startsWith(`${cookieName}=;`) && value.includes("Max-Age=0"),
      ),
    );

    console.log(
      "Verified real encrypted owner/non-owner/expired/forged sessions, host checks, quota exemption, spoof rejection, CSRF and unchanged per-run validation. No provider or compute calls.",
    );
  } finally {
    for (const key of Object.keys(process.env))
      if (!(key in original)) delete process.env[key];
    Object.assign(process.env, original);
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
