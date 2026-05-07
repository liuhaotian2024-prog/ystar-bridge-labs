import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e74_owner_facing_packet_answers_l3_readiness_questions():
    packet = json.loads((ROOT / "operations/external_validation/e74_owner_facing_l3_readiness_packet.json").read_text())

    assert packet["packet_status"] == "owner_reviewable_internal_no_execution"
    assert packet["current_product_route"]["product"] == "Governed Business Operations Blueprint + CIEU Audit Module"
    assert len(packet["exact_L3_read_only_research_questions"]) >= 6
    assert len(packet["source_categories_needed_for_L3"]) >= 6
    assert len(packet["positive_evidence_criteria"]) >= 4
    assert len(packet["negative_evidence_criteria"]) >= 4
    assert "Approve finalization" in packet["recommended_owner_decision"]
    assert packet["owner_decision_status"] == "pending_owner_decision"


def test_e74_l3_allowlist_is_no_execution_owner_approval_packet():
    allowlist = json.loads((ROOT / "operations/external_validation/e74_l3_allowlist_proposal_no_execution.json").read_text())

    assert allowlist["proposal_status"] == "owner_approval_required_before_any_L3_execution"
    assert allowlist["rules"]["no_contact"] is True
    assert allowlist["rules"]["no_publication"] is True
    assert allowlist["rules"]["no_payment"] is True
    assert allowlist["rules"]["no_L3_execution_in_E74"] is True
    assert allowlist["owner_approval_fields"]["owner_approved_L3_execution"] is False
    assert allowlist["maximum_scope_budget_for_future_L3_run"]["source_count_cap"] <= 30
    assert allowlist["external_action_allowed"] is False
