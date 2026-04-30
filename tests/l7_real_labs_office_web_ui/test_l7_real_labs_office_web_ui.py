import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_real_labs_office_web_ui"
SCRIPT_DIR = ROOT / "scripts/l7_labs_office_web"
sys.path.insert(0, str(SCRIPT_DIR))

from office_web_builder import build  # noqa: E402
from office_web_server import create_aiden_chat_turn, create_owner_message_packet, create_team_task_packet, serve  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def build_office_ui():
    build()


def load_json(relative_path: str):
    return json.loads((OUT / relative_path).read_text(encoding="utf-8"))


def scoped_text_outputs() -> str:
    chunks = []
    for suffix in ("*.json", "*.md", "*.html", "*.css", "*.js"):
        for path in OUT.rglob(suffix):
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_runner_server_and_builder_exist():
    assert (ROOT / "scripts/run_l7_labs_office_web.sh").exists()
    assert (SCRIPT_DIR / "office_web_server.py").exists()
    assert (SCRIPT_DIR / "office_web_builder.py").exists()


def test_existing_html_audit_exists_and_marks_old_html_not_usable():
    audit = load_json("existing_html_audit.json")
    assert audit["exists"] is True
    assert audit["owner_usable"] is False
    assert audit["has_message_form"] is False
    assert audit["has_team_task_form"] is False
    assert audit["has_api_runtime"] is False


def test_summary_and_runtime_state_exist():
    summary = load_json("web_ui_summary.json")
    state = load_json("office_runtime_state.json")
    assert summary["real_office_web_ui_created"] is True
    assert summary["local_url"] == "http://127.0.0.1:8771"
    assert state["current_phase"] == "Real Labs Office Web UI Runtime"


def test_original_team_roster_loaded_with_no_coo():
    state = load_json("office_runtime_state.json")
    assert state["agent_count"] >= 12
    ids = {agent["agent_id"] for agent in state["agents"]}
    assert "aiden_ceo" in ids
    assert "jinjin_k9_scout" in ids
    for agent in state["agents"]:
        joined = f"{agent['agent_id']} {agent['display_name']} {agent['legacy_role']}".lower()
        assert "coo" not in joined
        assert "operator" not in joined


def test_page_template_contains_aiden_only_chat():
    template = (OUT / "templates/index.html").read_text(encoding="utf-8")
    assert 'id="aiden-chat-form"' in template
    assert 'id="aiden-message"' in template
    assert 'id="chat-history"' in template
    assert "和 Aiden 讨论" in template
    assert "发送给 Aiden" in template
    assert "这里只有一个功能" in template
    assert "没有团队看板" in template
    assert "没有 L8/L9/L10" in template
    assert "NO EXTERNAL SENDING" in template
    assert "message-form" not in template
    assert "team-task-form" not in template
    assert "whiteboard-message-form" not in template
    assert "work-board" not in template
    assert "mode-switch" not in template
    assert "office.js?v=aiden-chat-v1" in template


def test_aiden_chat_js_uses_only_aiden_endpoint():
    js = (OUT / "static/office.js").read_text(encoding="utf-8")
    assert "/api/aiden_chat" in js
    assert "aiden-chat-form" in js
    assert "sendMessage" in js
    assert "loadHistory" in js
    assert "/api/whiteboard/message" not in js
    assert "/api/team_task" not in js
    assert "/api/message" not in js
    assert "sendTeamInstruction" not in js
    assert "quickTemplates" not in js
    assert "compatibility_fallback" not in js
    assert "setOfficeMode" not in js


def test_aiden_only_css_has_chat_layout():
    css = (OUT / "static/office.css").read_text(encoding="utf-8")
    assert "chat-shell" in css
    assert "chat-card" in css
    assert ".message.aiden" in css
    assert ".message.owner" in css
    assert "chat-form" in css
    assert "mode-switch" not in css
    assert "work-board" not in css


def test_runtime_packet_dirs_exist():
    for relative in [
        "runtime_packets/owner_messages",
        "runtime_packets/team_tasks",
        "runtime_packets/routing_decisions",
        "runtime_packets/agent_inboxes",
    ]:
        path = OUT / relative
        assert path.is_dir()
        assert (path / ".gitkeep").exists()


def test_post_message_packet_creation_is_local_only(tmp_path):
    result = create_owner_message_packet(
        {
            "target_agent": "aiden_ceo",
            "objective": "Route this safely",
            "message_text": "Please prepare an internal-only plan.",
            "urgency": "normal",
        },
        out_dir=tmp_path,
    )
    packet = result["packet"]
    assert result["ok"] is True
    assert packet["target_agent"] == "aiden_ceo"
    assert packet["external_side_effects"] is False
    assert packet["core_writeback"] is False
    assert (tmp_path / "runtime_packets/owner_messages").exists()


def test_post_team_task_packet_creation_is_local_only(tmp_path):
    result = create_team_task_packet(
        {
            "task_title": "Prepare office packet",
            "task_description": "Create a local-only work order for Aiden routing.",
        },
        out_dir=tmp_path,
    )
    packet = result["packet"]
    assert result["ok"] is True
    assert packet["target"] == "team"
    assert packet["suggested_lead"] == "Aiden"
    assert packet["external_side_effects"] is False
    assert packet["core_writeback"] is False
    assert (tmp_path / "runtime_packets/team_tasks").exists()


def test_aiden_chat_turn_creation_is_local_only(tmp_path):
    result = create_aiden_chat_turn(
        {"message": "Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？"},
        out_dir=tmp_path,
    )
    assert result["ok"] is True
    assert result["reply"]["speaker"] == "aiden_ceo"
    assert "Founder AI Workflow Audit" in result["reply"]["text"]
    assert result["external_side_effects"] is False
    assert result["core_writeback"] is False
    assert (tmp_path / "runtime_packets/aiden_chat/aiden_chat_thread.json").exists()


def test_server_refuses_non_local_bind():
    with pytest.raises(SystemExit):
        serve("0.0.0.0", 8765)


def test_no_ask_user_url_external_side_effects_or_core_writeback():
    receipt = load_json("office_web_no_action_receipt.json")
    assert receipt["ask_user_url_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    assert receipt["email_sent"] is False
    assert receipt["customer_contacted"] is False


def test_no_secret_serialization():
    lowered = scoped_text_outputs().lower()
    assert "tvly-" not in lowered
    assert "bearer " not in lowered
    assert "api_key=" not in lowered
    assert "api-key" not in lowered


def test_no_db_wal_shm_log_active_agent_content_read():
    receipt = load_json("office_web_no_action_receipt.json")
    assert receipt["db_log_wal_shm_active_agent_marker_content_read"] is False


def test_smoke_mode_works():
    result = subprocess.run(
        ["bash", "scripts/run_l7_labs_office_web.sh", "--mode", "smoke"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "smoke_ok" in result.stdout
