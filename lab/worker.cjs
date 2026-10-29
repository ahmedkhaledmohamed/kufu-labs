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
  const startedAt = new Date().toISOString();
  try {
    await store.writeJSON(id, "claim.json", {
      started_at: startedAt,
    });
  } catch (error) {
    if (store.existsError(error)) return;
    throw error;
  }
  const progress = {
    created_at: submission.created_at,
    started_at: startedAt,
    updated_at: startedAt,
    events: [
      {
        label: "Waiting for a worker",
        started_at: submission.created_at,
        finished_at: startedAt,
        outcome: "completed",
      },
    ],
  };
  async function report(phase) {
    const now = new Date().toISOString();
    const previous = progress.events.at(-1);
    if (previous.outcome === "active") {
      previous.finished_at = now;
      previous.outcome = "completed";
    }
    progress.events.push({ label: phase, started_at: now, outcome: "active" });
    progress.updated_at = now;
    await store.writeProgress(id, progress);
    console.log("Lab phase", id, phase);
  }
  function finish(outcome) {
    const now = new Date().toISOString();
    const current = progress.events.at(-1);
    current.finished_at = now;
    current.outcome = outcome;
    progress.updated_at = now;
    progress.finished_at = now;
  }
  try {
    await report("Starting experiment");
    const result = await execute(submission.cases, report);
    await report("Saving result bundle");
    await store.write(
      store.key(id, "results.zip"),
      result.archive,
      "application/zip",
    );
    finish("completed");
    await store.writeJSON(id, "result.json", {
      ...result.record,
      source_commit: store.build.commit,
      logs: result.logs,
      finished_at: progress.finished_at,
      progress,
    });
  } catch (error) {
    console.error("NWB run failed", id, error.name);
    finish("failed");
    await store.writeJSON(id, "error.json", {
      message:
        "The experiment could not complete. See the execution logs; no scientific result is claimed.",
      logs: error.labLogs || [],
      finished_at: progress.finished_at,
      progress,
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
