#!/usr/bin/env python3
"""Build the real local Labs Office Web UI runtime state and assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_real_labs_office_web_ui"
LEGACY_OUT = ROOT / "l7_labs_office_legacy_integration"
GENERATED_AT = "2026-04-30T00:00:00Z"
LOCAL_URL = "http://127.0.0.1:8765"

PACKET_DIRS = [
    "runtime_packets/owner_messages",
    "runtime_packets/team_tasks",
    "runtime_packets/routing_decisions",
    "runtime_packets/agent_inboxes",
]

FORBIDDEN_ACTIONS = [
    "external outreach",
    "email sending",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "grant/RFP submission",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

APPROVAL_REQUIRED_FOR = [
    "outreach",
    "publication",
    "payment",
    "account creation",
    "form submission",
    "grant/RFP submission",
    "customer contact",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

ALLOWED_LOCAL_ACTIONS = [
    "local office message packet creation",
    "local team task packet creation",
    "internal analysis",
    "draft-only work",
    "approval request preparation",
    "controlled read-only observation if separately configured",
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(relative_path: str, data: Any) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(relative_path: str, text: str) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def audit_existing_html() -> dict[str, Any]:
    html_path = LEGACY_OUT / "office_home/labs_office_home.html"
    exists = html_path.exists()
    text = html_path.read_text(encoding="utf-8") if exists else ""
    size = len(text.encode("utf-8")) if exists else 0
    lower = text.lower()
    audit = {
        "schema_version": "v0",
        "milestone_id": "L7.4R",
        "packet_type": "existing_html_audit",
        "generated_at_utc": GENERATED_AT,
        "audited_path": str(html_path),
        "exists": exists,
        "size_bytes": size,
        "has_agent_cards": "agent-card" in lower or "team rooms" in lower,
        "has_links_to_agent_rooms": "agent_rooms/" in lower,
        "has_message_form": "<form" in lower and "message" in lower,
        "has_team_task_form": "<form" in lower and "team" in lower and "task" in lower,
        "has_api_runtime": "/api/" in lower or "fetch(" in lower,
        "owner_usable": False,
        "deficiencies": [],
        "replacement_created": True,
    }
    if not exists:
        audit["deficiencies"].append("missing")
    if size == 0:
        audit["deficiencies"].append("empty")
    if not audit["has_message_form"]:
        audit["deficiencies"].append("no owner-to-agent message form")
    if not audit["has_team_task_form"]:
        audit["deficiencies"].append("no whole-team task form")
    if not audit["has_api_runtime"]:
        audit["deficiencies"].append("no local API runtime")
    if not audit["has_links_to_agent_rooms"]:
        audit["deficiencies"].append("no agent room links")
    if audit["deficiencies"]:
        audit["owner_usable"] = False
    else:
        audit["owner_usable"] = True
    return audit


def agent_room(agent_id: str) -> dict[str, Any]:
    return load_json(LEGACY_OUT / "agent_rooms" / f"{agent_id}_room.json", {})


def compact_agent(agent: dict[str, Any]) -> dict[str, Any]:
    room = agent_room(agent["agent_id"])
    return {
        "agent_id": agent["agent_id"],
        "display_name": agent["display_name"],
        "legacy_role": agent["legacy_role"],
        "current_status": agent.get("current_status", "unknown"),
        "can_accept_tasks": agent.get("can_accept_tasks", False),
        "can_self_work": agent.get("can_self_work", False),
        "known_responsibilities": agent.get("known_responsibilities", []),
        "brain_profile_refs": agent.get("brain_profile_refs", [])[:8],
        "source_evidence_summary": (
            agent.get("source_evidence", [{}])[0].get("excerpt", "needs review")
            if agent.get("source_evidence")
            else "needs review"
        ),
        "room": room,
    }


def commercial_summary() -> dict[str, Any]:
    selected_path = load_json(
        ROOT / "l7_approval_ready_offer_validation_workflow/selected_cash_path/selected_cash_path.json",
        {},
    )
    offer = load_json(
        ROOT / "l7_approval_ready_offer_validation_workflow/service_offer_definition/service_offer_definition.json",
        {},
    )
    money = load_json(ROOT / "l7_meta_development_money_path_engine/l7_2_summary.json", {})
    return {
        "selected_cash_path": selected_path.get("path_name")
        or selected_path.get("selected_cash_path", "Founder AI Workflow Audit and CEO Command Brief Sprint"),
        "service_offer": offer.get("offer_name", "Founder AI Workflow Audit & CEO Command Brief Sprint"),
        "primary_shortest_cash_path": money.get("primary_shortest_cash_path", "path_001"),
        "status": "first revenue readiness is prepared; external action remains approval-gated",
    }


def build_runtime_state() -> dict[str, Any]:
    registry = load_json(LEGACY_OUT / "original_team_registry/original_team_registry.json", {"agents": []})
    home = load_json(LEGACY_OUT / "office_home/labs_office_home.json", {})
    queue = load_json(LEGACY_OUT / "team_work_queue/team_work_queue.json", {"work_items": []})
    agents = [compact_agent(agent) for agent in registry.get("agents", [])]
    packet_dirs = {}
    for relative in PACKET_DIRS:
        path = OUT / relative
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").write_text("local runtime packet directory\n", encoding="utf-8")
        packet_dirs[relative.split("/")[-1]] = str(path.relative_to(ROOT))
    return {
        "schema_version": "v0",
        "milestone_id": "L7.4R",
        "packet_type": "office_runtime_state",
        "generated_at_utc": GENERATED_AT,
        "local_url": LOCAL_URL,
        "current_phase": "Real Labs Office Web UI Runtime",
        "legacy_source": "l7_labs_office_legacy_integration",
        "agent_count": len(agents),
        "agents": agents,
        "work_queue": queue.get("work_items", []),
        "pending_approvals": home.get(
            "pending_approvals",
            ["first manual outreach", "recipient selection", "price quote", "payment method"],
        ),
        "blocked_actions": FORBIDDEN_ACTIONS,
        "approval_required_for": APPROVAL_REQUIRED_FOR,
        "allowed_local_actions": ALLOWED_LOCAL_ACTIONS,
        "commercial_path_summary": commercial_summary(),
        "packet_dirs": packet_dirs,
        "next_commands": [
            "bash scripts/run_l7_labs_office_web.sh --mode serve",
            "bash scripts/run_l7_labs_office_web.sh --mode status",
            "bash scripts/run_l7_labs_office_web.sh --mode smoke",
        ],
        "no_coo_invented_as_legacy_member": True,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
    }


def write_assets() -> None:
    write_text(
        "templates/index.html",
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Y*Bridge Labs Office</title>
  <link rel="stylesheet" href="/static/office.css">
</head>
<body>
  <header class="hero">
    <p class="eyebrow">Local only: 127.0.0.1</p>
    <h1>Y*Bridge Labs Office</h1>
    <p id="phase">Loading office state...</p>
    <div class="actions">
      <code>bash scripts/run_l7_labs_office_web.sh --mode serve</code>
      <button id="refresh-button" type="button">Refresh Office</button>
    </div>
  </header>

  <main>
    <section class="panel">
      <h2>Recovered Legacy Team</h2>
      <p>This roster is loaded from L7.4 legacy recovery artifacts. No COO is invented as a legacy member.</p>
      <div id="roster" class="card-grid"></div>
    </section>

    <section class="panel split">
      <div>
        <h2>Agent Room</h2>
        <div id="agent-room" class="room-card">Select an agent room.</div>
      </div>
      <div>
        <h2>Work Queue</h2>
        <ul id="work-queue"></ul>
      </div>
    </section>

    <section class="panel split">
      <form id="message-form" class="office-form">
        <h2>Send Message To Agent</h2>
        <label>Target agent
          <select id="target-agent" name="target_agent"></select>
        </label>
        <label>Objective
          <input id="message-objective" name="objective" value="Ask for a safe internal recommendation">
        </label>
        <label>Message
          <textarea id="message-text" name="message_text" required>Hi Aiden, please route this safely through the original Y*Bridge Labs team.</textarea>
        </label>
        <label>Urgency
          <select id="message-urgency" name="urgency">
            <option>normal</option>
            <option>high</option>
            <option>low</option>
          </select>
        </label>
        <button type="submit">Create Local Message Packet</button>
      </form>

      <form id="team-task-form" class="office-form">
        <h2>Send Task To Whole Team</h2>
        <label>Task title
          <input id="task-title" name="task_title" value="Prepare next safe Labs Office work order">
        </label>
        <label>Task description
          <textarea id="task-description" name="task_description" required>Ask Aiden to route this task to the original team. No external action, no writeback.</textarea>
        </label>
        <button type="submit">Create Local Team Work Order</button>
      </form>
    </section>

    <section class="panel split">
      <div>
        <h2>Pending Approvals</h2>
        <ul id="pending-approvals"></ul>
      </div>
      <div>
        <h2>Blocked Actions</h2>
        <ul id="blocked-actions"></ul>
      </div>
    </section>

    <section class="panel">
      <h2>Commercial Path</h2>
      <div id="commercial-path"></div>
    </section>

    <section class="panel">
      <h2>Packet Result</h2>
      <pre id="packet-result">No packet created yet.</pre>
    </section>
  </main>
  <script src="/static/office.js"></script>
</body>
</html>
""",
    )
    write_text(
        "static/office.css",
        """
:root {
  --ink: #17312b;
  --muted: #65736f;
  --paper: #f8f1e7;
  --card: #fffaf0;
  --line: #d8c7a8;
  --accent: #d96d35;
  --accent-dark: #7b341c;
  --green: #2f6f58;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(217,109,53,.25), transparent 32rem),
    linear-gradient(135deg, #fbf5e8, #eaf4ed);
}
.hero {
  padding: 42px 6vw 28px;
  border-bottom: 1px solid var(--line);
}
.eyebrow { color: var(--accent-dark); letter-spacing: .08em; text-transform: uppercase; font-size: 12px; }
h1 { margin: 0; font-size: clamp(36px, 6vw, 72px); line-height: .95; }
h2 { margin-top: 0; }
main { padding: 24px 6vw 60px; display: grid; gap: 20px; }
.panel {
  background: rgba(255,250,240,.86);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 18px 45px rgba(78, 57, 31, .08);
}
.split { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; }
.agent-card, .room-card {
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 18px;
  padding: 16px;
}
.agent-card button, button {
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  background: var(--ink);
  color: white;
  cursor: pointer;
}
.agent-card button:hover, button:hover { background: var(--accent-dark); }
.role { color: var(--accent-dark); font-weight: 700; }
.muted { color: var(--muted); }
.office-form { display: grid; gap: 12px; }
label { display: grid; gap: 6px; font-weight: 700; }
input, select, textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  font: inherit;
  background: #fffdf8;
}
textarea { min-height: 110px; }
pre {
  white-space: pre-wrap;
  background: #17312b;
  color: #f8f1e7;
  border-radius: 16px;
  padding: 16px;
  overflow: auto;
}
code { background: rgba(23,49,43,.08); padding: 6px 8px; border-radius: 8px; }
.actions { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-top: 18px; }
@media (max-width: 820px) {
  .split { grid-template-columns: 1fr; }
}
""",
    )
    write_text(
        "static/office.js",
        """
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
""",
    )


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = audit_existing_html()
    state = build_runtime_state()
    write_assets()
    write_json("existing_html_audit.json", audit)
    write_text(
        "existing_html_audit.md",
        f"""
# Existing Labs Office HTML Audit

Audited file: `{audit['audited_path']}`

- Exists: {audit['exists']}
- Size bytes: {audit['size_bytes']}
- Links to agent rooms: {audit['has_links_to_agent_rooms']}
- Has message form: {audit['has_message_form']}
- Has team task form: {audit['has_team_task_form']}
- Has API runtime: {audit['has_api_runtime']}
- Owner usable: {audit['owner_usable']}
- Replacement created: {audit['replacement_created']}

Deficiencies:
{chr(10).join(f"- {item}" for item in audit['deficiencies'])}
""",
    )
    write_json("office_runtime_state.json", state)
    write_json(
        "office_web_no_action_receipt.json",
        {
            "schema_version": "v0",
            "milestone_id": "L7.4R",
            "packet_type": "office_web_no_action_receipt",
            "generated_at_utc": GENERATED_AT,
            "binds_localhost_only": True,
            "external_side_effects_occurred": False,
            "customer_contacted": False,
            "email_sent": False,
            "form_submitted": False,
            "payment_occurred": False,
            "publication_occurred": False,
            "core_writeback_occurred": False,
            "secret_printed_stored_in_repo": False,
            "ystar_bridge_labs_modified": False,
            "y_star_gov_modified": False,
            "gov_mcp_modified": False,
            "db_log_wal_shm_active_agent_marker_content_read": False,
            "ask_user_url_occurred": False,
        },
    )
    summary = {
        "schema_version": "v0",
        "milestone_id": "L7.4R",
        "packet_type": "web_ui_summary",
        "generated_at_utc": GENERATED_AT,
        "real_office_web_ui_created": True,
        "local_url": LOCAL_URL,
        "agent_count": state["agent_count"],
        "agent_cards_generated": state["agent_count"],
        "message_form_available": True,
        "team_task_form_available": True,
        "local_packet_creation_supported": True,
        "api_endpoints": [
            "GET /",
            "GET /api/status",
            "GET /api/roster",
            "GET /api/agents/<agent_id>",
            "GET /api/work_queue",
            "GET /api/pending_approvals",
            "POST /api/message",
            "POST /api/team_task",
        ],
        "existing_html_owner_usable": audit["owner_usable"],
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
        "no_coo_invented_as_legacy_member": True,
    }
    write_json("web_ui_summary.json", summary)
    write_text(
        "web_ui_summary.md",
        f"""
# L7.4R Real Labs Office Web UI Runtime

The prior `labs_office_home.html` was audited and found owner-usable: **{audit['owner_usable']}**.

This sprint creates a real local office runtime at:

`{LOCAL_URL}`

Run:

`bash scripts/run_l7_labs_office_web.sh --mode serve`

The page shows the recovered Y*Bridge Labs team, agent rooms, work queue, pending approvals, blocked actions, and local-only message/team task forms that create JSON packets without external side effects.
""",
    )
    return summary


def main() -> None:
    summary = build()
    print(f"real_office_web_ui_created: {summary['real_office_web_ui_created']}")
    print(f"local_url: {summary['local_url']}")
    print(f"agent_count: {summary['agent_count']}")
    print(f"next_command: {summary['next_one_command_action']}")


if __name__ == "__main__":
    main()
