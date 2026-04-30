const $ = (id) => document.getElementById(id);
let OFFICE_STATE = null;

function list(items) {
  return (items || []).map((item) => `<li>${escapeHtml(String(item))}</li>`).join("");
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}

async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}

async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(data));
  return data;
}

function renderRoster(agents) {
  $("roster").innerHTML = agents.map((agent) => `
    <article class="agent-card">
      <h3>${escapeHtml(agent.display_name)}</h3>
      <p class="role">${escapeHtml(agent.legacy_role)}</p>
      <p class="muted">${escapeHtml(agent.current_status)}</p>
      <p><strong>Accepts tasks:</strong> ${agent.can_accept_tasks ? "yes" : "no"}</p>
      <p>${escapeHtml((agent.known_responsibilities || []).slice(0, 2).join("; "))}</p>
      <button type="button" data-agent-id="${escapeHtml(agent.agent_id)}">Open room</button>
    </article>
  `).join("");
  $("target-agent").innerHTML = agents
    .filter((agent) => agent.can_accept_tasks)
    .map((agent) => `<option value="${escapeHtml(agent.agent_id)}">${escapeHtml(agent.display_name)} - ${escapeHtml(agent.legacy_role)}</option>`)
    .join("");
  document.querySelectorAll("[data-agent-id]").forEach((button) => {
    button.addEventListener("click", () => openRoom(button.dataset.agentId));
  });
}

async function openRoom(agentId) {
  const agent = await getJson(`/api/agents/${agentId}`);
  const room = agent.room || {};
  $("agent-room").innerHTML = `
    <h3>${escapeHtml(agent.display_name)}</h3>
    <p class="role">${escapeHtml(agent.legacy_role)}</p>
    <p><strong>Status:</strong> ${escapeHtml(agent.current_status)}</p>
    <p><strong>Evidence:</strong> ${escapeHtml(agent.source_evidence_summary || "needs review")}</p>
    <h4>Responsibilities</h4><ul>${list(agent.known_responsibilities)}</ul>
    <h4>What owner can ask</h4><ul>${list(room.what_owner_can_ask)}</ul>
    <h4>Requires approval</h4><ul>${list(room.requires_owner_approval)}</ul>
    <h4>Inbox</h4><ul>${list(room.current_inbox)}</ul>
    <p class="muted">Brain/profile refs are shown as refs only; contents are not loaded here.</p>
  `;
}

function renderState(state) {
  OFFICE_STATE = state;
  $("phase").textContent = state.current_phase;
  renderRoster(state.agents);
  $("work-queue").innerHTML = (state.work_queue || []).map((item) => `<li><strong>${escapeHtml(item.owner || "team")}</strong>: ${escapeHtml(item.task || item.work_id)}</li>`).join("");
  $("pending-approvals").innerHTML = list(state.pending_approvals);
  $("blocked-actions").innerHTML = list(state.blocked_actions);
  $("commercial-path").innerHTML = `
    <p><strong>Selected cash path:</strong> ${escapeHtml(state.commercial_path_summary.selected_cash_path || "not available")}</p>
    <p><strong>Service offer:</strong> ${escapeHtml(state.commercial_path_summary.service_offer || "not available")}</p>
    <p><strong>Status:</strong> ${escapeHtml(state.commercial_path_summary.status || "approval gated")}</p>
  `;
  if (state.agents.length) openRoom(state.agents.find((agent) => agent.agent_id === "aiden_ceo")?.agent_id || state.agents[0].agent_id);
}

async function refreshOffice() {
  renderState(await getJson("/api/status"));
}

$("refresh-button").addEventListener("click", refreshOffice);
$("message-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    target_agent: $("target-agent").value,
    objective: $("message-objective").value,
    message_text: $("message-text").value,
    urgency: $("message-urgency").value,
  };
  $("packet-result").textContent = JSON.stringify(await postJson("/api/message", payload), null, 2);
});
$("team-task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    task_title: $("task-title").value,
    task_description: $("task-description").value,
  };
  $("packet-result").textContent = JSON.stringify(await postJson("/api/team_task", payload), null, 2);
});

refreshOffice().catch((error) => {
  $("packet-result").textContent = `Office failed to load: ${error}`;
});
