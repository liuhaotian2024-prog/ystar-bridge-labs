import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e74_ceo_l2_readback import run_e74_l2_work_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def test_e74_cieu_residual_has_complete_five_tuple():
    residual = json.loads((ROOT / "operations/external_validation/e74_cieu_residual_for_l2_work_cycle.json").read_text())

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
        assert residual[key]
    assert residual["external_action_allowed"] is False
    assert residual["no_overclaim"] is True
    assert residual["R_t_plus_1"]["next_U"] == "E75_L3_Read_Only_External_Research_Owner_Decision_Packet_Finalization"


def test_e74_readback_and_ceo_brain_include_l2_work_result():
    assert run_e74_l2_work_readback_smoke()["passes"] is True
    context = load_ceo_brain_context({"task_title": "e74 readback", "task_description": "L2 internal work pilot"})

    assert context["current_ceo_l2_work_status"] == "completed_internal_no_external_action"
    assert "L3 Read-Only Research Readiness Packet" in context["current_ceo_l2_work_deliverable"]
    assert context["current_ceo_l2_work_no_new_wheel_compliance"] is True
    assert context["current_ceo_l2_work_l3_status"] == "ready_for_owner_decision_packet_finalization_not_execution"
    assert context["current_ceo_l2_work_next_recommended_milestone"] == "E75_L3_Read_Only_External_Research_Owner_Decision_Packet_Finalization"
    assert context["current_ceo_l2_work_external_action_allowed"] is False


def test_e74_no_forbidden_claims():
    packet = json.loads((ROOT / "operations/external_validation/e74_owner_facing_l3_readiness_packet.json").read_text())
    completion = json.loads((ROOT / "operations/external_validation/e74_completion_report.json").read_text())

    for key in [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "pricing_validation_claimed",
        "compliance_legal_claimed",
        "production_deployment_claimed",
        "live_ledger_claimed",
        "external_action_allowed",
    ]:
        assert packet[key] is False
        assert completion[key] is False
    assert completion["duplicate_K9_Y_star_gov_gov_mcp_core_implementation"] is False
