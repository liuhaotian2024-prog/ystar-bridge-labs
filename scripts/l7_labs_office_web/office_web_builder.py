#!/usr/bin/env python3
"""Build the real local Labs Office Web UI runtime state and assets."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from work_cycle_engine import create_demo_scenario
from whiteboard_store import ensure_dirs


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "l7_real_labs_office_web_ui"
L75_OUT = ROOT / "l7_labs_whiteboard_collaboration_runtime"
LEGACY_OUT = ROOT / "l7_labs_office_legacy_integration"
GENERATED_AT = "2026-04-30T00:00:00Z"
LOCAL_URL = "http://127.0.0.1:8771"

from l7_labs_team_self_work_scheduler.manifest_builder import build_manifest as build_l76_manifest  # noqa: E402
from l8_first_cash_path_operating_loop.l8_manifest_builder import build_manifest as build_l8_manifest  # noqa: E402
from l9_meta_development_opportunity_runtime.l9_manifest_builder import build_manifest as build_l9_manifest  # noqa: E402
from l10_delegated_live_meta_development_runtime.l10_manifest_builder import build_manifest as build_l10_manifest  # noqa: E402

PACKET_DIRS = [
    "runtime_packets/owner_messages",
    "runtime_packets/team_tasks",
    "runtime_packets/routing_decisions",
    "runtime_packets/agent_inboxes",
    "runtime_packets/whiteboard_threads",
    "runtime_packets/agent_replies",
    "runtime_packets/work_items",
    "runtime_packets/work_cycles",
    "runtime_packets/completion_reports",
    "runtime_packets/approval_requests",
    "runtime_packets/autonomous_runs",
    "runtime_packets/scheduler_ticks",
    "runtime_packets/progress_heartbeats",
    "runtime_packets/approval_interrupts",
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


def write_l75_json(relative_path: str, data: Any) -> None:
    path = L75_OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_l75_md(relative_path: str, text: str) -> None:
    path = L75_OUT / relative_path
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
    ensure_dirs()
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
        "whiteboard_runtime_phase": "Real Labs Whiteboard Collaboration & Team Work Runtime",
        "scheduler_runtime_phase": "L7.6 Labs Team Self-Work Scheduler & Autonomous Task Loop",
        "l8_runtime_phase": "L8.0 First Cash Path Operating Loop",
        "l9_runtime_phase": "L9.0 Meta-Development Opportunity & Execution Runtime",
        "l10_runtime_phase": "L10.0 Delegated Live Meta-Development Work Runtime",
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
        "whiteboard_features": [
            "team whiteboard chat",
            "Aiden routing",
            "team work board",
            "agent replies",
            "safe work cycles",
            "bounded scheduler self-work loop",
            "scheduler ticks",
            "progress heartbeats",
            "approval interruptions",
            "progress timeline",
            "approval queue",
            "completion reports",
        ],
        "scheduler_features": [
            "safe work-item classification",
            "eligible task selection",
            "bounded local autonomous cycles",
            "progress heartbeat packets",
            "approval interruption packets",
            "completion report aggregation",
        ],
        "l8_features": [
            "first cash path cockpit",
            "commercial action queue",
            "owner approval center",
            "manual-send packet generation",
            "customer feedback intake",
            "commercial residual analysis",
            "review-gated learning candidates",
        ],
        "l9_features": [
            "internal asset inventory",
            "opportunity discovery portfolio",
            "money path generation",
            "multi-lens opportunity ranking",
            "owner opportunity review center",
            "manual-send-only execution plans",
            "L8 action loop bridge packets",
            "portfolio residuals",
            "review-gated portfolio learning candidates",
        ],
        "l10_features": [
            "delegated meta-development missions",
            "permission tiers",
            "bounded research budgets",
            "mission plan and team-task decomposition",
            "fixture-backed research demo",
            "strategy brief and action plan",
            "approval escalation packets",
            "mission completion reports",
        ],
        "work_board_columns": ["Inbox", "Interpreting", "Assigned", "In Progress", "Waiting for Approval", "Blocked", "Done"],
        "packet_dirs": packet_dirs,
        "next_commands": [
            "bash scripts/run_l7_labs_office_web.sh --mode serve",
            "bash scripts/run_l7_labs_office_web.sh --mode status",
            "bash scripts/run_l7_labs_office_web.sh --mode demo",
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
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Aiden Chat</title>
  <link rel="stylesheet" href="/static/office.css">
</head>
<body>
  <main class="chat-shell">
    <section class="chat-card">
      <header class="chat-header">
        <p class="eyebrow">LOCAL ONLY · AIDEN CEO CHAT · NO EXTERNAL SENDING</p>
        <h1>和 Aiden 讨论</h1>
        <p>这里只有一个功能：你问问题，Aiden 用 CEO 视角回复你。没有团队看板、没有 L8/L9/L10、没有外发。</p>
      </header>

      <section id="chat-history" class="chat-history" aria-live="polite">
        <div class="message aiden">
          <strong>Aiden</strong>
          <p>我在。你直接说问题就行，我会尽量用清楚的人话回答。</p>
        </div>
      </section>

      <form id="aiden-chat-form" class="chat-form">
        <label for="aiden-message">你想跟 Aiden 讨论什么？</label>
        <textarea id="aiden-message" required placeholder="比如：Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？"></textarea>
        <button type="submit">发送给 Aiden</button>
        <p id="chat-status" class="status">本地对话，不会发邮件、不会联系客户、不会发布。</p>
      </form>
    </section>
  </main>
  <script src="/static/office.js?v=aiden-chat-v1"></script>
</body>
</html>
""",
    )
    write_text(
        "static/office.css",
        """
:root {
  --bg: #080b0f;
  --panel: #111821;
  --panel-2: #0d131a;
  --text: #edf7f3;
  --muted: #91a39d;
  --line: rgba(255,255,255,.1);
  --accent: #2cf59a;
  --aiden: #35c8ff;
  --owner: #ffcf70;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at 10% 0%, rgba(44,245,154,.18), transparent 28rem),
    radial-gradient(circle at 90% 20%, rgba(53,200,255,.13), transparent 24rem),
    linear-gradient(135deg, #07090d, #101820 55%, #07110d);
}
.chat-shell {
  width: min(920px, calc(100vw - 28px));
  min-height: 100vh;
  margin: 0 auto;
  padding: 28px 0;
  display: grid;
  place-items: center;
}
.chat-card {
  width: 100%;
  min-height: min(820px, calc(100vh - 56px));
  display: grid;
  grid-template-rows: auto 1fr auto;
  overflow: hidden;
  background: rgba(17,24,33,.94);
  border: 1px solid var(--line);
  border-radius: 28px;
  box-shadow: 0 28px 90px rgba(0,0,0,.35);
}
.chat-header { padding: 28px 30px 18px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 12px; color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: .12em; }
h1 { margin: 0; font-size: clamp(36px, 7vw, 76px); line-height: .9; letter-spacing: -.07em; }
.chat-header p:last-child { max-width: 680px; color: var(--muted); font-size: 16px; line-height: 1.7; }
.chat-history { padding: 24px 30px; display: flex; flex-direction: column; gap: 14px; overflow: auto; background: rgba(0,0,0,.13); }
.message { max-width: 82%; padding: 14px 16px; border: 1px solid var(--line); border-radius: 18px; line-height: 1.65; }
.message strong { display: block; margin-bottom: 6px; font-size: 13px; letter-spacing: .04em; }
.message p { margin: 0; white-space: pre-wrap; }
.message.owner { margin-left: auto; background: rgba(255,207,112,.08); border-color: rgba(255,207,112,.24); }
.message.owner strong { color: var(--owner); }
.message.aiden { background: rgba(53,200,255,.08); border-color: rgba(53,200,255,.22); }
.message.aiden strong { color: var(--aiden); }
.chat-form { padding: 18px 30px 26px; display: grid; gap: 10px; border-top: 1px solid var(--line); background: var(--panel-2); }
label { color: var(--muted); font-size: 14px; font-weight: 700; }
textarea { width: 100%; min-height: 110px; resize: vertical; padding: 14px; border: 1px solid rgba(255,255,255,.14); border-radius: 16px; color: var(--text); background: rgba(255,255,255,.055); font: inherit; }
button { width: fit-content; border: 0; border-radius: 14px; padding: 12px 18px; color: #06100c; background: linear-gradient(135deg, var(--accent), var(--aiden)); font: inherit; font-weight: 900; cursor: pointer; }
button:disabled { opacity: .55; cursor: wait; }
.status { margin: 0; color: var(--muted); font-size: 13px; }
@media (max-width: 720px) {
  .chat-shell { width: 100%; padding: 0; }
  .chat-card { min-height: 100vh; border-radius: 0; }
  .message { max-width: 95%; }
  .chat-header, .chat-history, .chat-form { padding-left: 18px; padding-right: 18px; }
}
""",
    )
    write_text(
        "static/office.js",
        """
const historyEl = document.getElementById("chat-history");
const form = document.getElementById("aiden-chat-form");
const textarea = document.getElementById("aiden-message");
const statusEl = document.getElementById("chat-status");

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
  return `
    <div class="message ${isOwner ? "owner" : "aiden"}">
      <strong>${isOwner ? "你" : "Aiden"}</strong>
      <p>${escapeHtml(turn.text)}</p>
    </div>`;
}

function renderHistory(history) {
  const turns = history && history.length ? history : [{
    speaker: "aiden_ceo",
    text: "我在。你直接说问题就行，我会尽量用清楚的人话回答。",
  }];
  historyEl.innerHTML = turns.slice(-30).map(renderTurn).join("");
  historyEl.scrollTop = historyEl.scrollHeight;
}

async function loadHistory() {
  const response = await fetch("/api/aiden_chat");
  if (!response.ok) return;
  const data = await response.json();
  renderHistory(data.history || []);
}

async function sendMessage(text) {
  const response = await fetch("/api/aiden_chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text}),
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || "Aiden 没有成功回复。");
  }
  renderHistory(data.history || []);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = textarea.value.trim();
  if (!text) return;
  textarea.value = "";
  statusEl.textContent = "Aiden 正在本地回复...";
  form.querySelector("button").disabled = true;
  renderHistory([
    ...Array.from(historyEl.querySelectorAll(".message")).map((node) => ({
      speaker: node.classList.contains("owner") ? "owner" : "aiden_ceo",
      text: node.querySelector("p")?.textContent || "",
    })),
    {speaker: "owner", text},
  ]);
  try {
    await sendMessage(text);
    statusEl.textContent = "已本地回复。没有外发、没有邮件、没有客户联系。";
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    form.querySelector("button").disabled = false;
    textarea.focus();
  }
});

loadHistory();
""",
    )
    return
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
    <p class="eyebrow">Local-only Labs Office · no external sending</p>
    <h1>Y*Bridge Labs Office</h1>
    <p class="subtitle">一个简单的白板办公室：你说目标，Aiden 拆任务，团队本地工作，结果和审批停在这里。</p>
    <p id="phase">Loading recovered team and work board...</p>
    <div class="actions">
      <button id="refresh-button" type="button">Refresh Status</button>
    </div>
  </header>

  <section class="mode-switch" aria-label="Office mode switcher">
    <div>
      <p class="section-label">Two Modes</p>
      <h2>先开会，再看执行</h2>
      <p class="muted">不用在一页里同时消化所有东西。讨论问题时用“讨论开会”，想追踪团队内部任务时切到“执行看板”。</p>
    </div>
    <div class="mode-buttons">
      <button class="mode-button active" type="button" data-office-mode-button="meeting">讨论开会模式</button>
      <button class="mode-button" type="button" data-office-mode-button="execution">执行看板模式</button>
    </div>
  </section>

  <main class="office-grid">
    <div id="message-form" hidden></div>
    <div id="team-task-form" hidden></div>
    <select id="target-agent" hidden></select>
    <section class="panel command-center office-mode-panel meeting-mode">
      <div class="section-label">Start Here</div>
      <h2>把目标交给团队</h2>
      <p class="muted">不用理解 L8/L9/L10。先写一句你想让团队完成的事，然后按下面 3 步走。</p>
      <div class="template-row">
        <button class="template-chip" type="button" data-template="first-cash">最快拿到第一笔钱</button>
        <button class="template-chip" type="button" data-template="thirty-day">30 天发展计划</button>
        <button class="template-chip" type="button" data-template="opportunities">寻找新赚钱机会</button>
      </div>
      <form id="whiteboard-message-form" class="office-form">
        <label>Target
          <select id="whiteboard-target" name="target">
            <option value="whole_team">Whole Team</option>
          </select>
        </label>
        <label>你要团队做什么？
          <textarea id="whiteboard-text" required>团队请一起分析：我们下一步怎么最快拿到第一笔钱，同时不牺牲长期战略？</textarea>
        </label>
        <label>这次任务的目标
          <input id="whiteboard-objective" value="Find the safest fastest first-cash path">
        </label>
        <button class="primary-action" type="submit">1. 发给团队</button>
        <p id="whiteboard-send-status" class="send-status muted">Ready to create a local team instruction packet.</p>
      </form>
      <div class="step-actions">
        <button id="route-button" type="button">2. Aiden 拆任务</button>
        <button id="team-cycle-button" type="button">3. 团队工作一轮</button>
        <button id="completion-button" type="button">4. 生成总结</button>
      </div>
      <details class="mini-help">
        <summary>我应该怎么用？</summary>
        <ol>
          <li>写一句目标，越像对真人团队说话越好。</li>
          <li>点“发给团队”，只会创建本地 packet，不会发到外网。</li>
          <li>点“Aiden 拆任务”，Aiden 会把目标分派给成员。</li>
          <li>点“团队工作一轮”，成员会在下面回复。</li>
        </ol>
      </details>
    </section>

    <section class="panel result-panel office-mode-panel meeting-mode">
      <div class="section-label">Team Replies</div>
      <h2>讨论白板</h2>
      <p class="muted">这里应该只显示当前讨论的消息和团队回复；执行细节放到“执行看板模式”。</p>
      <div id="whiteboard-thread" class="thread"></div>
    </section>

    <section class="panel office-mode-panel meeting-mode">
      <div class="section-label">Result</div>
      <h2>最近一次操作结果</h2>
      <pre id="packet-result">No whiteboard action yet.</pre>
    </section>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Work Board</div>
      <h2>执行看板：内部任务进度</h2>
      <p class="muted">这里看 Aiden 拆出来的任务、团队执行状态、阻塞和完成情况。</p>
      <div id="work-board" class="kanban"></div>
    </section>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Team</div>
      <h2>执行看板：团队成员状态</h2>
      <div id="agent-panel" class="agent-panel"></div>
    </section>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Approvals</div>
      <h2>需要你批准的事情</h2>
      <ul id="pending-approvals"></ul>
      <h3>系统不会自动做的事</h3>
      <ul id="blocked-actions"></ul>
    </section>

    <details class="panel advanced-panel office-mode-panel execution-mode">
      <summary>高级：调度器 / 商业路径 / 委托任务</summary>
      <section class="scheduler-panel">
      <h2>Self-Work Scheduler</h2>
      <p class="muted">自动选择安全的本地任务；遇到外部动作或核心写回会停下来。</p>
      <div class="step-actions">
        <button id="work-cycle-button" type="button">Run One Safe Work Cycle</button>
        <button id="scheduler-once-button" type="button">Run Scheduler Once</button>
        <button id="scheduler-bounded-button" type="button">Run Bounded Self-Work</button>
      </div>
      <div id="scheduler-status" class="scheduler-status">Loading scheduler...</div>
      <h3>Progress Heartbeats</h3>
      <ul id="progress-heartbeats"></ul>
      <h3>Approval Interruptions</h3>
      <ul id="approval-interruptions"></ul>
      <h3>Autonomous Runs</h3>
      <ul id="autonomous-runs"></ul>
      </section>

    <section class="l8-cockpit-panel">
      <h2>L8 First Cash Path Cockpit</h2>
      <p class="muted">Founder AI Workflow Audit & CEO Command Brief Sprint. Manual-send only; no automatic customer contact.</p>
      <div class="step-actions">
        <button id="l8-start-button" type="button">Start First Cash Path Loop</button>
        <button id="l8-build-actions-button" type="button">Build Commercial Action Queue</button>
      </div>
      <div id="l8-cockpit" class="l8-cockpit">Loading first cash path loop...</div>
      <div class="l8-controls">
        <label>Approval action
          <select id="l8-action-select"></select>
        </label>
        <label>Decision
          <select id="l8-decision-select">
            <option value="approve">approve</option>
            <option value="reject">reject</option>
            <option value="request_revision">request revision</option>
            <option value="hold">hold</option>
          </select>
        </label>
        <input id="l8-decision-note" placeholder="Optional owner decision note">
        <button id="l8-decide-button" type="button">Submit Approval Decision</button>
        <label>Manual-send packet
          <select id="l8-manual-packet-select"></select>
        </label>
        <label>Manual status
          <select id="l8-manual-status-select">
            <option value="marked_sent_by_owner">marked sent by owner</option>
            <option value="not_sent">not sent</option>
            <option value="revised_outside_system">revised outside system</option>
            <option value="customer_replied">customer replied</option>
            <option value="no_response">no response</option>
            <option value="interested">interested</option>
            <option value="not_interested">not interested</option>
            <option value="paid_signal">paid signal</option>
            <option value="pilot_accepted">pilot accepted</option>
          </select>
        </label>
        <input id="l8-manual-note" placeholder="Manual action note">
        <button id="l8-mark-manual-button" type="button">Mark Manual Packet</button>
        <label>Feedback status
          <select id="l8-feedback-status-select">
            <option value="no_response">no response</option>
            <option value="interested">interested</option>
            <option value="not_interested">not interested</option>
            <option value="asks_for_more_info">asks for more info</option>
            <option value="wants_call">wants call</option>
            <option value="paid_signal">paid signal</option>
            <option value="pilot_accepted">pilot accepted</option>
            <option value="rejected">rejected</option>
          </select>
        </label>
        <textarea id="l8-feedback-text" placeholder="Owner-entered customer feedback or demo note"></textarea>
        <button id="l8-feedback-button" type="button">Record Feedback</button>
        <button id="l8-residual-button" type="button">Generate Residual</button>
        <button id="l8-learning-button" type="button">Generate Learning Candidate</button>
        <button id="l8-refresh-cockpit-button" type="button">Refresh Cockpit Snapshot</button>
      </div>
    </section>

    <section class="l9-cockpit-panel">
      <h2>L9 Meta-Development Cockpit</h2>
      <p class="muted">Portfolio engine: discover opportunities, rank money paths, select a path, then bridge it into approval-gated L8 action loops.</p>
      <div id="l9-cockpit" class="l9-cockpit">Loading meta-development portfolio...</div>
      <div class="l9-controls">
        <button id="l9-assets-button" type="button">Build Internal Asset Inventory</button>
        <button id="l9-discover-button" type="button">Run Opportunity Discovery</button>
        <button id="l9-money-paths-button" type="button">Generate Money Paths</button>
        <button id="l9-rankings-button" type="button">Rank Opportunities</button>
        <button id="l9-decision-packets-button" type="button">Build Owner Decision Packets</button>
        <label>Decision packet
          <select id="l9-decision-packet-select"></select>
        </label>
        <label>Owner decision
          <select id="l9-review-decision-select">
            <option value="select_for_execution">select for execution</option>
            <option value="reject">reject</option>
            <option value="hold">hold</option>
            <option value="request_revision">request revision</option>
            <option value="request_more_evidence">request more evidence</option>
          </select>
        </label>
        <input id="l9-review-note" placeholder="Optional portfolio decision note">
        <button id="l9-review-button" type="button">Submit Opportunity Review</button>
        <label>Selected money path
          <select id="l9-money-path-select"></select>
        </label>
        <button id="l9-execution-plan-button" type="button">Generate Execution Plan</button>
        <label>Execution plan
          <select id="l9-execution-plan-select"></select>
        </label>
        <button id="l9-bridge-button" type="button">Bridge Selected Path to L8 Action Loop</button>
        <label>Portfolio signal
          <select id="l9-signal-select">
            <option value="no_signal">no signal</option>
            <option value="positive_signal">positive signal</option>
            <option value="pricing_friction">pricing friction</option>
            <option value="target_mismatch">target mismatch</option>
            <option value="offer_mismatch">offer mismatch</option>
            <option value="capability_gap">capability gap</option>
            <option value="channel_mismatch">channel mismatch</option>
          </select>
        </label>
        <button id="l9-residual-button" type="button">Build Portfolio Residual</button>
        <button id="l9-learning-button" type="button">Build Portfolio Learning Candidate</button>
        <button id="l9-refresh-button" type="button">Refresh Meta Cockpit</button>
      </div>
    </section>

    <section class="l10-cockpit-panel">
      <h2>L10 Delegated Mission Cockpit</h2>
      <p class="muted">Create a real delegated meta-development mission, run bounded internal/research work, and escalate risky actions for owner review.</p>
      <div id="l10-cockpit" class="l10-cockpit">Loading delegated mission state...</div>
      <div class="l10-controls">
        <button id="l10-create-default-button" type="button">Create Default Meta-Development Mission</button>
        <label>Custom mission title
          <input id="l10-custom-title" value="Research next 30-day meta-development plan">
        </label>
        <label>Custom mission goal
          <textarea id="l10-custom-goal">Research and formulate the next 30-day meta-development plan for Y*Bridge Labs to maximize the chance of first revenue.</textarea>
        </label>
        <label>Permission tier
          <select id="l10-tier-select">
            <option value="tier_1">Tier 1 read-only external research</option>
            <option value="tier_0">Tier 0 internal only</option>
            <option value="tier_2">Tier 2 preparation, owner-approved execution</option>
          </select>
        </label>
        <button id="l10-create-custom-button" type="button">Create Custom Mission</button>
        <button id="l10-plan-button" type="button">Build Mission Plan</button>
        <button id="l10-run-cycle-button" type="button">Run Bounded Mission Cycle</button>
        <button id="l10-run-mission-button" type="button">Run Delegated Mission</button>
        <button id="l10-research-plan-button" type="button">Build Research Plan</button>
        <button id="l10-fixture-research-button" type="button">Run Fixture-Backed Research Demo</button>
        <button id="l10-live-research-button" type="button">Try Configured Live Read-Only Research</button>
        <button id="l10-signals-button" type="button">Extract Opportunity Signals</button>
        <button id="l10-brief-button" type="button">Build Meta Strategy Brief</button>
        <button id="l10-action-plan-button" type="button">Build Action Plan</button>
        <button id="l10-escalations-button" type="button">Build Escalation Packets</button>
        <label>Escalation
          <select id="l10-escalation-select"></select>
        </label>
        <label>Escalation decision
          <select id="l10-escalation-decision-select">
            <option value="approve">approve</option>
            <option value="reject">reject</option>
            <option value="request_revision">request revision</option>
            <option value="hold">hold</option>
          </select>
        </label>
        <input id="l10-escalation-note" placeholder="Optional owner decision note">
        <button id="l10-escalation-decide-button" type="button">Submit Escalation Review</button>
        <button id="l10-l9-update-button" type="button">Build L9 Portfolio Update Packet</button>
        <button id="l10-l8-escalation-button" type="button">Build L8 Manual Action Escalation Packet</button>
        <button id="l10-completion-button" type="button">Build Mission Completion Report</button>
        <button id="l10-refresh-button" type="button">Refresh L10 Cockpit</button>
      </div>
    </section>
    </details>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Rooms</div>
      <h2>成员房间</h2>
      <div id="agent-room" class="room-card">Select an agent room.</div>
    </section>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Timeline</div>
      <h2>工作时间线</h2>
      <ol id="progress-timeline" class="timeline"></ol>
    </section>

    <section class="panel office-mode-panel execution-mode">
      <div class="section-label">Roster</div>
      <h2>原始团队</h2>
      <p>No COO is invented. The roster below is loaded from L7.4 recovery artifacts.</p>
      <div id="roster" class="card-grid"></div>
    </section>
  </main>
  <script src="/static/office.js?v=simple-office-v3"></script>
