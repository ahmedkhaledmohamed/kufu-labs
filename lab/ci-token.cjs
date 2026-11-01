// Obtain short-lived GitHub OIDC proof in CI; never persist or print it.
const { POLICY } = require("./ci-policy.cjs");
let cached;
async function ciToken() {
  if (process.env.GITHUB_ACTIONS !== "true")
    throw new Error("Hosted verification requires GitHub Actions identity");
  if (cached && cached.expires > Date.now() + 30000) return cached.value;
  const url = new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);
  if (url.protocol !== "https:" || !process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN)
    throw new Error("CI identity token request is unavailable");
  url.searchParams.set("audience", POLICY.audience);
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN}`,
    },
    signal: AbortSignal.timeout(10000),
    redirect: "error",
  });
  if (!response.ok) throw new Error("Unable to obtain GitHub CI proof");
  const { value } = await response.json();
  if (typeof value !== "string" || value.length > 12000)
    throw new Error("Invalid CI proof response");
  const claims = JSON.parse(Buffer.from(value.split(".")[1], "base64url"));
  if (!Number.isFinite(claims.exp) || claims.exp * 1000 <= Date.now() + 30000)
    throw new Error("CI proof is already expiring");
  cached = { value, expires: claims.exp * 1000 };
  return value;
}
module.exports = { ciToken };
