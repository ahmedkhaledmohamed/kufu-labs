const { QueueClient } = require("@vercel/queue");
const { validateRecipe, validateCases, validId } = require("./contracts.cjs");
const store = require("./store.cjs");
const queue = new QueueClient({ region: "iad1" });
const enabled = () =>
  process.env.KUFU_LAB_ENABLED === "1" &&
  Boolean(process.env.BLOB_STORE_ID || process.env.BLOB_READ_WRITE_TOKEN);
function json(res, code, value) {
  res.statusCode = code;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(value));
}
async function body(req) {
  // Vercel's Node launcher may have already parsed the JSON stream.
  if (req.body !== undefined) {
    const text =
      typeof req.body === "string" || Buffer.isBuffer(req.body)
        ? String(req.body)
        : JSON.stringify(req.body);
    if (Buffer.byteLength(text) > 8192)
      throw new Error("Request exceeds 8 KB.");
    return JSON.parse(text);
  }
  let text = "";
  for await (const chunk of req) {
    text += chunk;
    if (Buffer.byteLength(text) > 8192)
      throw new Error("Request exceeds 8 KB.");
  }
  return JSON.parse(text);
}
async function status(id) {
  const submission = await store.readJSON(id, "submission.json");
  if (!submission) return null;
  const result = await store.readJSON(id, "result.json");
  if (result)
    return {
      id,
      status: "completed",
      ...result,
      recipe: validateRecipe(submission.recipe),
      cases: submission.cases,
    };
  const failure = await store.readJSON(id, "error.json");
  if (failure)
    return {
      id,
      status: "failed",
      ...failure,
      recipe: validateRecipe(submission.recipe),
      cases: submission.cases,
    };
  const claim = await store.readJSON(id, "claim.json");
  const progress = (await store.readJSON(id, "progress.json")) || {
    created_at: submission.created_at,
    started_at: claim?.started_at || null,
    updated_at: claim?.started_at || submission.created_at,
    events: [
      {
        label: "Waiting for a worker",
        started_at: submission.created_at,
        ...(claim
          ? { finished_at: claim.started_at, outcome: "completed" }
          : { outcome: "active" }),
      },
      ...(claim
        ? [
            {
              label: "Starting worker",
              started_at: claim.started_at,
              outcome: "active",
            },
          ]
        : []),
    ],
  };
  const expired =
    Date.now() - Date.parse(claim?.started_at || submission.created_at) >
    (claim ? 360000 : 900000);
  return {
    id,
    status: expired ? "interrupted" : claim ? "running" : "queued",
    recipe: validateRecipe(submission.recipe),
    cases: submission.cases,
    created_at: submission.created_at,
    progress,
    message: expired
      ? "This run did not finish within its allowed time. Submit a new run to try again."
      : claim
        ? progress.events.at(-1).label + "."
        : "Waiting for a Vercel worker.",
  };
}
module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  try {
    const url = new URL(req.url, "https://lab.invalid");
    if (req.method === "GET" && !url.searchParams.has("id"))
      return json(res, 200, {
        enabled: enabled(),
        provider: "Vercel Sandbox",
        source_commit: store.build.commit,
        daily_limit: 10,
        max_cases: 4,
        recipes: ["nwb", "mne"],
      });
    if (!enabled())
      return json(res, 503, {
        error: "Hosted experiments are not enabled for this deployment yet.",
      });
    const id = url.searchParams.get("id");
    if (req.method === "GET") {
      if (!validId(id)) return json(res, 400, { error: "Invalid run ID." });
      if (url.searchParams.get("download") === "1") {
        const result = await store.readJSON(id, "result.json");
        if (!result)
          return json(res, 404, { error: "No completed result bundle." });
        const archive = await store.read(store.key(id, "results.zip"));
        if (!archive)
          return json(res, 404, { error: "Result bundle unavailable." });
        res.setHeader("Content-Type", "application/zip");
        res.setHeader(
          "Content-Disposition",
          `attachment; filename="kufu-${validateRecipe(result.recipe)}-${id}.zip"`,
        );
        return res.end(archive);
      }
      const value = await status(id);
      return json(
        res,
        value ? 200 : 404,
        value || { error: "Run not found in this deployment." },
      );
    }
    if (req.method !== "POST") {
      res.setHeader("Allow", "GET, POST");
      return json(res, 405, { error: "Method not allowed." });
    }
    // Deployment Authentication protects reads and writes. Reject cross-site writes too.
    const origin = req.headers.origin;
    if (
      req.headers["sec-fetch-site"] === "cross-site" ||
      !origin ||
      new URL(origin).host !== req.headers.host
    )
      return json(res, 403, {
        error: "Submit experiments from this lab's website.",
      });
    if (!req.headers["content-type"]?.startsWith("application/json"))
      return json(res, 415, { error: "Use application/json." });
    let submission;
    try {
      submission = await body(req);
      if (!validId(submission.id)) throw new Error("Invalid submission ID.");
      submission.recipe = validateRecipe(submission.recipe);
      submission.cases = validateCases(submission.cases, submission.recipe);
    } catch (error) {
      return json(res, 400, { error: error.message });
    }
    const previous = await store.readJSON(submission.id, "submission.json");
    if (
      previous &&
      (validateRecipe(previous.recipe) !== submission.recipe ||
        JSON.stringify(previous.cases) !== JSON.stringify(submission.cases))
    )
      return json(res, 409, {
        error: "That run ID belongs to different inputs.",
      });
    if (!previous) {
      if (!(await store.reserveDailySlot(submission.id)))
        return json(res, 429, {
          error:
            "The lab's limit of 10 submissions per UTC day has been reached.",
        });
      try {
        await store.writeJSON(submission.id, "submission.json", {
          recipe: submission.recipe,
          cases: submission.cases,
          created_at: new Date().toISOString(),
          source_commit: store.build.commit,
        });
      } catch (error) {
        if (!store.existsError(error)) throw error;
        const concurrent = await store.readJSON(
          submission.id,
          "submission.json",
        );
        if (
          !concurrent ||
          validateRecipe(concurrent.recipe) !== submission.recipe ||
          JSON.stringify(concurrent.cases) !== JSON.stringify(submission.cases)
        )
          return json(res, 409, {
            error: "That run ID belongs to different inputs.",
          });
      }
    }
    // A repeated submit can repair an interrupted publish; Queue deduplicates it.
    await queue.send(
      "kufu-nwb",
      { id: submission.id, source_commit: store.build.commit },
      { idempotencyKey: submission.id, retentionSeconds: 900 },
    );
    return json(res, 202, { id: submission.id, status: "queued" });
  } catch (error) {
    console.error("Lab API request failed", error.name);
    return json(res, 503, {
      error:
        "The execution service is unavailable. Your inputs are unchanged; retry shortly.",
    });
  }
};
