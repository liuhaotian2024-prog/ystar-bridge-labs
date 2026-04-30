const $ = (id) => document.getElementById(id);
const columns = ["Inbox", "Interpreting", "Assigned", "In Progress", "Waiting for Approval", "Blocked", "Done"];
let OFFICE_STATE = null;
let latestOwnerMessage = null;
let latestWorkItemId = "";
document.body.dataset.officeMode = "meeting";
const quickTemplates = {
  "first-cash": {
    text: "Aiden，请带团队分析：Y*Bridge Labs 下一步怎么最快拿到第一笔钱，同时不要牺牲长期战略。请分派给 Sofia、Marco、Zara、Ethan、Jinjin 和 Samantha。",
    objective: "Find the safest fastest first-cash path",
  },
  "thirty-day": {
    text: "团队请一起制定未来 30 天的 meta-development 计划：目标是提高首笔收入概率，同时保留长期产品化路线。",
    objective: "Build a 30-day meta-development plan",
  },
  "opportunities": {
    text: "团队请发现并比较多个可能赚钱路径，不要只看 Founder AI Workflow Audit；请按最短兑现路径、战略价值、执行难度排序。",
    objective: "Discover and rank money-making opportunities",
  },
};

function escapeHtml(text) {
  return String(text || "").replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function list(items) { return (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join(""); }
function setSendStatus(message, tone = "") {
  const status = $("whiteboard-send-status");
  if (!status) return;
  status.className = `send-status muted ${tone}`.trim();
  status.textContent = message;
}
function setOfficeMode(mode) {
  const nextMode = mode === "execution" ? "execution" : "meeting";
  document.body.dataset.officeMode = nextMode;
  try {
    localStorage.setItem("labsOfficeMode", nextMode);
  } catch (error) {
    // Local storage can be unavailable in restricted browser contexts.
  }
  document.querySelectorAll("[data-office-mode-button]").forEach((button) => {
    const active = button.dataset.officeModeButton === nextMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}
async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}
async function postJson(path, payload = {}) {
  const response = await fetch(path, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload) });
  const raw = await response.text();
  let data = {};
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch (error) {
    data = {ok: false, error: raw || String(error)};
  }
  if (!response.ok) {
    const error = new Error(data.error || `${path}: ${response.status}`);
    error.status = response.status;
    error.payload = data;
    error.path = path;
    throw error;
  }
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

function sortedByUpdated(items) {
  return [...(items || [])].sort((a, b) => {
    const bKey = `${String(b.last_routed_at_epoch_ns || "").padStart(20, "0")}|${b.updated_at_utc || b.created_at_utc || ""}|${b.work_item_id || b.reply_id || b.thread_id || ""}`;
    const aKey = `${String(a.last_routed_at_epoch_ns || "").padStart(20, "0")}|${a.updated_at_utc || a.created_at_utc || ""}|${a.work_item_id || a.reply_id || a.thread_id || ""}`;
    return bKey.localeCompare(aKey);
  });
}

function allWorkItems(board) {
  return columns.flatMap((column) => board[column] || []);
}

function dedupeWorkItems(items) {
  const seen = new Set();
  return sortedByUpdated(items).filter((item) => {
    const key = item.source_message_id || item.title || item.work_item_id;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function latestWorkItem(snapshot) {
  return dedupeWorkItems(allWorkItems(snapshot.work_board || {}))[0] || null;
}

function latestThread(snapshot) {
  return sortedByUpdated(snapshot.threads || [])[0] || null;
}

function currentReplies(snapshot, workItemId) {
  const replies = sortedByUpdated(snapshot.agent_replies || []);
  const scoped = workItemId ? replies.filter((reply) => reply.work_item_id === workItemId) : [];
  return (workItemId ? scoped : replies).slice(0, 8);
}

function renderFindings(findings) {
  const safeFindings = (findings || []).slice(0, 4);
  return safeFindings.length ? `<ul>${safeFindings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : "";
}

function renderWhiteboard(snapshot) {
  const thread = latestThread(snapshot);
  const item = latestWorkItem(snapshot);
  if (item?.work_item_id) latestWorkItemId = item.work_item_id;
  const messages = (thread?.messages || []).slice(-2);
  const replies = currentReplies(snapshot, item?.work_item_id);
  const totalMessages = (snapshot.threads || []).flatMap((entry) => entry.messages || []).length;
  const totalReplies = (snapshot.agent_replies || []).length;
  const focus = item ? `
    <article class="current-focus">
      <span class="section-label">Current Focus</span>
      <h3>${escapeHtml(item.title)}</h3>
      <p><strong>Status:</strong> ${escapeHtml(item.status)} · <strong>Agents:</strong> ${escapeHtml((item.assigned_agents || []).join(", ") || "not routed yet")}</p>
      <p class="muted">${escapeHtml((item.progress_notes || []).slice(-1)[0] || item.description || "Waiting for team work.")}</p>
    </article>` : "";
  const waitingForTeam = item && !replies.length && !["Done", "Waiting for Approval", "Blocked"].includes(item.status)
    ? `<div class="bubble system"><strong>system</strong><br>Aiden 已经拆好任务，但团队还没有工作。下一步请点 “3. 团队工作一轮”。</div>`
    : "";
  const rows = messages.map((m) => `<div class="bubble ${escapeHtml(m.sender_type)}"><strong>${escapeHtml(m.sender_id)}</strong> → ${escapeHtml(m.target)}<br>${escapeHtml(m.text)}</div>`)
    .concat(replies.map((r) => `<div class="bubble agent"><strong>${escapeHtml(r.agent_id)}</strong><br>${escapeHtml(r.work_done)}${renderFindings(r.findings)}<span class="muted">Next: ${escapeHtml(r.next_step)}</span></div>`));
  const historyNote = totalMessages || totalReplies
    ? `<details class="history-note"><summary>旧历史已隐藏：${Math.max(totalMessages - messages.length, 0)} 条消息、${Math.max(totalReplies - replies.length, 0)} 条回复</summary><p class="muted">为了避免办公室变成日志瀑布，这里默认只显示最近一次任务。历史 packet 仍保留在本地。</p></details>`
    : "";
  $("whiteboard-thread").innerHTML = focus + (rows.join("") || "<p class='muted'>No whiteboard messages yet. Send a goal to the team.</p>") + waitingForTeam + historyNote;
}

function renderWorkBoard(board) {
  const recentItems = dedupeWorkItems(allWorkItems(board)).slice(0, 8);
  const recentIds = new Set(recentItems.map((item) => item.work_item_id));
  $("work-board").innerHTML = columns.map((column) => `
    <div class="column"><h3>${column}</h3>${sortedByUpdated((board[column] || []).filter((item) => recentIds.has(item.work_item_id))).map((item) => `
      <article class="work-card">
        <strong>${escapeHtml(item.title)}</strong>
        <p class="status">${escapeHtml(item.status)}</p>
        <p>${escapeHtml((item.assigned_agents || []).join(", "))}</p>
        <p class="muted">${escapeHtml((item.progress_notes || []).slice(-1)[0] || item.description)}</p>
      </article>`).join("") || "<p class='muted'>No recent item.</p>"}</div>`).join("");
}

function renderAgentPanel(state, snapshot) {
  const replies = snapshot.agent_replies || [];
  $("agent-panel").innerHTML = state.agents.filter((agent) => agent.can_accept_tasks).map((agent) => {
    const last = [...replies].reverse().find((reply) => reply.agent_id === agent.agent_id);
    return `<article class="agent-card"><h3>${escapeHtml(agent.display_name)}</h3><p class="role">${escapeHtml(agent.legacy_role)}</p><p>Self-work: ${agent.can_self_work ? "yes" : "no"}</p><p class="muted">${escapeHtml(last ? last.next_step : "Ready")}</p></article>`;
  }).join("");
}

function renderTimeline(events) {
  $("progress-timeline").innerHTML = (events || []).slice(-12).reverse().map((event) => `<li><strong>${escapeHtml(event.event_type)}</strong>: ${escapeHtml(event.description)}</li>`).join("");
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

function renderL9Cockpit(cockpit) {
  const opportunities = cockpit.opportunity_candidates || [];
  const paths = cockpit.money_path_candidates || [];
  const selected = cockpit.selected_opportunities || [];
  const plans = cockpit.execution_plans || [];
  const bridges = cockpit.l8_bridge_packets || [];
  const residuals = cockpit.portfolio_residuals || [];
  const learning = cockpit.portfolio_learning_candidates || [];
  const decisionPackets = cockpit.owner_decision_packets || [];
  $("l9-cockpit").innerHTML = `
    <p><strong>Assets:</strong> ${cockpit.internal_asset_inventory_summary?.count || 0} · <strong>Opportunities:</strong> ${opportunities.length} · <strong>Money paths:</strong> ${paths.length}</p>
    <p><strong>Top balanced recommendation:</strong> ${escapeHtml(cockpit.top_recommendation?.path_title || cockpit.top_recommendation?.money_path_id || "not ranked yet")}</p>
    <p><strong>Shortest-cash recommendation:</strong> ${escapeHtml(cockpit.shortest_cash_recommendation?.path_title || cockpit.shortest_cash_recommendation?.money_path_id || "not ranked yet")}</p>
    <p><strong>Selected paths:</strong> ${selected.length} · <strong>Execution plans:</strong> ${plans.length} · <strong>L8 bridge packets:</strong> ${bridges.length}</p>
    <p><strong>Portfolio residuals:</strong> ${residuals.length} · <strong>Learning candidates:</strong> ${learning.length}</p>
    <p><strong>Next owner decision:</strong> ${escapeHtml(cockpit.next_recommended_owner_decision)}</p>
    <p><strong>Grant/RFP default path:</strong> ${escapeHtml(cockpit.grant_rfp_default_path_status)}</p>`;
  $("l9-decision-packet-select").innerHTML = decisionPackets.map((packet) => `<option value="${escapeHtml(packet.decision_packet_id)}">${escapeHtml(packet.money_path_id)} · ${escapeHtml(packet.recommended_decision)}</option>`).join("") || "<option value=''>No decision packet</option>";
  $("l9-money-path-select").innerHTML = selected.map((path) => `<option value="${escapeHtml(path.money_path_id)}">${escapeHtml(path.path_title)}</option>`).join("") || paths.map((path) => `<option value="${escapeHtml(path.money_path_id)}">${escapeHtml(path.path_title)} · ${escapeHtml(path.status)}</option>`).join("") || "<option value=''>No money path</option>";
  $("l9-execution-plan-select").innerHTML = plans.map((plan) => `<option value="${escapeHtml(plan.execution_plan_id)}">${escapeHtml(plan.money_path_id)} · ${escapeHtml(plan.status)}</option>`).join("") || "<option value=''>No execution plan</option>";
}

function renderL10Cockpit(cockpit) {
  const missions = cockpit.missions || [];
  const active = cockpit.active_missions || [];
  const escalations = cockpit.escalation_queue || [];
  const reports = cockpit.mission_completion_reports || [];
  $("l10-cockpit").innerHTML = `
    <p><strong>Missions:</strong> ${missions.length} · <strong>Active:</strong> ${active.length} · <strong>Evidence:</strong> ${cockpit.evidence_count || 0}</p>
    <p><strong>Signals:</strong> ${cockpit.opportunity_signal_count || 0} · <strong>Strategy brief:</strong> ${escapeHtml(cockpit.strategy_brief_status || "not_ready")}</p>
    <p><strong>Escalations waiting:</strong> ${escalations.length} · <strong>Completion reports:</strong> ${reports.length}</p>
    <p><strong>Fixture demo:</strong> ${cockpit.fixture_demo_available ? "available" : "unavailable"} · <strong>Configured live read-only:</strong> ${cockpit.configured_live_read_only_research_available ? "available" : "disabled"}</p>
    <p><strong>Next owner decision:</strong> ${escapeHtml(cockpit.next_owner_decision || "create mission")}</p>`;
  $("l10-escalation-select").innerHTML = (cockpit.escalation_packets || []).map((packet) => `<option value="${escapeHtml(packet.escalation_id)}">${escapeHtml(packet.requested_action)} · ${escapeHtml(packet.status)}</option>`).join("") || "<option value=''>No escalation packet</option>";
}

async function refreshOffice() {
  const state = await getJson("/api/status");
  const snapshot = await getJson("/api/whiteboard");
  const scheduler = await getJson("/api/scheduler/status");
  const runs = await getJson("/api/autonomous_runs");
  const heartbeats = await getJson("/api/progress_heartbeats");
  const interrupts = await getJson("/api/approval_interrupts");
  const l8Cockpit = await getJson("/api/l8/cockpit");
  const l9Cockpit = await getJson("/api/l9/meta/cockpit");
  const l10Cockpit = await getJson("/api/l10/cockpit");
  OFFICE_STATE = state;
  $("phase").textContent = `${state.l10_runtime_phase || state.l9_runtime_phase || state.l8_runtime_phase || state.scheduler_runtime_phase || state.whiteboard_runtime_phase || state.current_phase} · ${state.agent_count} recovered agents`;
  renderRoster(state.agents);
  renderWhiteboard(snapshot);
  renderWorkBoard(snapshot.work_board || {});
  renderAgentPanel(state, snapshot);
  renderTimeline(snapshot.timeline || []);
  renderScheduler(scheduler, runs, heartbeats, interrupts);
  renderL8Cockpit(l8Cockpit);
  renderL9Cockpit(l9Cockpit);
  renderL10Cockpit(l10Cockpit);
  $("pending-approvals").innerHTML = list((snapshot.approval_requests || []).map((item) => item.reason).concat(state.pending_approvals || []));
  $("blocked-actions").innerHTML = list(state.blocked_actions);
  if (state.agents.length) openRoom(state.agents.find((agent) => agent.agent_id === "aiden_ceo")?.agent_id || state.agents[0].agent_id);
}

async function act(label, path, payload = {}) {
  const data = await postJson(path, payload);
  $("packet-result").textContent = summarizeActionResult(label, data);
  try {
    await refreshOffice();
  } catch (error) {
    $("packet-result").textContent += `\n\nRefresh warning: ${error.message}. The packet action above still completed.`;
  }
}

function summarizeActionResult(label, data) {
  const lines = [label, ""];
  lines.push(`状态: ${data.ok === false ? "失败" : "完成"}`);
  if (data.message && !data.routing_decision) {
    latestOwnerMessage = data.message;
    latestWorkItemId = "";
    lines.push(`已进入白板: ${data.message.text || data.message.objective || data.message.message_id}`);
    lines.push("下一步: 点 “2. Aiden 拆任务”。");
  }
  if (data.routing_decision) {
    const decision = data.routing_decision;
    if (data.message) latestOwnerMessage = data.message;
    if (data.work_item?.work_item_id) latestWorkItemId = data.work_item.work_item_id;
    lines.push(`Aiden 分派: ${decision.primary_agent} + ${(decision.supporting_agents || []).join(", ")}`);
    lines.push(`任务: ${data.work_item?.title || decision.work_item_id}`);
    if (data.reused_existing_work_item) lines.push("说明: 这是同一条白板消息，未重复创建新任务。");
    lines.push("下一步: 点 “3. 团队工作一轮”。");
  }
  if (data.items_processed) {
    lines.push(`处理任务数: ${data.items_processed.length}`);
    (data.results || []).slice(0, 3).forEach((result) => {
      const item = result.work_item || {};
      lines.push(`- ${item.title || item.work_item_id}: ${item.status || "updated"}`);
      lines.push(`  团队回复: ${(result.agent_replies || []).map((reply) => reply.agent_id).join(", ")}`);
      if (result.approval_request) lines.push(`  需要审批: ${result.approval_request.reason}`);
    });
    lines.push("下一步: 看“团队白板”，或者点 “4. 生成总结”。");
  }
  if (data.agent_replies) {
    lines.push(`团队回复: ${data.agent_replies.map((reply) => reply.agent_id).join(", ")}`);
  }
  if (data.completion_report) {
    lines.push(`总结: ${data.completion_report.summary}`);
    lines.push(`下一步: ${data.completion_report.next_owner_action}`);
  }
  if (data.next_step && !lines.some((line) => line.includes(data.next_step))) lines.push(`下一步: ${data.next_step}`);
  lines.push("");
  lines.push("外部动作: 没有。邮件、客户联系、发布、付款、核心写回都没有执行。");
  return lines.join("\n");
}

async function sendTeamInstruction() {
  const payload = {
    target: $("whiteboard-target").value,
    text: $("whiteboard-text").value,
    objective: $("whiteboard-objective").value,
  };
  setSendStatus("Sending local team instruction...", "warn");
  try {
    const data = await postJson("/api/whiteboard/message", payload);
    setSendStatus("Sent to the local whiteboard queue. Next: Route with Aiden or run a team work cycle.", "ok");
    return {mode: "whiteboard_message", ...data};
  } catch (error) {
    if (error.status !== 404) throw error;
    const legacyPayload = {
      task_title: payload.objective || "Owner team instruction",
      task_description: payload.text,
    };
    const targetAgent = payload.target && payload.target !== "whole_team" ? payload.target : "aiden_ceo";
    const result = {
      ok: true,
      compatibility_fallback: true,
      reason: "The currently running server process is older than the page script and does not expose /api/whiteboard/message.",
      next_step: "Restart the Labs Office server for the full whiteboard runtime; this fallback still writes local instruction packets now.",
      team_task: null,
      owner_message: null,
    };
    try {
      result.team_task = await postJson("/api/team_task", legacyPayload);
    } catch (teamTaskError) {
      result.team_task_error = teamTaskError.message;
    }
    try {
      result.owner_message = await postJson("/api/message", {
        target_agent: targetAgent,
        message_text: payload.text,
        objective: payload.objective,
        urgency: "normal",
      });
    } catch (ownerMessageError) {
      result.owner_message_error = ownerMessageError.message;
    }
    if (!result.team_task && !result.owner_message) throw error;
    setSendStatus("Sent using compatibility fallback. A local team task/message packet was created; restart the server when convenient for full routing.", "warn");
    return result;
  }
}

$("refresh-button").addEventListener("click", refreshOffice);
document.querySelectorAll("[data-office-mode-button]").forEach((button) => {
  button.addEventListener("click", () => setOfficeMode(button.dataset.officeModeButton));
});
try {
  setOfficeMode(localStorage.getItem("labsOfficeMode") || "meeting");
} catch (error) {
  setOfficeMode("meeting");
}
document.querySelectorAll(".template-chip").forEach((button) => {
  button.addEventListener("click", () => {
    const template = quickTemplates[button.dataset.template];
    if (!template) return;
    $("whiteboard-text").value = template.text;
    $("whiteboard-objective").value = template.objective;
    setSendStatus("Template loaded. Edit it if needed, then click 1. 发给团队.", "ok");
  });
});
$("whiteboard-message-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await sendTeamInstruction();
    if (data.message) latestOwnerMessage = data.message;
    $("packet-result").textContent = summarizeActionResult("Team instruction submitted", data);
    try {
      await refreshOffice();
    } catch (error) {
      $("packet-result").textContent += `\n\nRefresh warning: ${error.message}. The instruction packet was still created.`;
    }
  } catch (error) {
    setSendStatus(`Could not submit instruction: ${error.message}`, "error");
    $("packet-result").textContent = `Team instruction failed\n${error.message}`;
  }
});
$("route-button").addEventListener("click", () => act("Aiden routing decision", "/api/route", latestOwnerMessage ? {message: latestOwnerMessage} : {}));
$("work-cycle-button").addEventListener("click", () => act("Safe work cycle", "/api/work_cycle"));
$("team-cycle-button").addEventListener("click", () => {
  if (latestWorkItemId) {
    act("Team work cycle", "/api/work_cycle", {work_item_id: latestWorkItemId});
  } else {
    act("Team work cycle", "/api/team_work_cycle", {max_work_items_per_cycle: 1});
  }
});
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
$("l9-assets-button").addEventListener("click", () => act("L9 internal asset inventory built", "/api/l9/assets/build"));
$("l9-discover-button").addEventListener("click", () => act("L9 opportunities discovered", "/api/l9/opportunities/discover"));
$("l9-money-paths-button").addEventListener("click", () => act("L9 money paths generated", "/api/l9/money_paths/generate"));
$("l9-rankings-button").addEventListener("click", () => act("L9 rankings built", "/api/l9/rankings/build"));
$("l9-decision-packets-button").addEventListener("click", () => act("L9 owner decision packets built", "/api/l9/decision_packets/build"));
$("l9-review-button").addEventListener("click", () => act("L9 opportunity review decision", "/api/l9/opportunity_reviews/decide", {
  decision_packet_id: $("l9-decision-packet-select").value,
  decision: $("l9-review-decision-select").value,
  decision_note: $("l9-review-note").value,
}));
$("l9-execution-plan-button").addEventListener("click", () => act("L9 execution plan generated", "/api/l9/execution_plans/build", {
  money_path_id: $("l9-money-path-select").value,
}));
$("l9-bridge-button").addEventListener("click", () => act("L9 bridge packet generated", "/api/l9/l8_bridge/build", {
  execution_plan_id: $("l9-execution-plan-select").value,
}));
$("l9-residual-button").addEventListener("click", () => act("L9 portfolio residual generated", "/api/l9/portfolio_residuals/build", {
  money_path_id: $("l9-money-path-select").value,
  actual_signal: $("l9-signal-select").value,
}));
$("l9-learning-button").addEventListener("click", () => act("L9 portfolio learning candidate generated", "/api/l9/portfolio_learning_candidates/build"));
$("l9-refresh-button").addEventListener("click", refreshOffice);
$("l10-create-default-button").addEventListener("click", () => act("L10 default mission created", "/api/l10/missions/create_default"));
$("l10-create-custom-button").addEventListener("click", () => act("L10 custom mission created", "/api/l10/missions/create", {
  title: $("l10-custom-title").value,
  owner_goal: $("l10-custom-goal").value,
  allowed_permission_tier: $("l10-tier-select").value,
}));
$("l10-plan-button").addEventListener("click", () => act("L10 mission plan built", "/api/l10/mission_plan/build"));
$("l10-run-cycle-button").addEventListener("click", () => act("L10 bounded mission cycle", "/api/l10/mission_runner/run_cycle", {max_cycles: 1}));
$("l10-run-mission-button").addEventListener("click", () => act("L10 delegated mission run", "/api/l10/mission_runner/run_bounded", {max_cycles: 2}));
$("l10-research-plan-button").addEventListener("click", () => act("L10 research plan built", "/api/l10/research_plan/build"));
$("l10-fixture-research-button").addEventListener("click", () => act("L10 fixture research demo", "/api/l10/research/run_fixture_demo"));
$("l10-live-research-button").addEventListener("click", () => act("L10 configured live read-only check", "/api/l10/research/run_configured_live_read_only", {explicitly_enabled: false}));
$("l10-signals-button").addEventListener("click", () => act("L10 opportunity signals extracted", "/api/l10/opportunity_signals/extract"));
$("l10-brief-button").addEventListener("click", () => act("L10 meta strategy brief built", "/api/l10/meta_strategy_brief/build"));
$("l10-action-plan-button").addEventListener("click", () => act("L10 action plan built", "/api/l10/action_plan/build"));
$("l10-escalations-button").addEventListener("click", () => act("L10 escalation packets built", "/api/l10/escalations/build"));
$("l10-escalation-decide-button").addEventListener("click", () => act("L10 escalation review decision", "/api/l10/escalations/decide", {
  escalation_id: $("l10-escalation-select").value,
  decision: $("l10-escalation-decision-select").value,
  decision_note: $("l10-escalation-note").value,
}));
$("l10-l9-update-button").addEventListener("click", () => act("L10 L9 portfolio update packet built", "/api/l10/l9_portfolio_update/build"));
$("l10-l8-escalation-button").addEventListener("click", () => act("L10 L8 manual escalation packet built", "/api/l10/l8_action_loop_escalation/build"));
$("l10-completion-button").addEventListener("click", () => act("L10 mission completion report built", "/api/l10/completion_report/build"));
$("l10-refresh-button").addEventListener("click", refreshOffice);

refreshOffice().catch((error) => { $("packet-result").textContent = `Office failed to load: ${error}`; });
