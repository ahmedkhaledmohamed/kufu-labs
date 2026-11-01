// Only the reviewed delivery workflow can use the bounded CI experiment pool.
const { POLICY, CI_LIMIT } = require("./ci-policy.cjs");
let keys;
const pullRequests = new Map();
async function sameRepositoryPullRequest(number, commit) {
  const key = `${number}:${commit}`;
  if ((pullRequests.get(key) || 0) > Date.now()) return true;
  const response = await fetch(
    `https://api.github.com/repos/${POLICY.repository}/pulls/${number}`,
    {
      headers: { Accept: "application/vnd.github+json" },
      signal: AbortSignal.timeout(5000),
      redirect: "error",
    },
  );
  if (!response.ok) return false;
  const value = await response.json();
  const valid =
    value.state === "open" &&
    String(value.head?.repo?.id) === POLICY.repositoryId &&
    String(value.base?.repo?.id) === POLICY.repositoryId &&
    value.merge_commit_sha === commit;
  if (valid) {
    if (pullRequests.size >= 64) pullRequests.clear();
    pullRequests.set(key, Date.now() + 60000);
  }
  return valid;
}
async function verifyToken(
  token,
  commit,
  environment,
  keySet,
  checkPullRequest = sameRepositoryPullRequest,
) {
  if (
    typeof token !== "string" ||
    token.length > 12000 ||
    !/^[0-9a-f]{40}$/.test(commit) ||
    !["preview", "production"].includes(environment)
  )
    throw new Error("Invalid CI proof");
  const { jwtVerify, createRemoteJWKSet } = await import("jose");
  if (!keySet) {
    keys ||= createRemoteJWKSet(new URL(`${POLICY.issuer}/.well-known/jwks`), {
      timeoutDuration: 5000,
    });
    keySet = keys;
  }
  const { payload } = await jwtVerify(token, keySet, {
    issuer: POLICY.issuer,
    audience: POLICY.audience,
    algorithms: ["RS256"],
    typ: "JWT",
    maxTokenAge: 600,
    clockTolerance: 5,
    requiredClaims: [
      "sub",
      "iat",
      "nbf",
      "exp",
      "sha",
      "workflow_sha",
      "workflow_ref",
      "repository_id",
      "repository_owner_id",
      "repository",
      "ref",
      "event_name",
      "run_id",
      "run_attempt",
      "runner_environment",
    ],
  });
  const checks = {
    audience: payload.aud === POLICY.audience,
    repository:
      payload.repository === POLICY.repository &&
      payload.repository_id === POLICY.repositoryId,
    owner: payload.repository_owner_id === POLICY.ownerId,
    subject: payload.sub === `${POLICY.subject}:environment:${environment}`,
    environment: payload.environment === environment,
    commit: payload.sha === commit && payload.workflow_sha === commit,
    workflow:
      payload.workflow_ref ===
      `${POLICY.repository}/${POLICY.workflow}@${payload.ref}`,
    callee:
      (!payload.job_workflow_ref && !payload.job_workflow_sha) ||
      (payload.job_workflow_ref === payload.workflow_ref &&
        payload.job_workflow_sha === commit),
    runner: payload.runner_environment === "github-hosted",
    run:
      typeof payload.run_id === "string" &&
      /^[1-9][0-9]{0,19}$/.test(payload.run_id) &&
      typeof payload.run_attempt === "string" &&
      /^[1-9][0-9]{0,5}$/.test(payload.run_attempt),
    lifetime: payload.exp > payload.iat && payload.exp - payload.iat <= 600,
  };
  const failed = Object.keys(checks).find((name) => !checks[name]);
  if (failed) {
    const error = new Error("CI claims do not match this deployment");
    error.ciReason = `claim-${failed}`;
    throw error;
  }
  if (environment === "production") {
    if (
      payload.ref !== "refs/heads/main" ||
      !["push", "workflow_dispatch"].includes(payload.event_name)
    )
      throw new Error("Invalid production CI ref");
  } else if (payload.event_name === "pull_request") {
    const match = /^refs\/pull\/([1-9][0-9]*)\/merge$/.exec(payload.ref);
    if (!match || !(await checkPullRequest(match[1], commit)))
      throw new Error("Untrusted pull request");
  } else if (
    payload.event_name !== "workflow_dispatch" ||
    !/^refs\/heads\/.+/.test(payload.ref) ||
    payload.ref === "refs/heads/main"
  ) {
    throw new Error("Invalid preview CI ref");
  }
  return { run_id: payload.run_id, run_attempt: payload.run_attempt };
}
async function ciAccess(req, commit, environment) {
  const token = req.headers["x-kufu-ci-token"];
  if (token === undefined) return null;
  try {
    return await verifyToken(token, commit, environment);
  } catch (cause) {
    const error = new Error(
      "CI proof could not be verified for this deployment.",
    );
    error.name = "CiIdentityError";
    // Only bounded categories leave this boundary, never token values.
    error.reason =
      /^claim-(audience|repository|owner|subject|environment|commit|workflow|callee|runner|run|lifetime)$/.test(
        cause.ciReason,
      )
        ? cause.ciReason
        : "token-or-ref-verification";
    throw error;
  }
}
module.exports = { POLICY, CI_LIMIT, verifyToken, ciAccess };
