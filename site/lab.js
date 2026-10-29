/* This page submits jobs; scientific calculations run only in Vercel Sandbox. */
(() => {
  const form = document.querySelector("#experimentForm");
  if (!form) return;
  const run = document.querySelector("#runExperiment");
  const availability = document.querySelector("#labAvailability");
  const status = document.querySelector("#runStatus");
  const results = document.querySelector("#runResults");
  const download = document.querySelector("#downloadRun");
  let ready = false;
  let busy = false;
  let timer;
  let pendingSubmission;
  const progressPanel = document.querySelector("#runProgress");
  const progressSummary = document.querySelector("#progressSummary");
  const timeline = document.querySelector("#runTimeline");
  let progressData;
  let progressReadError = false;
  let phaseTimings = [];
  const duration = (milliseconds) => {
    const seconds = Math.max(0, Math.floor(milliseconds / 1000));
    return seconds < 60
      ? `${seconds}s`
      : `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  };
  function updateTimings() {
    if (!progressData?.progress) return;
    const progress = progressData.progress;
    const terminal = ["completed", "failed", "interrupted"].includes(
      progressData.status,
    );
    const stoppedUpdating = progressReadError || terminal;
    const end =
      progress.finished_at || (stoppedUpdating ? progress.updated_at : null);
    const now = end ? Date.parse(end) : Date.now();
    const elapsed = duration(now - Date.parse(progress.created_at));
    document.querySelector("#runElapsed").textContent =
      `${progress.finished_at ? "Total recorded time" : stoppedUpdating ? "Time recorded before updates stopped" : "Elapsed since submission"}: ${elapsed}. Last update: ${new Date(progress.updated_at).toLocaleTimeString()}.`;
    for (const { event, node } of phaseTimings)
      node.textContent = duration(
        (event.finished_at ? Date.parse(event.finished_at) : now) -
          Date.parse(event.started_at),
      );
  }
  function renderProgress(data) {
    progressData = data;
    progressReadError = false;
    progressPanel.hidden = false;
    timeline.replaceChildren();
    phaseTimings = [];
    if (!data.progress?.events?.length) {
      progressSummary.textContent =
        "Stage history is unavailable for this older run.";
      document.querySelector("#runElapsed").textContent = "";
      return;
    }
    const terminal = ["completed", "failed", "interrupted"].includes(
      data.status,
    );
    progressSummary.textContent = terminal
      ? `Experiment ${data.status}.`
      : data.progress.events.at(-1).label;
    for (const event of data.progress.events) {
      const outcome =
        event.outcome === "active" && terminal ? data.status : event.outcome;
      const item = document.createElement("li");
      item.className = `phase-${outcome}`;
      if (outcome === "active") item.setAttribute("aria-current", "step");
      const label = document.createElement("span");
      label.textContent = event.label;
      const state = document.createElement("strong");
      state.className = "phase-state";
      state.textContent =
        data.status === "queued" && outcome === "active"
          ? "Waiting"
          : {
              completed: "Completed",
              active: "Running",
              failed: "Failed",
              interrupted: "Interrupted",
            }[outcome] || outcome;
      const time = document.createElement("span");
      time.className = "phase-time";
      item.append(label, state, time);
      timeline.append(item);
      phaseTimings.push({ event, node: time });
    }
    updateTimings();
  }
  setInterval(updateTimings, 1000);
  const inputs = () => {
    const data = Object.fromEntries(new FormData(form));
    const value = Object.fromEntries(
      Object.entries(data)
        .filter(([key]) => key !== "batch")
        .map(([key, value]) => [
          key,
          ["rows", "channels", "buffer", "seed"].includes(key)
            ? Number(value)
            : value,
        ]),
    );
    if (data.batch !== "boundary") return [value];
    return [
      ...new Set([
        Math.max(1, value.buffer - 1),
        value.buffer,
        value.buffer + 1,
        Math.min(2000, value.buffer * 3 + 1),
      ]),
    ].map((rows) => ({ ...value, rows }));
  };
  function preview() {
    document.querySelector("#inputPlan").textContent = JSON.stringify(
      inputs(),
      null,
      2,
    );
  }
  function cell(row, value, tag = "td") {
    const node = document.createElement(tag);
    node.textContent = String(value);
    row.append(node);
  }
  function render(data) {
    results.replaceChildren();
    for (const [index, comparison] of (data.comparisons || []).entries()) {
      const heading = document.createElement("h3");
      heading.textContent = `Case ${index + 1}: ${comparison.input.rows} rows × ${comparison.input.channels} channels · ${comparison.input.backend}`;
      const conclusion = document.createElement("p");
      conclusion.textContent = {
        "patch-preserved":
          "The baseline changed saved data; the patch preserved every value, shape and dtype. Both uninspected controls preserved the input.",
        "both-preserved":
          "Both revisions preserved this input. This case does not demonstrate a baseline failure.",
        "patch-changed-data":
          "The patched run changed saved data. This input reveals a remaining failure.",
        "invalid-comparison":
          "A control failed or the patched inspector reported an error. This comparison cannot establish that the patch works.",
      }[comparison.outcome];
      const wrap = document.createElement("div");
      wrap.className = "lab-table";
      const table = document.createElement("table");
      const caption = table.createCaption();
      caption.textContent = "Actual file round-trip comparison";
      const header = table.createTHead().insertRow();
      [
        "Run",
        "Changed rows",
        "Changed values",
        "Shape / dtype",
        "Values equal",
      ].forEach((title) => cell(header, title, "th"));
      const body = table.createTBody();
      for (const [name, value] of [
        ["Baseline control", comparison.controls.baseline],
        ["Baseline inspected", comparison.baseline],
        ["Patched control", comparison.controls.patched],
        ["Patched inspected", comparison.patched],
      ]) {
        const row = body.insertRow();
        [
          name,
          value.changed_rows ?? "Shape differs",
          value.changed_values ?? "Shape differs",
          `${value.shape_equal ? "same shape" : "different shape"} / ${value.dtype_equal ? "same dtype" : "different dtype"}`,
          value.values_equal ? "Yes" : "No",
        ].forEach((text) => cell(row, text));
      }
      wrap.append(table);
      results.append(heading, conclusion, wrap);
      if (comparison.baseline.examples.length) {
        const examples = document.createElement("p");
        examples.textContent =
          "Baseline differences (zero-based indexes): " +
          comparison.baseline.examples
            .map(
              (v) =>
                `row ${v.row}, channel ${v.channel}: expected ${v.expected}, saved ${v.actual}`,
            )
            .join("; ");
        results.append(examples);
      }
    }
    document.querySelector("#executionDetails").hidden = false;
    document.querySelector("#runDetails").textContent = JSON.stringify(
      data,
      null,
      2,
    );
  }
  async function request(url, options) {
    const response = await fetch(url, { ...options, cache: "no-store" });
    if (!response.headers.get("content-type")?.includes("application/json"))
      throw new Error(
        "The execution API is unavailable here. Open the deployed lab and sign in if requested.",
      );
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.error || "Execution service unavailable.");
    return data;
  }
  async function poll(id) {
    clearTimeout(timer);
    try {
      const data = await request(
        `/api/experiments?id=${encodeURIComponent(id)}`,
      );
      status.textContent = `Run ${id}: ${data.status}. ${data.message || ""}`;
      renderProgress(data);
      if (["completed", "failed", "interrupted"].includes(data.status)) {
        busy = false;
        run.disabled = !ready;
        render(data);
        if (data.status === "completed") {
          download.href = `/api/experiments?id=${encodeURIComponent(id)}&download=1`;
          download.hidden = false;
        }
      } else {
        busy = true;
        run.disabled = true;
        timer = setTimeout(() => poll(id), 5000);
      }
    } catch (error) {
      progressReadError = true;
      if (progressData) {
        progressSummary.textContent =
          "Status unavailable; showing the last received stage. Reload to check again.";
        timeline.querySelectorAll('[aria-current="step"]').forEach((node) => {
          node.removeAttribute("aria-current");
          node.querySelector(".phase-state").textContent =
            "Last reported running";
        });
        updateTimings();
      }
      status.textContent = `${error.message} Reload this page to check the same run again; no new experiment will be submitted.`;
      busy = false;
      run.disabled = !ready;
    }
  }
  form.addEventListener("input", preview);
  document.querySelector("#generateInputs").addEventListener("click", preview);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!ready || busy || !form.reportValidity()) return;
    busy = true;
    run.disabled = true;
    download.hidden = true;
    results.replaceChildren();
    progressPanel.hidden = true;
    progressData = undefined;
    document.querySelector("#executionDetails").hidden = true;
    status.textContent = "Submitting experiment…";
    const cases = inputs();
    const submission =
      pendingSubmission &&
      JSON.stringify(pendingSubmission.cases) === JSON.stringify(cases)
        ? pendingSubmission
        : { id: crypto.randomUUID(), cases };
    pendingSubmission = submission;
    history.replaceState(
      null,
      "",
      `lab.html?run=${encodeURIComponent(submission.id)}`,
    );
    try {
      const data = await request("/api/experiments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(submission),
      });
      history.replaceState(
        null,
        "",
        `lab.html?run=${encodeURIComponent(data.id)}`,
      );
      pendingSubmission = undefined;
      run.textContent = "Run on Vercel";
      poll(data.id);
    } catch (error) {
      status.textContent = error.message;
      busy = false;
      run.disabled = !ready;
      run.textContent = "Retry submission";
    }
  });
  preview();
  if (!["http:", "https:"].includes(location.protocol)) {
    availability.textContent =
      "This local file is a read-only preview. Hosted execution requires the deployed Vercel lab.";
    return;
  }
  request("/api/experiments")
    .then((data) => {
      ready = data.enabled;
      run.disabled = !ready || busy;
      availability.textContent = ready
        ? "Execution available on Vercel. No run starts until you press Run."
        : "Hosted execution is not enabled on this deployment yet.";
      const id = new URL(location.href).searchParams.get("run");
      if (ready && id) poll(id);
    })
    .catch((error) => {
      availability.textContent = error.message;
    });
})();
