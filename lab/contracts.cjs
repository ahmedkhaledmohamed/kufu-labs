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
const MNE_DEFAULT = Object.freeze({
  sfreq: 512,
  sample: 1,
  origin: "relative",
});
function validateRecipe(recipe = "nwb") {
  if (!["nwb", "mne"].includes(recipe))
    throw new Error("Unknown experiment recipe.");
  return recipe;
}
function validateCases(cases, recipe = "nwb") {
  validateRecipe(recipe);
  if (!Array.isArray(cases) || cases.length < 1 || cases.length > 4)
    throw new Error("Choose 1–4 experiment cases.");
  const defaults = recipe === "mne" ? MNE_DEFAULT : DEFAULT;
  return cases.map((raw) => {
    if (
      !raw ||
      typeof raw !== "object" ||
      Object.keys(raw).sort().join() !== Object.keys(defaults).sort().join()
    )
      throw new Error("Unexpected experiment fields.");
    const value = { ...raw };
    if (recipe === "mne") {
      if (
        !Number.isInteger(value.sfreq) ||
        value.sfreq < 128 ||
        value.sfreq > 8192
      )
        throw new Error(
          "Sampling rate must be an integer between 128 and 8192 Hz.",
        );
      if (
        !Number.isInteger(value.sample) ||
        value.sample < 0 ||
        value.sample > 2 * value.sfreq
      )
        throw new Error(
          "Annotation sample must be between 0 and twice the sampling rate.",
        );
      if (!["relative", "utc"].includes(value.origin))
        throw new Error("Invalid annotation origin.");
      return value;
    }
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
function summarize(baseline, patched, recipe = "nwb") {
  validateRecipe(recipe);
  if (baseline.cases.length !== patched.cases.length)
    throw new Error("Mismatched comparison cases.");
  return baseline.cases.map((before, index) => {
    const after = patched.cases[index];
    if (JSON.stringify(before.input) !== JSON.stringify(after.input))
      throw new Error("Comparison inputs differ.");
    if (recipe === "mne") {
      if (
        before.input_sha256 !== after.input_sha256 ||
        JSON.stringify(before.reference) !== JSON.stringify(after.reference)
      )
        throw new Error("Generated MNE references differ.");
      const valid = [before, after].every(
        (run) =>
          run.input_sha256 === run.output_sha256 &&
          [
            "signal_unchanged",
            "input_annotation_unchanged",
            "rounded_index_matches_sample",
          ].every((key) => run.controls[key] === true),
      );
      const preserved = (run) =>
        run.attached.onset_seconds === run.reference.onset_seconds &&
        run.attached.duration_seconds === run.reference.duration_seconds;
      return {
        input: before.input,
        reference: before.reference,
        baseline: before.attached,
        patched: after.attached,
        controls: { baseline: before.controls, patched: after.controls },
        outcome: !valid
          ? "invalid-comparison"
          : preserved(after)
            ? preserved(before)
              ? "both-preserved"
              : "patch-preserved"
            : "patch-changed-data",
      };
    }
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
module.exports = {
  DEFAULT,
  MNE_DEFAULT,
  validateRecipe,
  validateCases,
  summarize,
  validId,
  hash,
};
