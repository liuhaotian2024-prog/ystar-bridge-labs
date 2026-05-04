import json
from pathlib import Path

from office.mission_command.e17_owner_activation_console import build_final_message_package, build_owner_activation_console

ROOT = Path(__file__).resolve().parents[2]


def _selected_action():
    e17_console = json.loads((ROOT / "operations/external_validation/e17_owner_activation_console.json").read_text())
    return {
        "action_id": e17_console["action_id"],
        "target_id": e17_console["target_id"],
        "target_name": e17_console["target_name"],
        "target_evidence_basis": e17_console["target_evidence_basis"],
        "buyer_pain_hypothesis": e17_console["buyer_pain_hypothesis"],
        "selection_reason": e17_console["why_this_target"],
        "risk_tier": e17_console["risk_tier"],
        "capability_domain": e17_console["capability_domain"],
    }


def test_owner_activation_console_has_single_owner_decision_surface():
    msg = build_final_message_package(_selected_action())
    console = build_owner_activation_console(_selected_action(), msg)
    data = console.to_dict()
    assert data["target_name"] == "Alice Labs AI Operations Consulting"
    assert data["offer"] == "48h AI Agent Implementation Readiness Review"
    assert data["no_send_status"] == "agent_no_send_owner_manual_send_only"
    assert "approve_manual_send" in data["decision_options"]
    assert "revise_message" in data["decision_options"]
    assert data["e16c1_real_send_blocked"] is True
    assert data["external_action_executed"] is False


def test_owner_activation_console_artifact_is_ready_and_no_send():
    data = json.loads((ROOT / "operations/external_validation/e17_owner_activation_console.json").read_text())
    assert data["recommended_owner_action"].startswith("Review one page")
    assert data["no_send_status"] == "agent_no_send_owner_manual_send_only"
    assert "agent email/message send" in data["blocked_actions"]
