import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_l4_packet_is_owner_facing_and_no_execution():
    packet = _load("operations/external_validation/e79_l4_owner_decision_packet_no_external_action.json")

    assert packet["packet_status"] == "owner_reviewable_no_execution"
    assert packet["owner_approval_status"] == "pending_owner_decision"
    assert packet["L4_execution_authorized"] is False
    assert packet["external_action_allowed"] is False
    assert "why_generic_ai_governance_is_insufficient" in packet
    assert packet["recommended_frontstage_message"]
    assert packet["recommended_backstage_explanation"]


def test_e79_l4_packet_contains_actionable_feedback_plan():
    packet = _load("operations/external_validation/e79_l4_owner_decision_packet_no_external_action.json")

    assert packet["target_buyer_profile"]
    assert packet["trigger_event"]
    assert "what_to_ask" in packet and len(packet["what_to_ask"]) >= 3
    assert "what_not_to_ask" in packet and "do not ask for purchase commitment" in packet["what_not_to_ask"]
    assert packet["feedback_receipt_schema"]["customer_validation_claimed"] is False
    assert packet["feedback_receipt_schema"]["paid_signal_claimed"] is False
    assert packet["success_criteria"]
    assert packet["failure_criteria"]

