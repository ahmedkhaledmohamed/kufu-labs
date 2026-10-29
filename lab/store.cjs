const { put, get, BlobPreconditionFailedError } = require("@vercel/blob");
const { validId } = require("./contracts.cjs");
const build = KUFU_SOURCE;
const namespace = () =>
  process.env.VERCEL_ENV === "production"
    ? "production"
    : `preview-${build.commit}`;
const key = (id, name) => {
  if (!validId(id) || !/^[a-z.-]+$/.test(name))
    throw new Error("Invalid run path");
  return `kufu-lab/${namespace()}/runs/${id}/${name}`;
};
async function read(path) {
  const result = await get(path, { access: "private", useCache: false });
  if (!result || result.statusCode !== 200) return null;
  return Buffer.from(await new Response(result.stream).arrayBuffer());
}
async function readJSON(id, name) {
  const buffer = await read(key(id, name));
  return buffer ? JSON.parse(buffer.toString("utf8")) : null;
}
async function write(path, data, contentType = "application/json") {
  return put(path, data, {
    access: "private",
    addRandomSuffix: false,
    allowOverwrite: false,
    contentType,
  });
}
async function writeJSON(id, name, value) {
  return write(key(id, name), JSON.stringify(value));
}
async function writeProgress(id, value) {
  // The immutable run claim guarantees one writer. Only this live snapshot
  // is replaceable; submissions, claims and final results remain immutable.
  return put(key(id, "progress.json"), JSON.stringify(value), {
    access: "private",
    addRandomSuffix: false,
    allowOverwrite: true,
    contentType: "application/json",
    cacheControlMaxAge: 60,
  });
}
async function reserveDailySlot(id) {
  const date = new Date().toISOString().slice(0, 10);
  for (let slot = 0; slot < 10; slot++) {
    try {
      await write(
        `kufu-lab/budget/${date}/${slot}.json`,
        JSON.stringify({ id }),
      );
      return true;
    } catch (error) {
      if (
        !(error instanceof BlobPreconditionFailedError) &&
        error.name !== "BlobAlreadyExistsError" &&
        !/already exists/i.test(error.message)
      )
        throw error;
    }
  }
  return false;
}
const existsError = (error) =>
  error instanceof BlobPreconditionFailedError ||
  error.name === "BlobAlreadyExistsError" ||
  /already exists/i.test(error.message);
module.exports = {
  key,
  read,
  readJSON,
  write,
  writeJSON,
  writeProgress,
  reserveDailySlot,
  existsError,
  build,
};
