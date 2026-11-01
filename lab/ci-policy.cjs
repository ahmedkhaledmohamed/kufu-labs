const POLICY = Object.freeze({
  issuer: "https://token.actions.githubusercontent.com",
  audience: "https://kufu-labs.vercel.app/ci/experiments",
  repository: "ahmedkhaledmohamed/kufu-labs",
  repositoryId: "1435078504",
  ownerId: "1297561",
  subject: "repo:ahmedkhaledmohamed@1297561/kufu-labs@1435078504",
  workflow: ".github/workflows/lab-delivery.yml",
});
const CI_LIMIT = 20;
module.exports = { POLICY, CI_LIMIT };
