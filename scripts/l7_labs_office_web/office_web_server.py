#!/usr/bin/env python3
"""Local-only Web UI server for the real Y*Bridge Labs Office."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from whiteboard_store import (
    create_whiteboard_message,
    create_work_item,
    load_approval_requests,
    load_threads,
    load_timeline,
    work_board,
    whiteboard_snapshot,
)
from work_cycle_engine import create_completion_report, route_latest_or_payload, run_team_work_cycle, run_work_cycle


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "l7_real_labs_office_web_ui"
STATE_PATH = OUT / "office_runtime_state.json"
TEMPLATE_PATH = OUT / "templates/index.html"

from l7_labs_team_self_work_scheduler.progress_ledger import (  # noqa: E402
    load_approval_interrupts,
    load_autonomous_runs,
    load_progress_heartbeats,
)
from l7_labs_team_self_work_scheduler.scheduler import scheduler_status, run_bounded as run_scheduler_bounded, run_once as run_scheduler_once  # noqa: E402
from l8_first_cash_path_operating_loop.cockpit_model import build_cockpit_snapshot, current_cockpit  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_action_builder import build_commercial_actions  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_action_queue import list_commercial_actions  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_residual import build_commercial_residual, list_commercial_residuals  # noqa: E402
from l8_first_cash_path_operating_loop.customer_feedback_intake import list_customer_feedback, record_customer_feedback  # noqa: E402
from l8_first_cash_path_operating_loop.first_cash_path_loader import first_cash_path_status, initialize_first_cash_path  # noqa: E402
from l8_first_cash_path_operating_loop.first_cash_path_model import latest_packet  # noqa: E402
from l8_first_cash_path_operating_loop.learning_candidate_builder import build_learning_candidate, list_learning_candidates  # noqa: E402
from l8_first_cash_path_operating_loop.manual_send_packet import list_manual_send_packets, mark_manual_send_packet  # noqa: E402
from l8_first_cash_path_operating_loop.owner_approval_center import decide_action, list_approval_decisions, list_pending_approvals  # noqa: E402
from l9_meta_development_opportunity_runtime.execution_plan_generator import build_execution_plan, list_execution_plans  # noqa: E402
from l9_meta_development_opportunity_runtime.internal_asset_inventory import build_internal_asset_inventory, list_assets  # noqa: E402
from l9_meta_development_opportunity_runtime.l8_action_loop_bridge import build_l8_bridge_packet, list_l8_bridge_packets  # noqa: E402
from l9_meta_development_opportunity_runtime.l9_manifest_builder import build_manifest as build_l9_manifest  # noqa: E402
from l9_meta_development_opportunity_runtime.meta_development_cockpit import build_meta_cockpit, current_meta_cockpit  # noqa: E402
from l9_meta_development_opportunity_runtime.money_path_generator import generate_money_paths  # noqa: E402
from l9_meta_development_opportunity_runtime.money_path_model import list_money_paths  # noqa: E402
from l9_meta_development_opportunity_runtime.opportunity_discovery_engine import discover_opportunities  # noqa: E402
from l9_meta_development_opportunity_runtime.opportunity_model import latest_packet as latest_l9_packet  # noqa: E402
from l9_meta_development_opportunity_runtime.opportunity_portfolio import list_opportunities  # noqa: E402
from l9_meta_development_opportunity_runtime.opportunity_review_center import decide_opportunity, list_opportunity_review_decisions  # noqa: E402
from l9_meta_development_opportunity_runtime.owner_decision_packet import build_owner_decision_packets, list_owner_decision_packets  # noqa: E402
from l9_meta_development_opportunity_runtime.portfolio_feedback_ingestor import record_portfolio_feedback  # noqa: E402
from l9_meta_development_opportunity_runtime.portfolio_learning_candidate import build_portfolio_learning_candidate, list_portfolio_learning_candidates  # noqa: E402
from l9_meta_development_opportunity_runtime.portfolio_residual import build_portfolio_residual, list_portfolio_residuals  # noqa: E402
from l9_meta_development_opportunity_runtime.ranking_engine import build_rankings, list_rankings  # noqa: E402
from l10_delegated_live_meta_development_runtime.action_plan_builder import build_action_plan, list_action_plans  # noqa: E402
from l10_delegated_live_meta_development_runtime.conflict_detector import list_conflict_reports  # noqa: E402
from l10_delegated_live_meta_development_runtime.controlled_research_executor import run_configured_live_read_only, run_fixture_research_demo  # noqa: E402
from l10_delegated_live_meta_development_runtime.controlled_research_planner import build_research_plan, list_research_plans  # noqa: E402
from l10_delegated_live_meta_development_runtime.escalation_packet_builder import build_escalation_packets, list_escalation_packets  # noqa: E402
from l10_delegated_live_meta_development_runtime.escalation_review_center import decide_escalation, list_escalation_review_decisions  # noqa: E402
from l10_delegated_live_meta_development_runtime.evidence_packet_builder import list_evidence_packets  # noqa: E402
from l10_delegated_live_meta_development_runtime.l8_action_loop_escalation_bridge import build_l8_action_loop_escalation_packet  # noqa: E402
from l10_delegated_live_meta_development_runtime.l9_portfolio_update_bridge import build_l9_portfolio_update_packet, list_l9_portfolio_update_packets  # noqa: E402
from l10_delegated_live_meta_development_runtime.l10_manifest_builder import build_manifest as build_l10_manifest  # noqa: E402
from l10_delegated_live_meta_development_runtime.meta_strategy_brief_builder import build_meta_strategy_brief, list_meta_strategy_briefs  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_cockpit_model import build_mission_cockpit, current_mission_cockpit  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_completion_report import build_mission_completion_report, list_mission_completion_reports  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_delegation_center import create_default_mission, create_mission, get_mission, list_missions  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_model import load_packets as load_l10_packets  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_plan_builder import build_mission_plan, list_mission_plans  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_progress_ledger import list_progress  # noqa: E402
from l10_delegated_live_meta_development_runtime.mission_runner import run_bounded_mission, run_mission_cycle  # noqa: E402
from l10_delegated_live_meta_development_runtime.opportunity_signal_extractor import extract_opportunity_signals, list_opportunity_signals  # noqa: E402
from l10_delegated_live_meta_development_runtime.permission_tiers import permission_tier_registry  # noqa: E402
from l10_delegated_live_meta_development_runtime.source_summary_builder import list_source_summaries  # noqa: E402

ALLOWED_ACTIONS = [
    "local packet creation",
    "internal analysis",
    "draft-only artifact generation",
    "approval request preparation",
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


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        raise FileNotFoundError("office_runtime_state.json missing; run build mode first")
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler: BaseHTTPRequestHandler, body: str, content_type: str = "text/html; charset=utf-8") -> None:
    raw = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)


def error_response(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    json_response(handler, {"ok": False, "error": message}, status)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())[:80].strip("_")
    return slug or "packet"


def timestamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def packet_base(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.4R",
        "packet_type": packet_type,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "allowed_actions": ALLOWED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "approval_required_for": APPROVAL_REQUIRED_FOR,
        "status": "queued",
        "external_side_effects": False,
        "core_writeback": False,
    }


def create_owner_message_packet(payload: dict[str, Any], out_dir: Path = OUT) -> dict[str, Any]:
    target = safe_slug(str(payload.get("target_agent", "aiden_ceo")))
    packet_id = f"owner_message_{timestamp()}_{target}"
    packet = {
        **packet_base("owner_message"),
        "packet_id": packet_id,
        "from": "owner",
        "target_agent": target,
        "message_text": str(payload.get("message_text", "")).strip(),
        "objective": str(payload.get("objective", "")).strip(),
        "urgency": str(payload.get("urgency", "normal")).strip() or "normal",
    }
    packet_dir = out_dir / "runtime_packets/owner_messages"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / f"{packet_id}.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "packet_path": str(packet_path.relative_to(ROOT)) if packet_path.is_relative_to(ROOT) else str(packet_path),
        "next_step": "route_to_aiden_or_selected_agent",
        "packet": packet,
    }


def create_team_task_packet(payload: dict[str, Any], out_dir: Path = OUT) -> dict[str, Any]:
    packet_id = f"team_task_{timestamp()}_{safe_slug(str(payload.get('task_title', 'team_task')))}"
    packet = {
        **packet_base("team_task"),
        "packet_id": packet_id,
        "from": "owner",
        "target": "team",
        "task_title": str(payload.get("task_title", "")).strip(),
        "task_description": str(payload.get("task_description", "")).strip(),
        "suggested_lead": "Aiden",
        "assigned_status": "pending_routing",
    }
    packet_dir = out_dir / "runtime_packets/team_tasks"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / f"{packet_id}.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "packet_path": str(packet_path.relative_to(ROOT)) if packet_path.is_relative_to(ROOT) else str(packet_path),
        "next_step": "route_to_aiden_for_team_delegation",
        "packet": packet,
    }


def aiden_direct_reply(user_text: str) -> str:
    text = user_text.strip()
    lowered = text.lower()
    if any(word in text for word in ["第一笔钱", "赚钱", "收入", "cash", "付费"]):
        return (
            "我会先把目标收窄成一个可验证的现金实验：不要先卖宏大的 AI 公司愿景，先卖一个小而清楚的服务包。"
            "我建议的第一个可收费东西是 Founder AI Workflow Audit & CEO Command Brief：帮一个 AI founder/operator 看清当前 workflow、agent 使用、执行瓶颈和下一步决策。"
            "第一版价格可以把 $1500 当作测试假设。下一步不是群发，而是先做一页 offer 和一条 owner 手动发送草稿。"
        )
    if any(word in text for word in ["难受", "疯", "哭", "折磨", "崩溃"]):
        return (
            "你现在的感受是合理的。之前的页面把内部机制包装成团队办公室，给了你错误预期。"
            "我现在只做一件事：听你说问题，然后用 Aiden 的 CEO 视角给一个直接回答。"
            "不再让你看 packet、timeline、L8/L9/L10，除非你明确要。"
        )
    if any(word in text for word in ["计划", "30天", "三十天", "下一步"]):
        return (
            "我建议下一步只保留三条线：第一，定义一个能收钱的服务包；第二，做一个客户能看懂的样例 brief；第三，准备一条 owner 手动发送的信息。"
            "不要再扩展系统层级，先验证有没有人愿意为这个诊断服务付钱。"
        )
    if any(word in lowered for word in ["hello", "hi", "test"]) or any(word in text for word in ["测试", "在吗"]):
        return "我在。这个页面现在只负责一件事：你说一个问题，我用 Aiden 的 CEO 视角直接回应。"
    return (
        f"我先复述我听到的问题：{text[:160]}"
        "。我的建议是先把它变成一个可以判断的 owner 决策：目标是什么、下一步要产出什么、什么事情不能自动做。"
        "如果你愿意，下一句可以直接问我：'Aiden，你建议我现在具体做哪一个东西来赚钱？'"
    )


def aiden_chat_history(out_dir: Path = OUT) -> list[dict[str, Any]]:
    path = out_dir / "runtime_packets/aiden_chat/aiden_chat_thread.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def create_aiden_chat_turn(payload: dict[str, Any], out_dir: Path = OUT) -> dict[str, Any]:
    text = str(payload.get("message", "")).strip()
    if not text:
        raise ValueError("message is required")
    packet_dir = out_dir / "runtime_packets/aiden_chat"
    packet_dir.mkdir(parents=True, exist_ok=True)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    turn_id = f"aiden_chat_{timestamp()}_{time.time_ns() % 1_000_000:06d}"
    user_turn = {
        "turn_id": f"{turn_id}_owner",
        "created_at_utc": now,
        "speaker": "owner",
        "text": text,
        "external_side_effects": False,
        "core_writeback": False,
    }
    aiden_turn = {
        "turn_id": f"{turn_id}_aiden",
        "created_at_utc": now,
        "speaker": "aiden_ceo",
        "display_name": "Aiden Liu",
        "text": aiden_direct_reply(text),
        "external_side_effects": False,
        "core_writeback": False,
    }
    history = aiden_chat_history(out_dir)
    history.extend([user_turn, aiden_turn])
    path = packet_dir / "aiden_chat_thread.json"
    path.write_text(json.dumps(history[-80:], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "reply": aiden_turn,
        "history": history[-80:],
        "external_side_effects": False,
        "core_writeback": False,
    }


def l9_status() -> dict[str, Any]:
    build_l9_manifest(force=False)
    opportunities = list_opportunities()
    paths = list_money_paths()
    selected = [path for path in paths if path.get("status") == "selected_for_execution"]
    return {
        "ok": True,
        "l9_package_available": True,
        "asset_inventory_count": len(list_assets()),
        "opportunity_count": len(opportunities),
        "money_path_count": len(paths),
        "ranking_count": len(list_rankings()),
        "selected_opportunity_count": len(selected),
        "execution_plan_count": len(list_execution_plans()),
        "l8_bridge_packet_count": len(list_l8_bridge_packets()),
        "portfolio_residual_count": len(list_portfolio_residuals()),
        "portfolio_learning_candidate_count": len(list_portfolio_learning_candidates()),
        "grant_rfp_default_path_status": "no",
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "payment_processed": False,
        "publication": False,
        "core_writeback": False,
        "coo_invented": False,
    }


def l10_status() -> dict[str, Any]:
    build_l10_manifest(force=False)
    missions = list_missions()
    active = [mission for mission in missions if mission.get("status") not in {"completed_local_bounded_run"}]
    return {
        "ok": True,
        "l10_package_available": True,
        "mission_count": len(missions),
        "active_mission_count": len(active),
        "evidence_packet_count": len(list_evidence_packets()),
        "opportunity_signal_count": len(list_opportunity_signals()),
        "strategy_brief_count": len(list_meta_strategy_briefs()),
        "escalation_packet_count": len(list_escalation_packets()),
        "completion_report_count": len(list_mission_completion_reports()),
        "configured_live_read_only_research_available": False,
        "fixture_demo_available": True,
        "external_side_effects": False,
        "customer_contact": False,
        "email_sent": False,
        "payment_processed": False,
        "publication": False,
        "uncontrolled_web_research": False,
        "core_writeback": False,
        "coo_invented": False,
    }


class OfficeHandler(BaseHTTPRequestHandler):
    server_version = "LabsOffice/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/":
                text_response(self, TEMPLATE_PATH.read_text(encoding="utf-8"))
            elif path == "/static/office.css":
                text_response(self, (OUT / "static/office.css").read_text(encoding="utf-8"), "text/css; charset=utf-8")
            elif path == "/static/office.js":
                text_response(self, (OUT / "static/office.js").read_text(encoding="utf-8"), "application/javascript; charset=utf-8")
            elif path == "/api/status":
                json_response(self, load_state())
            elif path == "/api/aiden_chat":
                json_response(self, {"ok": True, "history": aiden_chat_history()})
            elif path == "/api/roster":
                state = load_state()
                json_response(self, {"agents": state.get("agents", []), "agent_count": state.get("agent_count", 0)})
            elif path.startswith("/api/agents/"):
                agent_id = safe_slug(unquote(path.removeprefix("/api/agents/")))
                state = load_state()
                for agent in state.get("agents", []):
                    if agent.get("agent_id") == agent_id:
                        json_response(self, agent)
                        return
                error_response(self, HTTPStatus.NOT_FOUND, f"unknown agent: {agent_id}")
            elif path == "/api/work_queue":
                json_response(self, {"work_queue": load_state().get("work_queue", [])})
            elif path == "/api/pending_approvals":
                state = load_state()
                json_response(
                    self,
                    {
                        "pending_approvals": state.get("pending_approvals", []),
                        "approval_requests": load_approval_requests(),
                    },
                )
            elif path == "/api/whiteboard":
                json_response(self, whiteboard_snapshot())
            elif path == "/api/whiteboard/threads":
                json_response(self, {"threads": load_threads()})
            elif path == "/api/work_board":
                json_response(self, {"work_board": work_board()})
            elif path == "/api/timeline":
                json_response(self, {"timeline": load_timeline()})
            elif path == "/api/scheduler/status":
                json_response(self, scheduler_status())
            elif path == "/api/autonomous_runs":
                json_response(self, {"autonomous_runs": load_autonomous_runs()})
            elif path == "/api/progress_heartbeats":
                json_response(self, {"progress_heartbeats": load_progress_heartbeats()})
            elif path == "/api/approval_interrupts":
                json_response(self, {"approval_interrupts": load_approval_interrupts()})
            elif path == "/api/l8/first_cash_path/status":
                json_response(self, first_cash_path_status())
            elif path == "/api/l8/commercial_actions":
                json_response(self, {"commercial_actions": list_commercial_actions()})
            elif path == "/api/l8/approvals":
                json_response(self, {"pending_approvals": list_pending_approvals(), "approval_decisions": list_approval_decisions()})
            elif path == "/api/l8/manual_send_packets":
                json_response(self, {"manual_send_packets": list_manual_send_packets()})
            elif path == "/api/l8/customer_feedback":
                json_response(self, {"customer_feedback": list_customer_feedback()})
            elif path == "/api/l8/residuals":
                json_response(self, {"commercial_residuals": list_commercial_residuals()})
            elif path == "/api/l8/learning_candidates":
                json_response(self, {"learning_candidates": list_learning_candidates()})
            elif path == "/api/l8/cockpit":
                json_response(self, current_cockpit())
            elif path == "/api/l9/meta/status":
                json_response(self, l9_status())
            elif path == "/api/l9/assets":
                json_response(self, {"assets": list_assets()})
            elif path == "/api/l9/opportunities":
                json_response(self, {"opportunities": list_opportunities()})
            elif path == "/api/l9/money_paths":
                json_response(self, {"money_paths": list_money_paths()})
            elif path == "/api/l9/rankings":
                json_response(self, {"rankings": list_rankings()})
            elif path == "/api/l9/decision_packets":
                json_response(self, {"decision_packets": list_owner_decision_packets()})
            elif path == "/api/l9/opportunity_reviews":
                json_response(self, {"opportunity_review_decisions": list_opportunity_review_decisions()})
            elif path == "/api/l9/execution_plans":
                json_response(self, {"execution_plans": list_execution_plans()})
            elif path == "/api/l9/l8_bridge_packets":
                json_response(self, {"l8_bridge_packets": list_l8_bridge_packets()})
            elif path == "/api/l9/portfolio_residuals":
                json_response(self, {"portfolio_residuals": list_portfolio_residuals()})
            elif path == "/api/l9/portfolio_learning_candidates":
                json_response(self, {"portfolio_learning_candidates": list_portfolio_learning_candidates()})
            elif path == "/api/l9/meta/cockpit":
                json_response(self, current_meta_cockpit())
            elif path == "/api/l10/missions":
                json_response(self, {"missions": list_missions()})
            elif path == "/api/l10/missions/status":
                json_response(self, l10_status())
            elif path == "/api/l10/mission_plan":
                json_response(self, {"mission_plans": list_mission_plans()})
            elif path == "/api/l10/research_plan":
                json_response(self, {"research_plans": list_research_plans()})
            elif path == "/api/l10/research/budget_receipts":
                json_response(self, {"research_budget_receipts": load_l10_packets("research_budget_receipts")})
            elif path == "/api/l10/evidence":
                json_response(self, {"evidence_packets": list_evidence_packets()})
            elif path == "/api/l10/source_summaries":
                json_response(self, {"source_summaries": list_source_summaries()})
            elif path == "/api/l10/conflicts":
                json_response(self, {"conflict_reports": list_conflict_reports()})
            elif path == "/api/l10/opportunity_signals":
                json_response(self, {"opportunity_signals": list_opportunity_signals()})
            elif path == "/api/l10/meta_strategy_briefs":
                json_response(self, {"meta_strategy_briefs": list_meta_strategy_briefs()})
            elif path == "/api/l10/action_plans":
                json_response(self, {"action_plans": list_action_plans()})
            elif path == "/api/l10/escalations":
                json_response(self, {"escalation_packets": list_escalation_packets()})
            elif path == "/api/l10/escalation_decisions":
                json_response(self, {"escalation_review_decisions": list_escalation_review_decisions()})
            elif path == "/api/l10/l9_portfolio_updates":
                json_response(self, {"l9_portfolio_update_packets": list_l9_portfolio_update_packets()})
            elif path == "/api/l10/completion_reports":
                json_response(self, {"mission_completion_reports": list_mission_completion_reports()})
            elif path == "/api/l10/cockpit":
                json_response(self, current_mission_cockpit())
            else:
                error_response(self, HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            error_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            error_response(self, HTTPStatus.BAD_REQUEST, "invalid json")
            return
        try:
            if parsed.path == "/api/aiden_chat":
                try:
                    json_response(self, create_aiden_chat_turn(payload))
                except ValueError as exc:
                    error_response(self, HTTPStatus.BAD_REQUEST, str(exc))
                    return
            elif parsed.path == "/api/message":
                if not str(payload.get("message_text", "")).strip():
                    error_response(self, HTTPStatus.BAD_REQUEST, "message_text is required")
                    return
                json_response(self, create_owner_message_packet(payload))
            elif parsed.path == "/api/team_task":
                if not str(payload.get("task_description", "")).strip():
                    error_response(self, HTTPStatus.BAD_REQUEST, "task_description is required")
                    return
                json_response(self, create_team_task_packet(payload))
            elif parsed.path == "/api/whiteboard/message":
                text = str(payload.get("text", "")).strip()
                if not text:
                    error_response(self, HTTPStatus.BAD_REQUEST, "text is required")
                    return
                message = create_whiteboard_message(
                    text=text,
                    target=str(payload.get("target", "whole_team")),
                    objective=str(payload.get("objective", "")),
                )
                json_response(self, {"ok": True, "message": message, "next_step": "route_with_aiden"})
            elif parsed.path == "/api/route":
                json_response(self, route_latest_or_payload(payload))
            elif parsed.path == "/api/work_items":
                title = str(payload.get("title", "Owner-created work item")).strip()
                description = str(payload.get("description", "")).strip()
                item = create_work_item(
                    title=title,
                    description=description or title,
                    source_message_id=payload.get("source_message_id"),
                    assigned_agents=payload.get("assigned_agents") or ["aiden_ceo"],
                )
                json_response(self, {"ok": True, "work_item": item})
            elif parsed.path == "/api/work_cycle":
                json_response(self, run_work_cycle(payload.get("work_item_id")))
            elif parsed.path == "/api/team_work_cycle":
                json_response(
                    self,
                    run_team_work_cycle(
                        max_work_items_per_cycle=int(payload.get("max_work_items_per_cycle", 3)),
                        max_agent_replies_per_cycle=int(payload.get("max_agent_replies_per_cycle", 8)),
                    ),
                )
            elif parsed.path == "/api/completion_report":
                json_response(self, create_completion_report(payload.get("work_item_id")))
            elif parsed.path == "/api/scheduler/run_once":
                json_response(
                    self,
                    run_scheduler_once(
                        max_cycles=int(payload.get("max_cycles", 1)),
                        max_agent_replies_per_cycle=int(payload.get("max_agent_replies_per_cycle", 8)),
                    ),
                )
            elif parsed.path == "/api/scheduler/run_bounded":
                json_response(
                    self,
                    run_scheduler_bounded(
                        max_work_items=int(payload.get("max_work_items", 3)),
                        max_cycles=int(payload.get("max_cycles", 2)),
                        max_agent_replies_per_cycle=int(payload.get("max_agent_replies_per_cycle", 8)),
                    ),
                )
            elif parsed.path == "/api/l8/first_cash_path/start":
                path = initialize_first_cash_path(force=bool(payload.get("force", False)))
                json_response(self, {"ok": True, "first_cash_path": path, "cockpit": build_cockpit_snapshot()})
            elif parsed.path == "/api/l8/commercial_actions/build":
                result = build_commercial_actions(force=bool(payload.get("force", False)))
                result["cockpit"] = build_cockpit_snapshot()
                json_response(self, result)
            elif parsed.path == "/api/l8/approvals/decide":
                action_id = str(payload.get("action_id", "")).strip()
                decision = str(payload.get("decision", "")).strip()
                if not action_id or not decision:
                    error_response(self, HTTPStatus.BAD_REQUEST, "action_id and decision are required")
                    return
                result = decide_action(action_id, decision, str(payload.get("decision_note", "")))
                result["cockpit"] = build_cockpit_snapshot()
                json_response(self, result)
            elif parsed.path == "/api/l8/manual_send_packets/mark":
                packet_id = str(payload.get("packet_id", "")).strip()
                status = str(payload.get("owner_marked_status", "")).strip()
                if not packet_id or not status:
                    error_response(self, HTTPStatus.BAD_REQUEST, "packet_id and owner_marked_status are required")
                    return
                receipt = mark_manual_send_packet(packet_id, status, str(payload.get("owner_note", "")))
                json_response(self, {"ok": True, "manual_action_receipt": receipt, "cockpit": build_cockpit_snapshot()})
            elif parsed.path == "/api/l8/customer_feedback":
                packet_id = str(payload.get("manual_send_packet_id", "")).strip()
                response_status = str(payload.get("response_status", "")).strip()
                if not packet_id or not response_status:
                    error_response(self, HTTPStatus.BAD_REQUEST, "manual_send_packet_id and response_status are required")
                    return
                feedback = record_customer_feedback(
                    packet_id,
                    response_status,
                    str(payload.get("feedback_text", "")),
                    payload.get("paid_signal") if "paid_signal" in payload else None,
                    str(payload.get("objection_type", "unknown")),
                    str(payload.get("next_step_requested", "")),
                )
                json_response(self, {"ok": True, "customer_feedback": feedback, "cockpit": build_cockpit_snapshot()})
            elif parsed.path == "/api/l8/residuals/build":
                feedback_id = str(payload.get("feedback_id", "")).strip()
                if not feedback_id:
                    latest_feedback = latest_packet("customer_feedback")
                    feedback_id = latest_feedback.get("feedback_id", "") if latest_feedback else ""
                if not feedback_id:
                    error_response(self, HTTPStatus.BAD_REQUEST, "feedback_id is required")
                    return
                residual = build_commercial_residual(feedback_id)
                json_response(self, {"ok": True, "commercial_residual": residual, "cockpit": build_cockpit_snapshot()})
            elif parsed.path == "/api/l8/learning_candidates/build":
                residual_id = str(payload.get("residual_id", "")).strip()
                if not residual_id:
                    latest_residual = latest_packet("commercial_residuals")
                    residual_id = latest_residual.get("residual_id", "") if latest_residual else ""
                if not residual_id:
                    error_response(self, HTTPStatus.BAD_REQUEST, "residual_id is required")
                    return
                candidate = build_learning_candidate(residual_id)
                json_response(self, {"ok": True, "learning_candidate": candidate, "cockpit": build_cockpit_snapshot()})
            elif parsed.path == "/api/l9/assets/build":
                inventory = build_internal_asset_inventory()
                json_response(self, {"ok": True, "asset_inventory": inventory, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/opportunities/discover":
                result = discover_opportunities(force=bool(payload.get("force", False)))
                json_response(self, {**result, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/money_paths/generate":
                result = generate_money_paths(force=bool(payload.get("force", False)))
                json_response(self, {**result, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/rankings/build":
                result = build_rankings(force=bool(payload.get("force", False)))
                json_response(self, {**result, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/decision_packets/build":
                result = build_owner_decision_packets(force=bool(payload.get("force", False)))
                json_response(self, {**result, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/opportunity_reviews/decide":
                packet_id = str(payload.get("decision_packet_id", "")).strip()
                decision = str(payload.get("decision", "")).strip()
                if not packet_id or not decision:
                    error_response(self, HTTPStatus.BAD_REQUEST, "decision_packet_id and decision are required")
                    return
                result = decide_opportunity(packet_id, decision, str(payload.get("decision_note", "")))
                result["cockpit"] = build_meta_cockpit()
                json_response(self, result)
            elif parsed.path == "/api/l9/execution_plans/build":
                plan = build_execution_plan(str(payload.get("money_path_id", "")).strip() or None)
                json_response(self, {"ok": True, "execution_plan": plan, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/l8_bridge/build":
                bridge = build_l8_bridge_packet(str(payload.get("execution_plan_id", "")).strip() or None)
                json_response(self, {"ok": True, "l8_bridge_packet": bridge, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/portfolio_residuals/build":
                feedback_id = str(payload.get("feedback_id", "")).strip()
                if not feedback_id:
                    money_path_id = str(payload.get("money_path_id", "")).strip()
                    if not money_path_id:
                        selected = [path for path in list_money_paths() if path.get("status") == "selected_for_execution"]
                        money_path_id = selected[0]["money_path_id"] if selected else (list_money_paths()[0]["money_path_id"] if list_money_paths() else "")
                    if not money_path_id:
                        error_response(self, HTTPStatus.BAD_REQUEST, "money_path_id or feedback_id is required")
                        return
                    feedback = record_portfolio_feedback(
                        money_path_id,
                        str(payload.get("actual_signal", "no_signal")),
                        str(payload.get("feedback_summary", "Owner/demo signal gap recorded locally.")),
                    )
                    feedback_id = feedback["feedback_id"]
                residual = build_portfolio_residual(feedback_id)
                json_response(self, {"ok": True, "portfolio_residual": residual, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l9/portfolio_learning_candidates/build":
                residual_id = str(payload.get("residual_id", "")).strip()
                if not residual_id:
                    latest_residual = latest_l9_packet("portfolio_residuals")
                    residual_id = latest_residual.get("residual_id", "") if latest_residual else ""
                if not residual_id:
                    error_response(self, HTTPStatus.BAD_REQUEST, "residual_id is required")
                    return
                candidate = build_portfolio_learning_candidate(residual_id)
                json_response(self, {"ok": True, "portfolio_learning_candidate": candidate, "cockpit": build_meta_cockpit()})
            elif parsed.path == "/api/l10/missions/create_default":
                mission = create_default_mission()
                json_response(self, {"ok": True, "mission": mission, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/missions/create":
                title = str(payload.get("title", "")).strip()
                owner_goal = str(payload.get("owner_goal", "")).strip()
                if not title or not owner_goal:
                    error_response(self, HTTPStatus.BAD_REQUEST, "title and owner_goal are required")
                    return
                mission = create_mission(
                    title,
                    owner_goal,
                    str(payload.get("mission_type", "meta_development_strategy")),
                    str(payload.get("allowed_permission_tier", "tier_0")),
                )
                json_response(self, {"ok": True, "mission": mission, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/mission_plan/build":
                plan = build_mission_plan(str(payload.get("mission_id", "")).strip() or None)
                json_response(self, {"ok": True, "mission_plan": plan, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/mission_runner/run_cycle":
                result = run_mission_cycle(str(payload.get("mission_id", "")).strip() or None, int(payload.get("max_cycles", 1)))
                result["cockpit"] = build_mission_cockpit()
                json_response(self, result)
            elif parsed.path == "/api/l10/mission_runner/run_bounded":
                result = run_bounded_mission(str(payload.get("mission_id", "")).strip() or None, int(payload.get("max_cycles", 2)))
                result["cockpit"] = build_mission_cockpit()
                json_response(self, result)
            elif parsed.path == "/api/l10/research_plan/build":
                plan = build_research_plan(str(payload.get("mission_id", "")).strip() or None)
                json_response(self, {"ok": True, "research_plan": plan, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/research/run_fixture_demo":
                result = run_fixture_research_demo(str(payload.get("mission_id", "")).strip() or None)
                result["cockpit"] = build_mission_cockpit()
                json_response(self, result)
            elif parsed.path == "/api/l10/research/run_configured_live_read_only":
                result = run_configured_live_read_only(str(payload.get("mission_id", "")).strip() or None, bool(payload.get("explicitly_enabled", False)))
                result["cockpit"] = build_mission_cockpit()
                json_response(self, result)
            elif parsed.path == "/api/l10/opportunity_signals/extract":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                signals = extract_opportunity_signals(mission["mission_id"])
                json_response(self, {"ok": True, "opportunity_signals": signals, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/meta_strategy_brief/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                brief = build_meta_strategy_brief(mission["mission_id"])
                json_response(self, {"ok": True, "meta_strategy_brief": brief, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/action_plan/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                plan = build_action_plan(mission["mission_id"])
                json_response(self, {"ok": True, "action_plan": plan, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/escalations/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                escalations = build_escalation_packets(mission["mission_id"])
                json_response(self, {"ok": True, "escalation_packets": escalations, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/escalations/decide":
                escalation_id = str(payload.get("escalation_id", "")).strip()
                decision = str(payload.get("decision", "")).strip()
                if not escalation_id or not decision:
                    error_response(self, HTTPStatus.BAD_REQUEST, "escalation_id and decision are required")
                    return
                result = decide_escalation(escalation_id, decision, str(payload.get("decision_note", "")))
                json_response(self, {"ok": True, "escalation_review_decision": result, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/l9_portfolio_update/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                update = build_l9_portfolio_update_packet(mission["mission_id"])
                json_response(self, {"ok": True, "l9_portfolio_update_packet": update, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/completion_report/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                report = build_mission_completion_report(mission["mission_id"])
                json_response(self, {"ok": True, "mission_completion_report": report, "cockpit": build_mission_cockpit()})
            elif parsed.path == "/api/l10/l8_action_loop_escalation/build":
                mission = get_mission(str(payload.get("mission_id", "")).strip() or None)
                packet = build_l8_action_loop_escalation_packet(mission["mission_id"])
                json_response(self, {"ok": True, "l8_action_loop_escalation_packet": packet, "cockpit": build_mission_cockpit()})
            else:
                error_response(self, HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            error_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    if host != "127.0.0.1":
        raise SystemExit("Refusing non-local bind. Use 127.0.0.1.")
    server = ThreadingHTTPServer((host, port), OfficeHandler)
    print(f"Y*Bridge Labs Office: http://{host}:{port}")
    print("Local-only server. Press Ctrl-C to stop.")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
