const $ = (id) => document.getElementById(id);
const columns = ["Inbox", "Interpreting", "Assigned", "In Progress", "Waiting for Approval", "Blocked", "Done"];
let OFFICE_STATE = null;

function escapeHtml(text) {
  return String(text || "").replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function list(items) { return (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join(""); }
async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}
async function postJson(path, payload = {}) {
  const response = await fetch(path, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload) });
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
      <button type="button" data-agent-id="${escapeHtml(agent.agent_id)}">Open room</button>
    </article>`).join("");
  const options = [`<option value="whole_team">Whole Team</option>`].concat(agents.filter((agent) => agent.can_accept_tasks).map((agent) => `<option value="${escapeHtml(agent.agent_id)}">${escapeHtml(agent.display_name)} - ${escapeHtml(agent.legacy_role)}</option>`));
  $("whiteboard-target").innerHTML = options.join("");
  document.querySelectorAll("[data-agent-id]").forEach((button) => button.addEventListener("click", () => openRoom(button.dataset.agentId)));
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
    <h4>Inbox</h4><ul>${list(room.current_inbox)}</ul>`;
}

function renderWhiteboard(snapshot) {
  const messages = (snapshot.threads || []).flatMap((thread) => thread.messages || []);
  const replies = snapshot.agent_replies || [];
  const rows = messages.map((m) => `<div class="bubble ${escapeHtml(m.sender_type)}"><strong>${escapeHtml(m.sender_id)}</strong> → ${escapeHtml(m.target)}<br>${escapeHtml(m.text)}</div>`)
    .concat(replies.map((r) => `<div class="bubble agent"><strong>${escapeHtml(r.agent_id)}</strong><br>${escapeHtml(r.work_done)}<br><span class="muted">${escapeHtml(r.next_step)}</span></div>`));
  $("whiteboard-thread").innerHTML = rows.join("") || "<p class='muted'>No whiteboard messages yet. Send a goal to the team.</p>";
}

function renderWorkBoard(board) {
  $("work-board").innerHTML = columns.map((column) => `
    <div class="column"><h3>${column}</h3>${(board[column] || []).map((item) => `
      <article class="work-card">
        <strong>${escapeHtml(item.title)}</strong>
        <p class="status">${escapeHtml(item.status)}</p>
        <p>${escapeHtml((item.assigned_agents || []).join(", "))}</p>
        <p class="muted">${escapeHtml((item.progress_notes || []).slice(-1)[0] || item.description)}</p>
      </article>`).join("")}</div>`).join("");
}

function renderAgentPanel(state, snapshot) {
  const replies = snapshot.agent_replies || [];
  $("agent-panel").innerHTML = state.agents.filter((agent) => agent.can_accept_tasks).map((agent) => {
    const last = [...replies].reverse().find((reply) => reply.agent_id === agent.agent_id);
    return `<article class="agent-card"><h3>${escapeHtml(agent.display_name)}</h3><p class="role">${escapeHtml(agent.legacy_role)}</p><p>Self-work: ${agent.can_self_work ? "yes" : "no"}</p><p class="muted">${escapeHtml(last ? last.next_step : "Ready")}</p></article>`;
  }).join("");
}

function renderTimeline(events) {
  $("progress-timeline").innerHTML = (events || []).slice(-30).reverse().map((event) => `<li><strong>${escapeHtml(event.event_type)}</strong>: ${escapeHtml(event.description)}</li>`).join("");
}

function renderScheduler(status, runs, heartbeats, interrupts) {
  $("scheduler-status").innerHTML = `
    <p><strong>Ready:</strong> ${status.scheduler_ready ? "yes" : "no"}</p>
    <p><strong>Pending:</strong> ${status.pending_work_items} · <strong>Eligible:</strong> ${status.eligible_autonomous_work_items}</p>
    <p><strong>Last tick:</strong> ${escapeHtml(status.last_scheduler_tick ? status.last_scheduler_tick.summary : "none yet")}</p>
    <p><strong>No external side effects:</strong> ${status.no_external_side_effects ? "yes" : "no"} · <strong>No core writeback:</strong> ${status.no_core_writeback ? "yes" : "no"}</p>`;
  $("progress-heartbeats").innerHTML = (heartbeats.progress_heartbeats || []).slice(-8).reverse().map((item) => `<li>${escapeHtml(item.summary)} <span class="muted">${escapeHtml(item.work_item_id || "")}</span></li>`).join("") || "<li>No progress heartbeats yet.</li>";
  $("approval-interruptions").innerHTML = (interrupts.approval_interrupts || []).slice(-8).reverse().map((item) => `<li>${escapeHtml(item.owner_visible_explanation)} <span class="muted">${escapeHtml(item.status)}</span></li>`).join("") || "<li>No approval interruptions.</li>";
  $("autonomous-runs").innerHTML = (runs.autonomous_runs || []).slice(-8).reverse().map((item) => `<li>${escapeHtml(item.summary)} <span class="muted">${escapeHtml(item.stop_reason)}</span></li>`).join("") || "<li>No autonomous runs yet.</li>";
}