</body>
</html>
""",
    )
    write_text(
        "static/office.css",
        """
:root {
  --ink: #17251f;
  --muted: #64726d;
  --paper: #f7efe1;
  --card: #fffaf0;
  --line: #dbc8a7;
  --accent: #cf6636;
  --blue: #214e75;
  --green: #2f6f58;
  --red: #8f3328;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(207,102,54,.28), transparent 30rem),
    radial-gradient(circle at bottom right, rgba(47,111,88,.18), transparent 28rem),
    linear-gradient(135deg, #fcf4e7, #eaf4ee);
}
.hero { padding: 36px 5vw 22px; border-bottom: 1px solid var(--line); }
.eyebrow { color: var(--accent); letter-spacing: .08em; text-transform: uppercase; font-size: 12px; }
h1 { margin: 0; font-size: clamp(36px, 6vw, 76px); line-height: .95; }
h2, h3 { margin-top: 0; }
.office-grid { padding: 22px 5vw 64px; display: grid; gap: 18px; grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr); }
.panel {
  background: rgba(255,250,240,.9);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 20px;
  box-shadow: 0 18px 45px rgba(78,57,31,.08);
}
.whiteboard-panel { grid-row: span 2; }
.actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
button {
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  background: var(--ink);
  color: white;
  cursor: pointer;
}
button:hover { background: var(--accent); }
.office-form { display: grid; gap: 10px; margin-top: 14px; }
label { display: grid; gap: 6px; font-weight: 700; }
input, select, textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  font: inherit;
  background: #fffdf8;
}
textarea { min-height: 120px; }
.thread { min-height: 260px; max-height: 480px; overflow: auto; display: grid; gap: 10px; }
.bubble { padding: 12px 14px; border-radius: 16px; background: #fffdf8; border: 1px solid var(--line); }
.bubble.agent { border-left: 5px solid var(--green); }
.bubble.owner { border-left: 5px solid var(--blue); }
.kanban { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.column { background: rgba(23,37,31,.05); border-radius: 16px; padding: 10px; min-height: 90px; }
.work-card, .agent-card, .room-card {
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 16px;
  padding: 12px;
  margin-bottom: 8px;
}
.status { color: var(--blue); font-weight: 700; }
.role { color: var(--accent); font-weight: 700; }
.muted { color: var(--muted); }
.send-status {
  border: 1px dashed var(--line);
  border-radius: 12px;
  padding: 10px;
  background: rgba(33,78,117,.06);
}
.send-status.ok { color: var(--green); border-color: var(--green); }
.send-status.warn { color: var(--accent); border-color: var(--accent); }
.send-status.error { color: var(--red); border-color: var(--red); }
.scheduler-status {
  border: 1px dashed var(--green);
  border-radius: 16px;
  padding: 12px;
  background: rgba(47,111,88,.08);
  margin-bottom: 12px;
}
.l8-cockpit {
  border: 1px dashed var(--accent);
  border-radius: 16px;
  padding: 12px;
  background: rgba(207,102,54,.08);
  margin-bottom: 12px;
}
.l9-cockpit {
  border: 1px dashed var(--blue);
  border-radius: 16px;
  padding: 12px;
  background: rgba(33,78,117,.08);
  margin-bottom: 12px;
}
.l10-cockpit {
  border: 1px dashed var(--green);
  border-radius: 16px;
  padding: 12px;
  background: rgba(47,111,88,.09);
  margin-bottom: 12px;
}
.l8-controls, .l9-controls, .l10-controls { display: grid; gap: 10px; }
.card-grid, .agent-panel { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.timeline { max-height: 360px; overflow: auto; }
pre {
  white-space: pre-wrap;
  background: var(--ink);
  color: #fffaf0;
  border-radius: 16px;
  padding: 14px;
  overflow: auto;
}
@media (max-width: 980px) { .office-grid { grid-template-columns: 1fr; } }

/* Simple Office mode, inspired by the OpenClaw/K9 dark wizard style. */
:root {
  --bg: #080b0f;
  --surface: rgba(15, 20, 28, .92);
  --surface2: rgba(22, 30, 42, .94);
  --border: rgba(110, 231, 183, .22);
  --text: #e8f2ef;
  --text2: #8fa4a0;
  --accent: #2cf59a;
  --accent2: #35c8ff;
  --warn: #ffb86b;
}
body {
  font-family: "SF Mono", "Fira Code", Consolas, ui-monospace, monospace;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 0%, rgba(44, 245, 154, .18), transparent 32rem),
    radial-gradient(circle at 88% 18%, rgba(53, 200, 255, .16), transparent 28rem),
    linear-gradient(135deg, #07090d, #101820 52%, #07110d);
}
.hero {
  max-width: 1180px;
  margin: 0 auto;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.hero h1 {
  font-family: inherit;
  font-size: clamp(34px, 6vw, 72px);
  letter-spacing: -.06em;
}
.subtitle {
  max-width: 760px;
  color: var(--text2);
  font-size: 16px;
}
.eyebrow, .section-label {
  color: var(--accent);
  letter-spacing: .16em;
  text-transform: uppercase;
  font-size: 11px;
}
.office-grid {
  max-width: 1180px;
  margin: 0 auto;
  grid-template-columns: minmax(0, 1.05fr) minmax(340px, .95fr);
}
.mode-switch {
  max-width: 1180px;
  margin: 18px auto 0;
  padding: 18px 20px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  background: rgba(15, 20, 28, .86);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 18px;
  box-shadow: 0 22px 80px rgba(0,0,0,.2);
}
.mode-switch h2 {
  margin: 4px 0;
  letter-spacing: -.04em;
}
.mode-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  min-width: min(440px, 100%);
}
.mode-button {
  min-height: 54px;
  border-color: rgba(255,255,255,.14);
  background: rgba(255,255,255,.055);
  color: var(--text2);
}
.mode-button.active {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #06100c;
  border-color: transparent;
  box-shadow: 0 0 0 1px rgba(44,245,154,.22), 0 12px 35px rgba(44,245,154,.14);
  font-weight: 900;
}
body[data-office-mode="meeting"] .execution-mode,
body[data-office-mode="execution"] .meeting-mode {
  display: none;
}
body[data-office-mode="meeting"] .office-grid {
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, .75fr);
}
body[data-office-mode="execution"] .office-grid {
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
}
.panel {
  background: var(--surface);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 18px;
  box-shadow: 0 22px 80px rgba(0,0,0,.28);
}
.command-center {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, .42fr);
  gap: 18px;
  align-items: start;
  border-color: var(--border);
}
.command-center h2 { font-size: clamp(28px, 4vw, 48px); letter-spacing: -.04em; }
.command-center .office-form { grid-column: 1; }
.template-row, .step-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.template-row { grid-column: 2; align-self: start; }
.template-chip, button {
  font-family: inherit;
  border: 1px solid rgba(44,245,154,.25);
  background: rgba(44,245,154,.12);
  color: var(--text);
  border-radius: 10px;
}
.template-chip:hover, button:hover {
  background: rgba(44,245,154,.22);
  color: white;
}
.primary-action {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #06100c;
  font-weight: 800;
  border: 0;
}
input, select, textarea {
  background: rgba(255,255,255,.055);
  border: 1px solid rgba(255,255,255,.12);
  color: var(--text);
}
textarea { min-height: 150px; }
.muted, .role { color: var(--text2); }
.thread {
  min-height: 360px;
  background: rgba(0,0,0,.16);
  border-radius: 14px;
  padding: 12px;
}
.current-focus {
  margin-bottom: 14px;
  padding: 14px;
  border: 1px solid rgba(53,200,255,.24);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(53,200,255,.12), rgba(44,245,154,.08));
}
.current-focus h3 { margin: 8px 0; }
.history-note {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px dashed rgba(255,255,255,.16);
  border-radius: 12px;
  color: var(--text2);
}
.history-note summary {
  cursor: pointer;
  color: var(--accent2);
}
.bubble {
  background: rgba(255,255,255,.06);
  border-color: rgba(255,255,255,.09);
}
.bubble.owner { border-left-color: var(--accent2); }
.bubble.agent { border-left-color: var(--accent); }
.kanban { grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }
.column, .work-card, .agent-card, .room-card {
  background: rgba(255,255,255,.055);
  border-color: rgba(255,255,255,.09);
}
.send-status, .scheduler-status, .l8-cockpit, .l9-cockpit, .l10-cockpit {
  background: rgba(44,245,154,.07);
  border-color: rgba(44,245,154,.22);
}
pre {
  background: #05070a;
  border: 1px solid rgba(255,255,255,.08);
  color: #d7fff0;
}
.advanced-panel {
  grid-column: 1 / -1;
}
.advanced-panel > summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 800;
  letter-spacing: .02em;
}
.advanced-panel > section {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,.08);
}
.mini-help {
  grid-column: 2;
  color: var(--text2);
}
.mini-help summary { color: var(--accent2); cursor: pointer; }
@media (max-width: 980px) {
  .office-grid, .command-center, .mode-switch { grid-template-columns: 1fr; }
  .template-row, .mini-help { grid-column: 1; }
  .mode-buttons { grid-template-columns: 1fr; }
}
""",
    )
    write_text(
        "static/office.js",
        """
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
    $("packet-result").textContent += `\\n\\nRefresh warning: ${error.message}. The packet action above still completed.`;
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
  return lines.join("\\n");
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
      $("packet-result").textContent += `\\n\\nRefresh warning: ${error.message}. The instruction packet was still created.`;
    }
  } catch (error) {
    setSendStatus(`Could not submit instruction: ${error.message}`, "error");
    $("packet-result").textContent = `Team instruction failed\\n${error.message}`;
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
""",
    )


def schema(name: str, fields: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "schema_id": name,
        "fields": fields,
    }


def write_l75_outputs(state: dict[str, Any]) -> dict[str, Any]:
    schemas = {
        "whiteboard_message_schema": {
            "message_id": "string",
            "thread_id": "string",
            "sender_type": "owner | agent | system",
            "sender_id": "string",
            "target": "string",
            "text": "string",
            "objective": "string",
            "linked_work_item": "string|null",
            "status": "queued|routed|done",
            "external_side_effects": "false",
            "core_writeback": "false",
        },
        "whiteboard_thread_schema": {"thread_id": "string", "status": "open|closed", "messages": "array"},
        "work_item_schema": {
            "work_item_id": "string",
            "title": "string",
            "description": "string",
            "source_message_id": "string|null",
            "requested_by": "string",
            "assigned_agents": "array",
            "status": "Inbox|Interpreting|Assigned|In Progress|Waiting for Approval|Blocked|Done",
            "progress_notes": "array",
            "blockers": "array",
        },
        "routing_decision_schema": {
            "routing_decision_id": "string",
            "primary_agent": "string",
            "supporting_agents": "array",
            "expected_outputs": "array",
            "approval_points": "array",
            "no_go_boundaries": "array",
        },
        "agent_reply_schema": {
            "reply_id": "string",
            "agent_id": "string",
            "work_item_id": "string",
            "role_interpretation": "string",
            "work_done": "string",
            "findings": "array",
            "blockers": "array",
            "next_step": "string",
            "approval_needed": "boolean",
        },
        "work_cycle_schema": {
            "work_cycle_id": "string",
            "work_items_processed": "array",
            "agents_involved": "array",
            "actions_taken": "array",
            "artifacts_created": "array",
            "blocked_items": "array",
            "approval_requests_created": "array",
            "no_action_receipt": "object",
        },
        "completion_report_schema": {
            "completion_report_id": "string",
            "work_item_id": "string",
            "summary": "string",
            "assigned_agents": "array",
            "artifacts": "array",
            "completion_status": "string",
            "remaining_risks": "array",
            "approval_needed": "boolean",
            "next_owner_action": "string",
        },
        "approval_request_schema": {
            "approval_request_id": "string",
            "work_item_id": "string",
            "reason": "string",
            "default_decision": "blocked_until_human_approved",
            "status": "waiting_for_owner",
        },
    }
    for name, fields in schemas.items():
        write_l75_json(f"schemas/{name}.json", schema(name, fields))

    demo = create_demo_scenario()
    write_l75_json("demo_scenarios/demo_first_cash_path_team_discussion.json", demo)
    write_l75_md(
        "demo_scenarios/demo_first_cash_path_team_discussion.md",
        """
# Demo: First Cash Path Team Discussion

Owner message:

团队请一起分析：我们下一步怎么最快拿到第一笔钱，同时不牺牲长期战略？

Expected local flow:

- Aiden interprets and delegates.
- Zara analyzes commercialization path.
- Marco checks pricing and cash assumptions.
- Sofia drafts internal positioning.
- Jinjin proposes read-only research.
- Ethan identifies missing tools.
- Samantha archives and indexes packets.
- Auditor function reviews no-action boundaries.

No external side effects occur.
""",
    )

    runtime_state = {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "packet_type": "whiteboard_runtime_state",
        "generated_at_utc": GENERATED_AT,
        "local_url": LOCAL_URL,
        "whiteboard_chat_ui_available": True,
        "team_work_board_available": True,
        "agent_panels_available": True,
        "progress_timeline_available": True,
        "approval_queue_available": True,
        "agent_count": state["agent_count"],
        "work_board_columns": state["work_board_columns"],
        "safe_internal_work_cycles_enabled": True,
        "coo_invented": False,
    }
    write_l75_json("whiteboard_runtime_state.json", runtime_state)
    receipt = {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "packet_type": "l7_5_no_action_receipt",
        "generated_at_utc": GENERATED_AT,
        "outreach_occurred": False,
        "email_sent": False,
        "form_submission_occurred": False,
        "publication_occurred": False,
        "payment_occurred": False,
        "account_creation_occurred": False,
        "customer_contacted": False,
        "grant_rfp_submission_occurred": False,
        "mcp_live_behavior_occurred": False,
        "actual_memory_brain_canonical_cieu_db_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
        "ask_user_url_occurred": False,
    }
    write_l75_json("l7_5_no_action_receipts/l7_5_no_action_receipt.json", receipt)
    summary = {
        "schema_version": "v0",
        "milestone_id": "L7.5",
        "packet_type": "l7_5_summary",
        "generated_at_utc": GENERATED_AT,
        "whiteboard_chat_ui_available": True,
        "team_work_board_available": True,
        "agent_panels_available": True,
        "progress_timeline_available": True,
        "approval_queue_available": True,
        "message_to_agent_works_locally": True,
        "team_task_works_locally": True,
        "routing_engine_generated": True,
        "work_cycle_engine_generated": True,
        "agent_replies_generated": True,
        "completion_report_generated": True,
        "demo_scenario_generated": True,
        "local_url": LOCAL_URL,
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
        "coo_invented": False,
    }
    write_l75_json("l7_5_summary.json", summary)
    write_l75_md(
        "l7_5_summary.md",
        f"""
# L7.5 Real Labs Whiteboard Collaboration Runtime

The Labs Office now has a local whiteboard collaboration loop:

owner message → Aiden routing → agent replies → work board progress → approval gate → completion report.

Run:

`bash scripts/run_l7_labs_office_web.sh --mode serve`

Then open:

`{LOCAL_URL}`
""",
    )
    return summary


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = audit_existing_html()
    state = build_runtime_state()
    write_assets()
    l75_summary = write_l75_outputs(state)
    l76_summary = build_l76_manifest()
    l8_summary = build_l8_manifest()
    l9_summary = build_l9_manifest()
    l10_summary = build_l10_manifest()
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
        "whiteboard_runtime_created": True,
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
            "GET /api/scheduler/status",
            "POST /api/scheduler/run_once",
            "POST /api/scheduler/run_bounded",
            "GET /api/autonomous_runs",
            "GET /api/progress_heartbeats",
            "GET /api/approval_interrupts",
            "GET /api/l8/first_cash_path/status",
            "POST /api/l8/first_cash_path/start",
            "POST /api/l8/commercial_actions/build",
            "GET /api/l8/commercial_actions",
            "GET /api/l8/approvals",
            "POST /api/l8/approvals/decide",
            "GET /api/l8/manual_send_packets",
            "POST /api/l8/manual_send_packets/mark",
            "POST /api/l8/customer_feedback",
            "GET /api/l8/customer_feedback",
            "POST /api/l8/residuals/build",
            "GET /api/l8/residuals",
            "POST /api/l8/learning_candidates/build",
            "GET /api/l8/learning_candidates",
            "GET /api/l8/cockpit",
            "GET /api/l9/meta/status",
            "POST /api/l9/assets/build",
            "GET /api/l9/assets",
            "POST /api/l9/opportunities/discover",
            "GET /api/l9/opportunities",
            "POST /api/l9/money_paths/generate",
            "GET /api/l9/money_paths",
            "POST /api/l9/rankings/build",
            "GET /api/l9/rankings",
            "POST /api/l9/decision_packets/build",
            "GET /api/l9/decision_packets",
            "POST /api/l9/opportunity_reviews/decide",
            "GET /api/l9/opportunity_reviews",
            "POST /api/l9/execution_plans/build",
            "GET /api/l9/execution_plans",
            "POST /api/l9/l8_bridge/build",
            "GET /api/l9/l8_bridge_packets",
            "POST /api/l9/portfolio_residuals/build",
            "GET /api/l9/portfolio_residuals",
            "POST /api/l9/portfolio_learning_candidates/build",
            "GET /api/l9/portfolio_learning_candidates",
            "GET /api/l9/meta/cockpit",
            "GET /api/l10/missions",
            "POST /api/l10/missions/create_default",
            "POST /api/l10/missions/create",
            "GET /api/l10/missions/status",
            "POST /api/l10/mission_plan/build",
            "POST /api/l10/mission_runner/run_bounded",
            "POST /api/l10/research/run_fixture_demo",
            "POST /api/l10/escalations/decide",
            "GET /api/l10/cockpit",
        ],
        "existing_html_owner_usable": audit["owner_usable"],
        "next_one_command_action": "bash scripts/run_l7_labs_office_web.sh --mode serve",
        "no_coo_invented_as_legacy_member": True,
        "l7_5_summary_ref": "l7_labs_whiteboard_collaboration_runtime/l7_5_summary.json",
        "l7_6_summary_ref": "l7_labs_team_self_work_scheduler/l7_6_summary.json",
        "scheduler_created": l76_summary["scheduler_created"],
        "l8_summary_ref": "l8_first_cash_path_operating_loop/l8_summary.json",
        "l8_first_cash_path_initialized": l8_summary["first_cash_path_initialized"],
        "l9_summary_ref": "l9_meta_development_opportunity_runtime/l9_summary.json",
        "l9_package_available": True,
        "l9_opportunity_count": l9_summary["opportunity_count"],
        "l9_money_path_count": l9_summary["money_path_count"],
        "l9_ranking_count": l9_summary["ranking_count"],
        "grant_rfp_path_created_by_default": False,
        "l10_summary_ref": "l10_delegated_live_meta_development_runtime/l10_summary.json",
        "l10_package_available": True,
        "l10_mission_count": l10_summary["mission_count"],
        "l10_permission_tier_count": l10_summary["permission_tier_count"],
        "configured_live_read_only_research_available": False,
        "fixture_demo_available": True,
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
