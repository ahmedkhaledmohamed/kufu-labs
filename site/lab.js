/* This page submits jobs; scientific calculations run only in Vercel Sandbox. */
(() => {
  const form = document.querySelector("#experimentForm");
  if (!form) return;
  const run = document.querySelector("#runExperiment");
  const availability = document.querySelector("#labAvailability");
  const status = document.querySelector("#runStatus");
  const results = document.querySelector("#runResults");
  const download = document.querySelector("#downloadRun");
  const recipeSelect = document.querySelector("#experimentRecipe");
  recipeSelect.value =
    new URL(location.href).searchParams.get("recipe") === "mne" ? "mne" : "nwb";
  let serviceEnabled = false;
  let capabilitiesRead = false;
  let supportedRecipes = ["nwb"];
  const descriptions = {
    nwb: {
      name: "NWB stream preservation",
      intro:
        "Generate a synthetic signal, inspect it, then write and reopen the file. Compare saved values with the original using the baseline software and patch.",
      explanation:
        "These are constructed arrays, not neural recordings. A seed reproduces the same random values with the recorded NumPy version.",
      links: [
        [
          "Original problem: NWB Inspector #771",
          "https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771",
        ],
        ["Investigation and limits", "projects/nwb-stream-integrity/README.md"],
        [
          "Implementation",
          "https://github.com/ahmedkhaledmohamed/kufu-labs/tree/main/projects/nwb-stream-integrity",
        ],
      ],
      steps: [
        "A queued Vercel worker starts an isolated Sandbox.",
        "Python generates identical inputs for fresh control and inspected runs.",
        "The pinned baseline and patched NWB software write and reopen real files.",
        "Every value, shape and dtype is compared; arrays, reports and logs are saved.",
        "The Sandbox stops. Results remain available.",
      ],
      bounds: "Up to 2,000 rows × 8 channels per case.",
    },
    mne: {
      name: "MNE annotation precision",
      intro:
        "Choose a sampling rate and mark a sample. Run actual MNE annotation attachment before and after the patch, then compare the timestamp and sample indexes.",
      explanation:
        "Python constructs a four-second, one-channel linear ramp. The annotation lasts 100 ms and the recording's first-sample offset is zero. These are software fixtures, not neural recordings or a neural simulation.",
      links: [
        [
          "Original problem: MNE #12327",
          "https://github.com/mne-tools/mne-python/issues/12327",
        ],
        [
          "Investigation and limits",
          "projects/mne-annotation-onsets/README.md",
        ],
        [
          "Implementation",
          "https://github.com/ahmedkhaledmohamed/kufu-labs/tree/main/projects/mne-annotation-onsets",
        ],
      ],
      steps: [
        "A queued Vercel worker starts an isolated Sandbox.",
        "Python generates the same constructed signal and annotation for both revisions.",
        "The pinned baseline and patched MNE software attach the annotation.",
        "Onset, duration, floor/rounded indexes and unchanged-input controls are compared; actual arrays and reports are saved.",
        "The Sandbox stops. Results remain available.",
      ],
      bounds:
        "Rates from 128 to 8,192 Hz; annotation sample from zero to twice the rate. The four-rate batch uses sample 1.",
    },
  };
  function updateAvailability() {
    ready = serviceEnabled && supportedRecipes.includes(recipeSelect.value);
    run.disabled = !ready || busy;
    recipeSelect.disabled = busy;
    if (capabilitiesRead)
      availability.textContent = ready
        ? "Execution available on Vercel. No run starts until you press Run."
        : "This experiment is not enabled on this deployment yet.";
  }
  function configureRecipe() {
    const recipe = recipeSelect.value;
    const description = descriptions[recipe];
    for (const name of ["nwb", "mne"]) {
      const group = document.querySelector(`#${name}Inputs`);
      group.hidden = name !== recipe;
      group
        .querySelectorAll("input,select")
        .forEach((field) => (field.disabled = name !== recipe));
    }
    if (recipe === "mne") {
      const reference = form.elements.mneBatch.value === "reference";
      form.elements.sfreq.disabled = reference;
      form.elements.sample.disabled = reference;
      form.elements.sample.max = 2 * Number(form.elements.sfreq.value || 512);
    }
    document.querySelector("#experimentName").textContent =
      `Execution lab · ${description.name}`;
    document.querySelector("#experimentIntro").textContent = description.intro;
    document.querySelector("#inputExplanation").textContent =
      description.explanation;
    const links = document.querySelector("#experimentLinks");
    links.replaceChildren();
    for (const [label, href] of description.links) {
      if (links.childNodes.length) links.append(" · ");
      const link = document.createElement("a");
      link.textContent = label;
      link.href = href;
      links.append(link);
    }
    const steps = document.querySelector("#methodSteps");
    steps.replaceChildren();
    for (const text of description.steps) {
      const step = document.createElement("li");
      step.textContent = text;
      steps.append(step);
    }
    document.querySelector("#experimentLimits").textContent =
      `Limit: four cases per submission, 10 submissions per UTC day across both experiments. Sandbox time is capped at four minutes. ${description.bounds} This validates software properties, not biological accuracy, physical clocks or researcher benefit.`;
    updateAvailability();
    preview();
  }
  let ready = false;
  let busy = false;
  let timer;
  let pendingSubmission;
  let restoredRun;
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
    if (recipeSelect.value === "mne") {
      const origin = form.elements.origin.value;
      if (form.elements.mneBatch.value === "reference")
        return [300, 512, 1000, 2048].map((sfreq) => ({
          sfreq,
          sample: 1,
          origin,
        }));
      return [
        {
          sfreq: Number(form.elements.sfreq.value),
          sample: Number(form.elements.sample.value),
          origin,
        },
      ];
    }
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
  function restoreInputs(data, id) {
    if (restoredRun === id || !data.cases?.length) return;
    const fields =
      recipeSelect.value === "mne"
        ? ["sfreq", "sample", "origin"]
        : [
            "rows",
            "channels",
            "buffer",
            "seed",
            "pattern",
            "backend",
            "iterator",
          ];
    for (const key of fields) form.elements[key].value = data.cases[0][key];
    const equals = (planned) =>
      planned.length === data.cases.length &&
      data.cases.every((value, index) =>
        fields.every((key) => value[key] === planned[index][key]),
      );
    if (recipeSelect.value === "mne") {
      form.elements.mneBatch.value = "reference";
      if (!equals(inputs())) form.elements.mneBatch.value = "single";
    } else {
      form.elements.batch.value = "boundary";
      if (!equals(inputs())) form.elements.batch.value = "single";
    }
    configureRecipe();
    document.querySelector("#inputPlan").textContent = JSON.stringify(
      data.cases,
      null,
      2,
    );
    document.querySelector("#inputExplanation").textContent +=
      " Showing this run's input plan. Changing the controls creates a new plan.";
    restoredRun = id;
  }
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
  function renderMne(comparison, index) {
    const heading = document.createElement("h3");
    heading.textContent = `Case ${index + 1}: ${comparison.input.sfreq} Hz · sample ${comparison.input.sample} · ${comparison.input.origin} origin`;
    const conclusion = document.createElement("p");
    conclusion.textContent = {
      "patch-preserved":
        "The baseline changed the annotation timestamp; the patch preserved the original onset and duration. The signal and input annotation stayed unchanged.",
      "both-preserved":
        "Both revisions preserved this annotation. This input does not demonstrate a baseline failure.",
      "patch-changed-data":
        "The patched run changed the annotation timestamp. This input reveals a remaining precision failure.",
      "invalid-comparison":
        "A signal, input-annotation or rounded-index control failed. This comparison cannot establish that the patch works.",
    }[comparison.outcome];
    const wrap = document.createElement("div");
    wrap.className = "lab-table";
    const table = document.createElement("table");
    table.createCaption().textContent =
      "Actual MNE annotation attachment comparison";
    const header = table.createTHead().insertRow();
    [
      "Annotation",
      "Onset (s)",
      "Duration (s)",
      "Floor index",
      "Rounded index",
    ].forEach((title) => cell(header, title, "th"));
    const body = table.createTBody();
    for (const [name, value] of [
      ["Original", comparison.reference],
      ["Baseline attached", comparison.baseline],
      ["Patched attached", comparison.patched],
    ]) {
      const row = body.insertRow();
      [
        name,
        value.onset_seconds,
        value.duration_seconds,
        value.floor_index,
        value.rounded_index,
      ].forEach((value) => cell(row, value));
    }
    wrap.append(table);
    results.append(heading, conclusion, wrap);
    const controls = document.createElement("p");
    const valid = Object.values(comparison.controls).every(
      (value) =>
        value.signal_unchanged &&
        value.input_annotation_unchanged &&
        value.rounded_index_matches_sample,
    );
    controls.textContent = valid
      ? "Controls passed for both revisions: every signal value and the input annotation are unchanged, and rounded lookup matches the chosen sample. Rounded lookup is an existing workaround; it does not restore a rounded onset."
      : "One or more input controls failed; inspect the saved reports.";
    results.append(controls);
    if (comparison.reference.floor_index !== comparison.input.sample) {
      const note = document.createElement("p");
      note.textContent =
        "The original float already maps to a different sample under floor lookup. This is visible before attachment; nearest rounding matches the chosen sample.";
      results.append(note);
    }
  }
  function render(data) {
    results.replaceChildren();
    for (const [index, comparison] of (data.comparisons || []).entries()) {
      if (data.recipe === "mne") {
        renderMne(comparison, index);
        continue;
      }
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
      const recipe = data.recipe || "nwb";
      if (["nwb", "mne"].includes(recipe) && recipeSelect.value !== recipe) {
        recipeSelect.value = recipe;
        configureRecipe();
      }
      restoreInputs(data, id);
      status.textContent = `Run ${id}: ${data.status}. ${data.message || ""}`;
      renderProgress(data);
      if (["completed", "failed", "interrupted"].includes(data.status)) {
        busy = false;
        updateAvailability();
        render(data);
        if (data.status === "completed") {
          download.href = `/api/experiments?id=${encodeURIComponent(id)}&download=1`;
          download.hidden = false;
        }
      } else {
        busy = true;
        updateAvailability();
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
      updateAvailability();
    }
  }
  form.addEventListener("input", () => configureRecipe());
  recipeSelect.addEventListener("change", () => {
    clearTimeout(timer);
    pendingSubmission = undefined;
    restoredRun = undefined;
    progressData = undefined;
    run.textContent = "Run on Vercel";
    results.replaceChildren();
    progressPanel.hidden = true;
    download.hidden = true;
    document.querySelector("#executionDetails").hidden = true;
    status.textContent = "No experiment submitted.";
    if (["http:", "https:"].includes(location.protocol)) {
      const url = new URL(location.href);
      url.searchParams.set("recipe", recipeSelect.value);
      url.searchParams.delete("run");
      history.replaceState(null, "", url);
    }
    configureRecipe();
  });
  document.querySelector("#generateInputs").addEventListener("click", preview);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!ready || busy || !form.reportValidity()) return;
    busy = true;
    updateAvailability();
    download.hidden = true;
    results.replaceChildren();
    progressPanel.hidden = true;
    progressData = undefined;
    document.querySelector("#executionDetails").hidden = true;
    status.textContent = "Submitting experiment…";
    const cases = inputs();
    const submission =
      pendingSubmission &&
      pendingSubmission.recipe === recipeSelect.value &&
      JSON.stringify(pendingSubmission.cases) === JSON.stringify(cases)
        ? pendingSubmission
        : { id: crypto.randomUUID(), recipe: recipeSelect.value, cases };
    pendingSubmission = submission;
    history.replaceState(
      null,
      "",
      `lab.html?recipe=${submission.recipe}&run=${encodeURIComponent(submission.id)}`,
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
        `lab.html?recipe=${submission.recipe}&run=${encodeURIComponent(data.id)}`,
      );
      pendingSubmission = undefined;
      run.textContent = "Run on Vercel";
      poll(data.id);
    } catch (error) {
      status.textContent = error.message;
      busy = false;
      updateAvailability();
      run.textContent = "Retry submission";
    }
  });
  configureRecipe();
  if (!["http:", "https:"].includes(location.protocol)) {
    availability.textContent =
      "This local file is a read-only preview. Hosted execution requires the deployed Vercel lab.";
    return;
  }
  request("/api/experiments")
    .then((data) => {
      serviceEnabled = data.enabled;
      supportedRecipes = data.recipes || ["nwb"];
      capabilitiesRead = true;
      updateAvailability();
      const id = new URL(location.href).searchParams.get("run");
      if (ready && id) poll(id);
    })
    .catch((error) => {
      availability.textContent = error.message;
    });
})();