function renderL8Cockpit(cockpit) {
  const path = cockpit.selected_first_cash_path || {};
  const pendingActions = cockpit.pending_commercial_actions || [];
  const manualPackets = cockpit.approved_manual_send_packets || [];
  const feedback = cockpit.customer_feedback_packets || [];
  const residuals = cockpit.commercial_residuals || [];
  const learning = cockpit.learning_candidates || [];
  $("l8-cockpit").innerHTML = `
    <p><strong>Selected path:</strong> ${escapeHtml(path.selected_offer || "Founder AI Workflow Audit & CEO Command Brief Sprint")}</p>
    <p><strong>Stage:</strong> ${escapeHtml(cockpit.current_commercial_stage)}</p>
    <p><strong>Pending actions:</strong> ${pendingActions.length} · <strong>Manual packets:</strong> ${manualPackets.length} · <strong>Feedback:</strong> ${feedback.length}</p>
    <p><strong>Residuals:</strong> ${residuals.length} · <strong>Learning candidates:</strong> ${learning.length}</p>
    <p><strong>Paid signal:</strong> ${escapeHtml(cockpit.paid_signal_status)}</p>
    <p><strong>Next owner decision:</strong> ${escapeHtml(cockpit.next_recommended_owner_decision)}</p>
    <p><strong>Tool-send email enabled:</strong> ${cockpit.tool_send_email_enabled ? "yes" : "no"}</p>`;
  $("l8-action-select").innerHTML = pendingActions.map((action) => `<option value="${escapeHtml(action.action_id)}">${escapeHtml(action.action_type)} · ${escapeHtml(action.status)}</option>`).join("") || "<option value=''>No pending action</option>";
  $("l8-manual-packet-select").innerHTML = manualPackets.map((packet) => `<option value="${escapeHtml(packet.packet_id)}">${escapeHtml(packet.subject_or_opening)} · ${escapeHtml(packet.status)}</option>`).join("") || "<option value=''>No manual-send packet</option>";
}

async function refreshOffice() {
  const state = await getJson("/api/status");
  const snapshot = await getJson("/api/whiteboard");
  const scheduler = await getJson("/api/scheduler/status");
  const runs = await getJson("/api/autonomous_runs");
  const heartbeats = await getJson("/api/progress_heartbeats");
  const interrupts = await getJson("/api/approval_interrupts");
  const l8Cockpit = await getJson("/api/l8/cockpit");
  OFFICE_STATE = state;
  $("phase").textContent = `${state.l8_runtime_phase || state.scheduler_runtime_phase || state.whiteboard_runtime_phase || state.current_phase} · ${state.agent_count} recovered agents`;
  renderRoster(state.agents);
  renderWhiteboard(snapshot);
  renderWorkBoard(snapshot.work_board || {});
  renderAgentPanel(state, snapshot);
  renderTimeline(snapshot.timeline || []);
  renderScheduler(scheduler, runs, heartbeats, interrupts);
  renderL8Cockpit(l8Cockpit);
  $("pending-approvals").innerHTML = list((snapshot.approval_requests || []).map((item) => item.reason).concat(state.pending_approvals || []));
  $("blocked-actions").innerHTML = list(state.blocked_actions);
  if (state.agents.length) openRoom(state.agents.find((agent) => agent.agent_id === "aiden_ceo")?.agent_id || state.agents[0].agent_id);
}

async function act(label, path, payload = {}) {
  const data = await postJson(path, payload);
  $("packet-result").textContent = `${label}\n${JSON.stringify(data, null, 2)}`;
  await refreshOffice();
}

$("refresh-button").addEventListener("click", refreshOffice);
$("whiteboard-message-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await act("Whiteboard message created", "/api/whiteboard/message", {
    target: $("whiteboard-target").value,
    text: $("whiteboard-text").value,
    objective: $("whiteboard-objective").value,
  });
});
$("route-button").addEventListener("click", () => act("Aiden routing decision", "/api/route"));
$("work-cycle-button").addEventListener("click", () => act("Safe work cycle", "/api/work_cycle"));
$("team-cycle-button").addEventListener("click", () => act("Team work cycle", "/api/team_work_cycle"));
$("scheduler-once-button").addEventListener("click", () => act("Scheduler run once", "/api/scheduler/run_once", {max_cycles: 1}));
$("scheduler-bounded-button").addEventListener("click", () => act("Bounded scheduler self-work", "/api/scheduler/run_bounded", {max_work_items: 3, max_cycles: 2}));
$("completion-button").addEventListener("click", () => act("Completion report", "/api/completion_report"));
$("l8-start-button").addEventListener("click", () => act("L8 first cash path initialized", "/api/l8/first_cash_path/start"));
$("l8-build-actions-button").addEventListener("click", () => act("L8 commercial action queue built", "/api/l8/commercial_actions/build"));
$("l8-decide-button").addEventListener("click", () => act("L8 approval decision", "/api/l8/approvals/decide", {
  action_id: $("l8-action-select").value,
  decision: $("l8-decision-select").value,
  decision_note: $("l8-decision-note").value,
}));
$("l8-mark-manual-button").addEventListener("click", () => act("L8 manual-send packet marked", "/api/l8/manual_send_packets/mark", {
  packet_id: $("l8-manual-packet-select").value,
  owner_marked_status: $("l8-manual-status-select").value,
  owner_note: $("l8-manual-note").value,
}));
$("l8-feedback-button").addEventListener("click", () => act("L8 customer feedback recorded", "/api/l8/customer_feedback", {
  manual_send_packet_id: $("l8-manual-packet-select").value,
  response_status: $("l8-feedback-status-select").value,
  feedback_text: $("l8-feedback-text").value,
}));
$("l8-residual-button").addEventListener("click", () => act("L8 commercial residual generated", "/api/l8/residuals/build"));
$("l8-learning-button").addEventListener("click", () => act("L8 learning candidate generated", "/api/l8/learning_candidates/build"));
$("l8-refresh-cockpit-button").addEventListener("click", () => act("L8 cockpit snapshot refreshed", "/api/l8/first_cash_path/start"));

refreshOffice().catch((error) => { $("packet-result").textContent = `Office failed to load: ${error}`; });
