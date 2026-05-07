import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_live_internal_decision_passes_validator_before_acceptance():
    packet = _load("operations/external_validation/e81_live_internal_decision_pre_action_packet.json")
    result = _load("operations/external_validation/e81_live_internal_decision_validator_result.json")
    residual = _load("operations/external_validation/e81_live_internal_decision_post_action_residual.json")

    assert packet["selected_action"] == "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch"
    assert result["decision"] == "ALLOW"
    assert residual["linked_pre_action_packet_id"] == packet["packet_id"]
    assert residual["YstarGov_sync_status"] == "pending_owner_approved_patch"


def test_e81_live_internal_decision_remains_internal_and_owner_gated():
    packet = _load("operations/external_validation/e81_live_internal_decision_pre_action_packet.json")

    assert packet["safety_boundary"]["external_action_allowed"] is False
    assert packet["safety_boundary"]["Y_star_gov_mutation_allowed"] is False
    assert packet["owner_approval_state"] == "pending_owner_decision"
