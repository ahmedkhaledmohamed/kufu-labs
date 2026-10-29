const { QueueClient } = require("@vercel/queue");
const { execute } = require("./run.cjs");
const { validId } = require("./contracts.cjs");
const store = require("./store.cjs");
const queue = new QueueClient({ region: "iad1" });
async function processRun(message) {
  if (
    process.env.KUFU_LAB_ENABLED !== "1" ||
    !validId(message.id) ||
    message.source_commit !== store.build.commit
  )
    return;
  const { id } = message;
  const submission = await store.readJSON(id, "submission.json");
  if (!submission || Date.now() - Date.parse(submission.created_at) > 900000)
    return;
  // Atomic immutable claim prevents duplicate delivery from launching more VMs.
  try {
    await store.writeJSON(id, "claim.json", {
      started_at: new Date().toISOString(),
    });
  } catch (error) {
    if (store.existsError(error)) return;
    throw error;
  }
  try {
    const result = await execute(submission.cases, async (phase) =>
      console.log("Lab phase", id, phase),
    );
    await store.write(
      store.key(id, "results.zip"),
      result.archive,
      "application/zip",
    );
    await store.writeJSON(id, "result.json", {
      ...result.record,
      source_commit: store.build.commit,
      logs: result.logs,
      finished_at: new Date().toISOString(),
    });
  } catch (error) {
    console.error("NWB run failed", id, error.name);
    await store.writeJSON(id, "error.json", {
      message:
        "The experiment could not complete. See the execution logs; no scientific result is claimed.",
      logs: error.labLogs || [],
      finished_at: new Date().toISOString(),
    });
  }
}
const callback = queue.handleNodeCallback(processRun, {
  visibilityTimeoutSeconds: 300,
  retry: (_error, metadata) =>
    metadata.deliveryCount >= 2 ? { acknowledge: true } : { afterSeconds: 15 },
});
module.exports = callback;
module.exports.processRun = processRun;
