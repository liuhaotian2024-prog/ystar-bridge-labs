import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e75_no_external_action_or_forbidden_claims():
    packet = json.loads((ROOT / "operations/external_validation/e75_l3_owner_decision_packet.json").read_text())
    readback = json.loads((ROOT / "operations/external_validation/e75_ceo_readback.json").read_text())
    completion = json.loads((ROOT / "operations/external_validation/e75_completion_report.json").read_text())

    for artifact in [packet, readback, completion]:
        assert artifact["external_action_allowed"] is False
        assert artifact["customer_validation_claimed"] is False
        assert artifact["paid_signal_claimed"] is False
        assert artifact["pricing_validation_claimed"] is False
        assert artifact["compliance_legal_claimed"] is False
        assert artifact["production_deployment_claimed"] is False
        assert artifact["live_ledger_claimed"] is False
    assert packet["L4_ready_claimed"] is False
    assert packet["L5_ready_claimed"] is False
    assert completion["duplicate_K9_Y_star_gov_gov_mcp_core_implementation"] is False
    assert completion["read_only_repos_mutated"] is False


def test_e75_completion_report_says_decision_not_construction():
    completion = json.loads((ROOT / "operations/external_validation/e75_completion_report.json").read_text())

    assert completion["gate_passed"] is True
    assert completion["final_status"] == "e75_l3_owner_decision_packet_finalized_no_execution"
    assert completion["owner_approval_status"] == "pending_owner_decision"
    assert completion["L3_executed"] is False
    assert completion["L4_ready"] is False
    assert completion["L5_ready"] is False
    assert completion["next_step_type"] == "owner_decision_not_construction"
