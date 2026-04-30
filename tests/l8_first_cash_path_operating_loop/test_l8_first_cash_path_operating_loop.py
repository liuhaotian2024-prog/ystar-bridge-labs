import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "scripts/l7_labs_office_web"
RUNNER = ROOT / "scripts/run_l7_labs_office_web.sh"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

from l7_labs_team_self_work_scheduler.scheduler import scheduler_status  # noqa: E402
from l8_first_cash_path_operating_loop import first_cash_path_model as model  # noqa: E402
from l8_first_cash_path_operating_loop.cockpit_model import build_cockpit_snapshot  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_action_builder import build_commercial_actions  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_action_queue import list_commercial_actions  # noqa: E402
from l8_first_cash_path_operating_loop.commercial_residual import build_commercial_residual  # noqa: E402
from l8_first_cash_path_operating_loop.customer_feedback_intake import record_customer_feedback  # noqa: E402
from l8_first_cash_path_operating_loop.first_cash_path_loader import initialize_first_cash_path  # noqa: E402
from l8_first_cash_path_operating_loop.learning_candidate_builder import build_learning_candidate  # noqa: E402
from l8_first_cash_path_operating_loop.manual_send_packet import disabled_tool_send_email_future_slot, list_manual_send_packets, mark_manual_send_packet  # noqa: E402
from l8_first_cash_path_operating_loop.owner_approval_center import decide_action  # noqa: E402
from office_web_builder import build as build_office  # noqa: E402
from office_web_server import serve  # noqa: E402


@pytest.fixture()
def isolated_l8(monkeypatch, tmp_path):
    out = tmp_path / "l8"
    packet_root = out / "runtime_packets"
    dirs = {name: packet_root / name for name in model.PACKET_DIRS}
    monkeypatch.setattr(model, "OUT", out)
    monkeypatch.setattr(model, "PACKET_ROOT", packet_root)
    monkeypatch.setattr(model, "PACKET_DIRS", dirs)
    model.ensure_dirs()
    return out


def approve_first_action():
    actions = build_commercial_actions(force=True)["actions"]
    action = actions[0]
    return action, decide_action(action["action_id"], "approve", "test approval")


def test_first_cash_path_initializes_selected_offer(isolated_l8):
    path = initialize_first_cash_path()
    assert path["selected_offer"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert path["pricing_hypothesis"]["recommended_first_test_usd"] == 1500


def test_no_grant_or_rfp_path_is_created_by_default(isolated_l8):
    actions = build_commercial_actions(force=True)["actions"]
    assert all("grant" not in action["action_type"].lower() for action in actions)
    assert all("rfp" not in action["action_type"].lower() for action in actions)
    assert initialize_first_cash_path()["forbidden_current_routes"] == ["grant/RFP default route", "automatic lead scraping", "automatic outreach send"]


def test_commercial_action_builder_creates_manual_send_actions(isolated_l8):
    actions = build_commercial_actions(force=True)["actions"]
    assert {action["action_type"] for action in actions} == {
        "warm_intro_request",
        "direct_founder_outreach",
        "founder_operator_diagnostic_offer",
    }
    assert all(action["execution_mode"] == "manual_send_packet" for action in actions)


def test_commercial_actions_require_owner_approval(isolated_l8):
    actions = build_commercial_actions(force=True)["actions"]
    assert all(action["approval_required"] is True for action in actions)
    assert all(action["status"] == "pending_owner_approval" for action in actions)


def test_rejected_action_does_not_generate_manual_send_packet(isolated_l8):
    action = build_commercial_actions(force=True)["actions"][0]
    result = decide_action(action["action_id"], "reject", "not this one")
    assert result["manual_send_packet"] is None
    assert list_manual_send_packets() == []


def test_approved_action_generates_manual_send_packet(isolated_l8):
    _, result = approve_first_action()
    assert result["manual_send_packet"]["status"] == "ready_for_owner_manual_send"
    assert result["manual_send_packet"]["tool_send_email_slot"]["enabled"] is False


def test_tool_send_email_slot_is_disabled():
    slot = disabled_tool_send_email_future_slot()
    assert slot["enabled"] is False
    assert slot["can_execute"] is False


def test_mark_manual_send_packet_as_sent_writes_receipt(isolated_l8):
    _, result = approve_first_action()
    receipt = mark_manual_send_packet(result["manual_send_packet"]["packet_id"], "marked_sent_by_owner", "manual test")
    assert receipt["owner_marked_status"] == "marked_sent_by_owner"
    assert receipt["automatic_send_executed"] is False


def test_customer_feedback_intake_writes_packet(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "interested", "asks for sample")
    assert feedback["response_status"] == "interested"
    assert feedback["paid_signal"] is False


def test_feedback_builds_commercial_residual(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "asks_for_more_info", "need details")
    residual = build_commercial_residual(feedback["feedback_id"])
    assert residual["residual_type"] == "offer_specificity_gap"


def test_positive_feedback_builds_positive_signal_residual(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "paid_signal", "wants paid pilot")
    residual = build_commercial_residual(feedback["feedback_id"])
    assert residual["residual_type"] == "positive_signal"


def test_no_response_builds_channel_or_weak_signal_residual(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "no_response", "")
    residual = build_commercial_residual(feedback["feedback_id"])
    assert residual["residual_type"] == "weak_signal_or_channel_mismatch"


def test_learning_candidate_is_review_gated(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "interested", "asks")
    residual = build_commercial_residual(feedback["feedback_id"])
    candidate = build_learning_candidate(residual["residual_id"])
    assert candidate["writeback_allowed"] is False
    assert candidate["review_required"] is True
    assert candidate["owner_review_status"] == "pending_review"


def test_learning_candidate_does_not_write_core_memory(isolated_l8):
    _, result = approve_first_action()
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "no_response", "")
    residual = build_commercial_residual(feedback["feedback_id"])
    candidate = build_learning_candidate(residual["residual_id"])
    assert {"brain", "memory", "canonical strategy", "CIEU DB"} <= set(candidate["forbidden_writeback_targets"])


