const historyEl = document.getElementById("chat-history");
const form = document.getElementById("aiden-chat-form");
const textarea = document.getElementById("aiden-message");
const statusEl = document.getElementById("chat-status");
const statusCard = document.getElementById("aiden-status-card");
const contextPanel = document.getElementById("context-panel");

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function renderTurn(turn) {
  const isOwner = turn.speaker === "owner";
  const intent = turn.intent ? `<small>intent: ${escapeHtml(turn.intent)}</small>` : "";
  return `
    <div class="message ${isOwner ? "owner" : "aiden"}">
      <strong>${isOwner ? "你" : "Aiden"}</strong>
      <p>${escapeHtml(turn.text)}</p>
      ${intent}
    </div>`;
}

function renderHistory(history) {
  const turns = history && history.length ? history : [{
    speaker: "aiden_ceo",
    text: "我在。你可以直接问：为什么是这个商业方向？Labs 的元发展是什么？我现在到底是什么状态？我会基于当前本地 context 回答。",
  }];
  historyEl.innerHTML = turns.slice(-40).map(renderTurn).join("");
  historyEl.scrollTop = historyEl.scrollHeight;
}

async function getJson(path) {
  const response = await fetch(path);
  const data = await response.json();
  if (!response.ok || data.ok === false) throw new Error(data.error || path);
  return data;
}

async function postJson(path, payload = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) throw new Error(data.error || path);
  return data;
}

async function loadStatus() {
  const data = await getJson("/api/aiden/status");
  const profile = data.profile || {};
  statusCard.innerHTML = `
    <span>Aiden 状态</span>
    <strong>${escapeHtml(profile.current_state || "context-grounded local CEO layer")}</strong>
    <p>已知 milestones: ${escapeHtml((data.diagnostics?.milestones_known || []).length)} · memory turns: ${escapeHtml(data.meeting_memory_count || 0)}</p>`;
}

async function loadHistory() {
  const data = await getJson("/api/aiden/thread");
  renderHistory(data.history || []);
}

async function sendMessage(text) {
  const data = await postJson("/api/aiden/message", {message: text});
  renderHistory(data.history || []);
  return data;
}

function showPanel(title, items) {
  contextPanel.hidden = false;
  contextPanel.innerHTML = `<strong>${escapeHtml(title)}</strong><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

async function showBasis() {
  const data = await getJson("/api/aiden/context");
  const context = data.context || {};
  showPanel("Aiden 当前依据", [
    `runtime: ${context.current_runtime_stage}`,
    `milestones: ${(context.completed_milestones || []).join(" / ")}`,
    `seed paths: ${(context.commercial_seed_paths || []).slice(0, 5).join(" / ")}`,
    `principle: ${(context.meta_development_principles || [])[1] || ""}`,
  ]);
}

async function showLimits() {
  const data = await getJson("/api/aiden/context");
  showPanel("当前限制", data.context?.current_limitations || []);
}

async function buildSummary() {
  const data = await postJson("/api/aiden/summary", {});
  const summary = data.summary || {};
  showPanel("CEO Meeting Summary", [
    `goal: ${summary.current_meeting_goal || "Aiden discussion"}`,
    `owner questions: ${(summary.owner_questions || []).length}`,
    `follow-up: ${(summary.follow_up_tasks || []).slice(-3).join(" / ") || "none yet"}`,
  ]);
  statusEl.textContent = "已生成本地会议摘要。没有外发。";
}

async function createMission() {
  const data = await postJson("/api/aiden/create_l10_mission", {});
  const mission = data.mission_candidate || {};
  showPanel("L10 Mission Candidate", [
    mission.mission_title || "Aiden CEO discussion follow-up mission",
    mission.owner_goal || "",
    mission.suggested_permission_tier || "",
    `status: ${mission.status || "candidate_only_not_executed"}`,
  ]);
  statusEl.textContent = "已创建本地 L10 mission candidate，没有执行外部动作。";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textarea.value.trim();
  if (!text) return;
  textarea.value = "";
  statusEl.textContent = "Aiden 正在基于 Labs context 回复...";
  form.querySelector("button").disabled = true;
  renderHistory([
    ...Array.from(historyEl.querySelectorAll(".message")).map((node) => ({
      speaker: node.classList.contains("owner") ? "owner" : "aiden_ceo",
      text: node.querySelector("p")?.textContent || "",
    })),
    {speaker: "owner", text},
  ]);
  try {
    const data = await sendMessage(text);
    const diag = data.diagnostics || {};
    statusEl.textContent = `已本地回复。intent: ${diag.used_fallback ? "unknown-useful" : data.reply?.intent || "known"}；没有外发。`;
    await loadStatus();
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    form.querySelector("button").disabled = false;
    textarea.focus();
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    textarea.value = button.dataset.prompt || "";
    textarea.focus();
  });
});

document.getElementById("show-basis-button").addEventListener("click", showBasis);
document.getElementById("show-limits-button").addEventListener("click", showLimits);
document.getElementById("summary-button").addEventListener("click", buildSummary);
document.getElementById("mission-button").addEventListener("click", createMission);

loadStatus().catch(() => {});
loadHistory().catch(() => {});
