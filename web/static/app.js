const $ = (selector) => document.querySelector(selector);

const els = {
  prompt: $("#prompt"),
  device: $("#device"),
  examples: $("#examples"),
  planButton: $("#planButton"),
  runButton: $("#runButton"),
  error: $("#error"),
  planSection: $("#planSection"),
  plan: $("#plan"),
  taskId: $("#taskId"),
  resultSection: $("#resultSection"),
  status: $("#status"),
  summary: $("#summary"),
  metrics: $("#metrics"),
  verification: $("#verification"),
  probabilityCard: $("#probabilityCard"),
  probabilities: $("#probabilities"),
  artifacts: $("#artifacts"),
};

const exampleLabels = ["Bell纠缠验证", "Grover搜索", "QAOA MaxCut"];

async function request(path) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: els.prompt.value, device: els.device.value }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "请求失败");
  return payload;
}

function setBusy(busy, label = "运行并验证") {
  els.planButton.disabled = busy;
  els.runButton.disabled = busy;
  els.runButton.querySelector("span").textContent = busy ? "实验执行中…" : label;
}

function showError(message) {
  els.error.textContent = message;
  els.error.classList.toggle("hidden", !message);
}

function renderPlan(payload) {
  els.planSection.classList.remove("hidden");
  els.taskId.textContent = payload.spec?.task_id ? `TASK ${payload.spec.task_id}` : "";
  els.plan.innerHTML = payload.plan.map((step, index) => `
    <div class="step">
      <b>STEP ${String(index + 1).padStart(2, "0")}</b>
      <strong>${escapeHtml(step.title)}</strong>
      <p>${escapeHtml(step.detail)}</p>
    </div>`).join("");
}

function renderResult(payload) {
  els.resultSection.classList.remove("hidden");
  els.status.className = `status ${payload.status}`;
  els.status.textContent = payload.status.toUpperCase();
  els.summary.textContent = payload.summary;
  const metricEntries = flattenMetrics(payload.metrics).slice(0, 8);
  els.metrics.innerHTML = metricEntries.map(([key, value]) => `
    <div class="metric"><span>${escapeHtml(labelize(key))}</span><b>${escapeHtml(formatValue(value))}</b></div>
  `).join("");

  els.verification.innerHTML = Object.entries(payload.verification || {}).map(([key, value]) => `
    <div class="check ${key === "passed" ? "primary" : ""}">
      <span>${escapeHtml(labelize(key))}</span><b>${escapeHtml(formatValue(value))}</b>
    </div>`).join("");

  const states = (payload.probabilities || []).map((value, index) => ({
    label: payload.labels[index], value: Number(value),
  })).sort((a, b) => b.value - a.value).slice(0, 10);
  els.probabilityCard.classList.toggle("hidden", states.length === 0);
  els.probabilities.innerHTML = states.map(({ label, value }) => `
    <div class="bar"><span>|${escapeHtml(label)}⟩</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(1, value * 100)}%"></div></div><b>${(value * 100).toFixed(3)}%</b></div>
  `).join("");

  els.artifacts.innerHTML = Object.entries(payload.artifacts || {}).map(([key, url]) => `
    <a class="artifact" href="${encodeURI(url)}" target="_blank"><span>${escapeHtml(labelize(key))}</span><b>打开 ↗</b></a>
  `).join("") || '<span class="hint">暂无产物</span>';
}

function flattenMetrics(metrics) {
  const entries = [];
  for (const [key, value] of Object.entries(metrics || {})) {
    if (value && typeof value === "object") {
      for (const [child, childValue] of Object.entries(value)) {
        if (typeof childValue !== "object") entries.push([`${key}.${child}`, childValue]);
      }
    } else entries.push([key, value]);
  }
  return entries;
}

function labelize(value) {
  return value.replaceAll("_", " ").replaceAll(".", " · ");
}

function formatValue(value) {
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(6);
  if (typeof value === "boolean") return value ? "PASS" : "FAIL";
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value ?? "—");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

els.planButton.addEventListener("click", async () => {
  showError(""); setBusy(true);
  try { renderPlan(await request("/api/plan")); els.planSection.scrollIntoView({ behavior: "smooth" }); }
  catch (error) { showError(error.message); }
  finally { setBusy(false); }
});

els.runButton.addEventListener("click", async () => {
  showError(""); setBusy(true);
  try {
    const payload = await request("/api/run");
    renderPlan({ spec: payload.spec, plan: payload.plan });
    renderResult(payload);
    els.resultSection.scrollIntoView({ behavior: "smooth" });
  } catch (error) { showError(error.message); }
  finally { setBusy(false); }
});

fetch("/api/examples").then(response => response.json()).then(payload => {
  els.examples.innerHTML = payload.examples.map((prompt, index) => `<button class="example" data-prompt="${escapeHtml(prompt)}">${exampleLabels[index]}</button>`).join("");
  els.examples.querySelectorAll(".example").forEach(button => button.addEventListener("click", () => { els.prompt.value = button.dataset.prompt; }));
  els.prompt.value = payload.examples[1];
});