def test_cockpit_snapshot_contains_full_loop_state(isolated_l8):
    _, result = approve_first_action()
    receipt = mark_manual_send_packet(result["manual_send_packet"]["packet_id"], "marked_sent_by_owner", "sent manually")
    feedback = record_customer_feedback(result["manual_send_packet"]["packet_id"], "interested", "asks for more")
    residual = build_commercial_residual(feedback["feedback_id"])
    candidate = build_learning_candidate(residual["residual_id"])
    cockpit = build_cockpit_snapshot("test_cockpit")
    assert cockpit["selected_first_cash_path"]["selected_offer"] == "Founder AI Workflow Audit & CEO Command Brief Sprint"
    assert cockpit["manual_action_receipts"][0]["receipt_id"] == receipt["receipt_id"]
    assert cockpit["customer_feedback_packets"][0]["feedback_id"] == feedback["feedback_id"]
    assert cockpit["commercial_residuals"][0]["residual_id"] == residual["residual_id"]
    assert cockpit["learning_candidates"][0]["candidate_id"] == candidate["candidate_id"]


def test_l8_api_first_cash_path_status():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l8/first_cash_path/status" in source
    assert "/api/l8/cockpit" in source


def test_l8_api_build_commercial_actions():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l8/commercial_actions/build" in source
    assert "/api/l8/commercial_actions" in source


def test_l8_api_approval_decision():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l8/approvals/decide" in source
    assert "decide_action" in source


def test_l8_api_feedback_and_residual():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    assert "/api/l8/customer_feedback" in source
    assert "/api/l8/residuals/build" in source
    assert "/api/l8/learning_candidates/build" in source


def test_runner_build_status_demo_smoke():
    source = RUNNER.read_text(encoding="utf-8")
    for text in ["L8 package available", "l8_first_cash_path_operating_loop", "demo_ok: L8 first cash path operating loop simulated locally"]:
        assert text in source


def test_no_external_side_effects(isolated_l8):
    build_commercial_actions(force=True)
    cockpit = build_cockpit_snapshot("test_no_side_effects")
    assert cockpit["external_side_effects_occurred"] is False
    assert cockpit["tool_send_email_enabled"] is False


def test_no_coo_invented(isolated_l8):
    text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "l8_first_cash_path_operating_loop").rglob("*") if path.is_file())
    assert "COO" not in text
    assert "coo_invented" in text


def test_existing_l7_scheduler_still_works():
    status = scheduler_status()
    assert status["scheduler_ready"] is True
    assert status["coo_invented"] is False


def test_existing_l7_office_apis_still_work():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    for endpoint in ["/api/whiteboard/message", "/api/route", "/api/scheduler/status"]:
        assert endpoint in source
    with pytest.raises(SystemExit):
        serve("0.0.0.0", 8765)


def test_office_builder_outputs_l8_cockpit():
    build_office()
    html = (ROOT / "l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    summary = json.loads((ROOT / "l8_first_cash_path_operating_loop/l8_summary.json").read_text(encoding="utf-8"))
    assert "L8 First Cash Path Cockpit" in html
    assert summary["first_cash_path_initialized"] is True


def test_runner_build_and_status_modes_pass():
    for mode in ["build", "status"]:
        result = subprocess.run(["bash", str(RUNNER), "--mode", mode], cwd=ROOT, text=True, capture_output=True, check=True, timeout=30)
        assert "error" not in result.stderr.lower()

