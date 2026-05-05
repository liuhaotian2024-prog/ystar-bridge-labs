import json
from pathlib import Path

from office.mission_command.e33_agent_action_black_box_builder import build_agent_action_black_box_demo_record


ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / "operations" / "external_validation" / f"{name}.json").read_text())


def test_black_box_record_schema_and_boundaries():
    record = build_agent_action_black_box_demo_record()
    for section in [
        "action_identity",
        "declared_intent",
        "evidence_chain",
        "authorization_and_boundary",
        "execution_trace",
        "outcome_and_residual",
        "learning_eligibility",
        "buyer_visible_summary",
    ]:
        assert section in record
    assert record["action_identity"]["source_milestone"] == "E31"
    assert record["authorization_and_boundary"]["customer_contact_allowed"] is False
    assert record["authorization_and_boundary"]["send_allowed"] is False
    assert record["authorization_and_boundary"]["publication_allowed"] is False
    assert record["authorization_and_boundary"]["provider_send_api_allowed"] is False
    assert record["authorization_and_boundary"]["production_live_allowed"] is False
    assert record["learning_eligibility"]["customer_feedback"] == "none"
    assert record["learning_eligibility"]["paid_signal"] == "none"
    assert record["learning_eligibility"]["canonical_learning_eligibility"] is False


def test_buyer_packet_contains_non_claims_and_no_fake_evidence_audit():
    packet = read("e33_agent_action_black_box_demo_packet")
    buyer = read("e33_black_box_buyer_view")
    audit = read("e33_black_box_no_fake_evidence_audit")
    assert packet["packet_status"] == "created_no_send"
    assert "No customer validation yet." in packet["clear_non_claims"]
    assert "customer validation" in " ".join(buyer["what_it_does_not_prove"])
    assert audit["audit_status"] == "passed"
    assert audit["customer_feedback_claimed"] is False
    assert audit["paid_signal_claimed"] is False
    assert audit["provider_api_send_occurred"] is False
    assert audit["production_live_execution_occurred"] is False
