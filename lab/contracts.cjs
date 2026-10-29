const crypto = require("node:crypto");

const DEFAULT = Object.freeze({
  rows: 500,
  channels: 2,
  buffer: 100,
  seed: 42,
  pattern: "ramp",
  backend: "hdf5",
  iterator: "basic",
});
function validateCases(cases) {
  if (!Array.isArray(cases) || cases.length < 1 || cases.length > 4)
    throw new Error("Choose 1–4 experiment cases.");
  return cases.map((raw) => {
    if (
      !raw ||
      typeof raw !== "object" ||
      Object.keys(raw).sort().join() !== Object.keys(DEFAULT).sort().join()
    )
      throw new Error("Unexpected experiment fields.");
    const value = { ...raw };
    for (const [key, min, max] of [
      ["rows", 1, 2000],
      ["channels", 1, 8],
      ["buffer", 1, 500],
      ["seed", 0, 2147483647],
    ]) {
      if (!Number.isInteger(value[key]) || value[key] < min || value[key] > max)
        throw new Error(`${key} must be an integer between ${min} and ${max}.`);
    }
    for (const [key, allowed] of Object.entries({
      pattern: ["ramp", "random", "alternating"],
      backend: ["hdf5", "zarr"],
      iterator: ["basic", "generic"],
    }))
      if (!allowed.includes(value[key])) throw new Error(`Invalid ${key}.`);
    return value;
  });
}
function summarize(baseline, patched) {
  if (baseline.cases.length !== patched.cases.length)
    throw new Error("Mismatched comparison cases.");
  return baseline.cases.map((before, index) => {
    const after = patched.cases[index];
    if (JSON.stringify(before.input) !== JSON.stringify(after.input))
      throw new Error("Comparison inputs differ.");
    const runs = [
      before.control,
      before.inspected,
      after.control,
      after.inspected,
    ];
    if (new Set(runs.map((r) => r.input_sha256)).size !== 1)
      throw new Error("Generated arrays differ.");
    const valid =
      [before.control, after.control].every(
        (r) => r.values_equal && r.shape_equal && r.dtype_equal,
      ) && after.inspected.inspection_errors.length === 0;
    return {
      input: before.input,
      baseline: before.inspected,
      patched: after.inspected,
      controls: { baseline: before.control, patched: after.control },
      outcome: !valid
        ? "invalid-comparison"
        : after.inspected.values_equal &&
            after.inspected.shape_equal &&
            after.inspected.dtype_equal
          ? before.inspected.values_equal
            ? "both-preserved"
            : "patch-preserved"
          : "patch-changed-data",
    };
  });
}
const validId = (id) =>
  typeof id === "string" &&
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(
    id,
  );
const hash = (value) => crypto.createHash("sha256").update(value).digest("hex");
module.exports = { DEFAULT, validateCases, summarize, validId, hash };
