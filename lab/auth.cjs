// Vercel proves identity through OIDC; Auth.js owns OAuth checks and session crypto.
const productionHost =
  require("../site/deployment-config.json").productionHostname;
const configured = () =>
  [
    "KUFU_VERCEL_CLIENT_ID",
    "KUFU_VERCEL_CLIENT_SECRET",
    "KUFU_AUTH_SECRET",
    "KUFU_OWNER_VERCEL_ID",
  ].every((key) => Boolean(process.env[key])) &&
  Buffer.byteLength(process.env.KUFU_AUTH_SECRET || "") >= 32;
const anonymous = {
  sign_in_available: false,
  signed_in: false,
  owner_override: false,
};
function origin(req) {
  const hosts = [
    productionHost,
    process.env.VERCEL_URL,
    process.env.VERCEL_BRANCH_URL,
  ].filter(Boolean);
  if (!hosts.includes(req.headers.host))
    throw new Error("Unrecognized authentication host");
  return `https://${req.headers.host}`;
}
function config() {
  return {
    secret: process.env.KUFU_AUTH_SECRET,
    basePath: "/api/auth",
    trustHost: true, // origin() restricts hosts before creating the Auth.js Request.
    useSecureCookies: true,
    session: { strategy: "jwt", maxAge: 3600 },
    providers: [
      {
        id: "vercel",
        name: "Vercel",
        type: "oidc",
        issuer: "https://vercel.com",
        wellKnown: "https://vercel.com/.well-known/openid-configuration",
        clientId: process.env.KUFU_VERCEL_CLIENT_ID,
        clientSecret: process.env.KUFU_VERCEL_CLIENT_SECRET,
        client: { token_endpoint_auth_method: "client_secret_basic" },
        authorization: { params: { scope: "openid" } },
        checks: ["state", "pkce", "nonce"],
        profile: (profile) => ({ id: profile.sub }),
      },
    ],
    callbacks: {
      jwt({ token, account }) {
        if (account)
          token.vercelSubject =
            account.provider === "vercel"
              ? account.providerAccountId
              : undefined;
        return token;
      },
      session({ session, token }) {
        return {
          expires: session.expires,
          signed_in: typeof token.vercelSubject === "string",
          owner_override:
            typeof token.vercelSubject === "string" &&
            token.vercelSubject === process.env.KUFU_OWNER_VERCEL_ID,
        };
      },
    },
    logger: {
      // Never print cookies, tokens, callback parameters or provider response data.
      error(error) {
        console.error("Lab sign-in failed", error.type || error.name);
      },
      warn(code) {
        console.warn("Lab sign-in warning", code);
      },
    },
  };
}
async function access(req) {
  if (!configured()) return { ...anonymous };
  try {
    const { Auth } = await import("@auth/core");
    const response = await Auth(
      new Request(`${origin(req)}/api/auth/session`, {
        headers: { cookie: req.headers.cookie || "" },
      }),
      config(),
    );
    if (!response.ok) throw new Error("Session unavailable");
    const session = await response.json();
    return {
      sign_in_available: true,
      signed_in: session?.signed_in === true,
      owner_override: session?.owner_override === true,
    };
  } catch {
    // An invalid/expired/unreadable session never confers owner privileges.
    return { ...anonymous, sign_in_available: true };
  }
}
async function handler(req, res) {
  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  if (!configured()) {
    res.statusCode = 503;
    return res.end("Owner sign-in is not configured.");
  }
  try {
    if (!["GET", "POST"].includes(req.method)) {
      res.statusCode = 405;
      res.setHeader("Allow", "GET, POST");
      return res.end();
    }
    const base = origin(req);
    if (
      req.method === "POST" &&
      (req.headers.origin !== base ||
        req.headers["sec-fetch-site"] === "cross-site")
    ) {
      res.statusCode = 403;
      return res.end("Use the lab's sign-in page.");
    }
    const url = new URL(req.url, base);
    // Support launchers that expose the rewritten URL instead of the original.
    if (url.pathname === "/api/auth") {
      const action = url.searchParams.get("__kufu_auth_path");
      if (action) url.pathname += `/${action}`;
    }
    url.searchParams.delete("__kufu_auth_path");
    if (url.origin !== base)
      throw new Error("Unrecognized authentication origin");
    if (
      !/^\/api\/auth\/(signin|signout|callback|session|csrf|providers|error)(\/vercel)?$/.test(
        url.pathname,
      )
    ) {
      res.statusCode = 404;
      return res.end();
    }
    const headers = new Headers();
    for (const key of ["cookie", "content-type"])
      if (typeof req.headers[key] === "string")
        headers.set(key, req.headers[key]);
    const options = { method: req.method, headers };
    if (req.method === "POST") {
      if (
        !req.headers["content-type"]?.startsWith(
          "application/x-www-form-urlencoded",
        )
      ) {
        res.statusCode = 415;
        return res.end();
      }
      let body = "";
      if (req.body !== undefined)
        body =
          typeof req.body === "string" || Buffer.isBuffer(req.body)
            ? String(req.body)
            : new URLSearchParams(req.body).toString();
      else
        for await (const chunk of req) {
          body += chunk;
          if (Buffer.byteLength(body) > 8192)
            throw new Error("Sign-in request too large");
        }
      if (Buffer.byteLength(body) > 8192)
        throw new Error("Sign-in request too large");
      options.body = body;
    }
    const { Auth } = await import("@auth/core");
    const response = await Auth(new Request(url, options), config());
    res.statusCode = response.status;
    for (const [key, value] of response.headers)
      if (key !== "set-cookie") res.setHeader(key, value);
    const cookies = response.headers.getSetCookie();
    if (cookies.length) res.setHeader("Set-Cookie", cookies);
    res.end(Buffer.from(await response.arrayBuffer()));
  } catch {
    res.statusCode = 503;
    res.end(
      "Sign-in is unavailable. Return to the Execution lab and try again.",
    );
  }
}
module.exports = { access, handler, configured, config };
