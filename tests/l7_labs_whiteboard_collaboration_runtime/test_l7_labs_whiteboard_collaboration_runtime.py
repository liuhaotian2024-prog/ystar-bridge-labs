import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
WEB_OUT = ROOT / "l7_real_labs_office_web_ui"
L75_OUT = ROOT / "l7_labs_whiteboard_collaboration_runtime"
SCRIPT_DIR = ROOT / "scripts/l7_labs_office_web"
sys.path.insert(0, str(SCRIPT_DIR))

from office_web_builder import build  # noqa: E402
from office_web_server import serve  # noqa: E402
from team_router import known_agent_ids, route_owner_goal  # noqa: E402
from whiteboard_store import (  # noqa: E402
    PACKET_ROOT,
    create_whiteboard_message,
    create_work_item,
    load_approval_requests,
    load_agent_replies,
    load_work_items,
)
from work_cycle_engine import create_completion_report, route_latest_or_payload, run_team_work_cycle, run_work_cycle  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def build_runtime():
    build()


@pytest.fixture()
def packet_root():
    root = PACKET_ROOT / "_test_l7_5_packets"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    yield root
    if root.exists():
        shutil.rmtree(root)


def load_l75(relative_path: str):
    return json.loads((L75_OUT / relative_path).read_text(encoding="utf-8"))


def scoped_text_outputs() -> str:
    chunks = []
    for folder in [L75_OUT, WEB_OUT / "templates", WEB_OUT / "static", SCRIPT_DIR]:
        for suffix in ("*.json", "*.md", "*.html", "*.css", "*.js", "*.py"):
            for path in folder.rglob(suffix):
                chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_whiteboard_schemas_exist():
    required = [
        "whiteboard_message_schema",
        "whiteboard_thread_schema",
        "work_item_schema",
        "routing_decision_schema",
        "agent_reply_schema",
        "work_cycle_schema",
        "completion_report_schema",
        "approval_request_schema",
    ]
    for name in required:
        assert (L75_OUT / "schemas" / f"{name}.json").exists()


def test_server_exposes_whiteboard_endpoints():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    for endpoint in [
        "/api/whiteboard",
        "/api/whiteboard/threads",
        "/api/work_board",
        "/api/timeline",
        "/api/whiteboard/message",
        "/api/route",
        "/api/work_cycle",
        "/api/team_work_cycle",
        "/api/completion_report",
    ]:
        assert endpoint in source


def test_template_contains_whiteboard_work_board_agent_panel_and_timeline():
    template = (WEB_OUT / "templates/index.html").read_text(encoding="utf-8")
    assert "Team Whiteboard / Chat" in template
    assert 'id="whiteboard-message-form"' in template
    assert 'id="whiteboard-send-status"' in template
    assert 'id="work-board"' in template
    assert 'id="agent-panel"' in template
    assert 'id="progress-timeline"' in template


def test_js_can_submit_whiteboard_and_work_cycle_paths():
    js = (WEB_OUT / "static/office.js").read_text(encoding="utf-8")
    for endpoint in ["/api/whiteboard/message", "/api/route", "/api/work_cycle", "/api/team_work_cycle", "/api/completion_report"]:
        assert endpoint in js
    assert "compatibility_fallback" in js
    assert "/api/team_task" in js
    assert "/api/message" in js


def test_routing_engine_uses_original_agents_and_no_coo():
    routing = route_owner_goal("团队请分析最快拿到第一笔钱，同时不牺牲长期战略", "whole_team")
    assigned = [routing["primary_agent"], *routing["supporting_agents"]]
    assert "aiden_ceo" in assigned
    assert "zara_cso" in assigned
    assert "marco_cfo" in assigned
    assert "sofia_cmo" in assigned
    assert "jinjin_k9_scout" in assigned
    assert "coo" not in " ".join(known_agent_ids()).lower()
    assert routing["coo_invented"] is False


def test_owner_message_packet_can_be_created_locally(packet_root):
    message = create_whiteboard_message("请团队分析下一步。", target="whole_team", objective="safe internal plan", packet_root=packet_root)
    assert message["sender_type"] == "owner"
    assert message["external_side_effects"] is False
    assert message["core_writeback"] is False
    assert list((packet_root / "whiteboard_threads").glob("*.json"))


def test_team_task_work_item_can_be_created_locally(packet_root):
    item = create_work_item("Prepare plan", "Local-only task", None, assigned_agents=["aiden_ceo"], packet_root=packet_root)
    assert item["status"] == "Inbox"
    assert load_work_items(packet_root)[0]["work_item_id"] == item["work_item_id"]


def test_work_cycle_creates_agent_replies_and_updates_status(packet_root):
    create_whiteboard_message("团队请分析最快拿到第一笔钱。", target="whole_team", packet_root=packet_root)
    routed = route_latest_or_payload(packet_root=packet_root)
    result = run_work_cycle(routed["work_item"]["work_item_id"], packet_root=packet_root)
    assert result["agent_replies"]
    item = result["work_item"]
    assert item["status"] in {"Done", "Waiting for Approval"}
    assert load_agent_replies(packet_root)


def test_completion_report_can_be_created(packet_root):
    create_whiteboard_message("请 Aiden 安排本地内部分析。", target="whole_team", packet_root=packet_root)
    routed = route_latest_or_payload(packet_root=packet_root)
    run_work_cycle(routed["work_item"]["work_item_id"], packet_root=packet_root)
    report = create_completion_report(routed["work_item"]["work_item_id"], packet_root=packet_root)
    assert report["ok"] is True
    assert report["completion_report"]["work_item_id"] == routed["work_item"]["work_item_id"]


def test_approval_request_is_created_when_needed(packet_root):
    create_whiteboard_message("请准备 outreach email send 和 publication。", target="whole_team", packet_root=packet_root)
    routed = route_latest_or_payload(packet_root=packet_root)
    result = run_work_cycle(routed["work_item"]["work_item_id"], packet_root=packet_root)
    assert result["approval_request"] is not None
    assert load_approval_requests(packet_root)


def test_team_work_cycle_processes_bounded_items(packet_root):
    create_whiteboard_message("团队请做一个内部白板计划。", target="whole_team", packet_root=packet_root)
    route_latest_or_payload(packet_root=packet_root)
    result = run_team_work_cycle(max_work_items_per_cycle=3, packet_root=packet_root)
    assert result["ok"] is True
    assert len(result["items_processed"]) <= 3


def test_server_binds_to_localhost_only():
    with pytest.raises(SystemExit):
        serve("0.0.0.0", 8765)


def test_demo_scenario_exists():
    demo = load_l75("demo_scenarios/demo_first_cash_path_team_discussion.json")
    assert "团队请一起分析" in demo["owner_message"]
    agent_ids = {reply["agent_id"] for reply in demo["agent_replies"]}
    assert {"aiden_ceo", "zara_cso", "marco_cfo", "sofia_cmo", "jinjin_k9_scout", "ethan_cto", "samantha_secretary"} <= agent_ids


def test_no_action_receipt_and_no_unsafe_serialization():
    receipt = load_l75("l7_5_no_action_receipts/l7_5_no_action_receipt.json")
    assert receipt["outreach_occurred"] is False
    assert receipt["actual_memory_brain_canonical_cieu_db_writeback_occurred"] is False
    assert receipt["db_log_wal_shm_active_agent_marker_content_read"] is False
    lowered = scoped_text_outputs().lower()
    assert "tvly-" not in lowered
    assert "bearer " not in lowered
    assert "api_key=" not in lowered
