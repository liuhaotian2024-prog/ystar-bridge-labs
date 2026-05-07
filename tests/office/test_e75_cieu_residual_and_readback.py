import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e75_readback import run_e75_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def test_e75_cieu_residual_has_complete_five_tuple():
    residual = json.loads((ROOT / "operations/external_validation/e75_cieu_residual_for_owner_decision_packet.json").read_text())

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
        assert residual[key]
    assert residual["Y_t_plus_1"]["L3_executed"] is False
    assert residual["R_t_plus_1"]["next_U"] == "E76_Await_or_Record_Owner_Decision_for_L3_Read_Only_Research"
    assert residual["external_action_allowed"] is False
    assert residual["no_overclaim"] is True


def test_e75_readback_and_ceo_brain_answer_owner_decision_state():
    assert run_e75_readback_smoke()["passes"] is True
    context = load_ceo_brain_context({"task_title": "e75 readback", "task_description": "L3 owner decision"})

    assert context["current_l3_owner_decision_packet_status"] == "owner_decision_packet_finalized_no_execution"
    assert context["current_l3_owner_decision_packet_l3_executed"] is False
    assert context["current_l3_owner_decision_packet_owner_approval_status"] == "pending_owner_decision"
    assert context["current_l3_owner_decision_L4_ready"] is False
    assert context["current_l3_owner_decision_L5_ready"] is False
    assert context["current_l3_owner_decision_next_milestone"] == "E76_Await_or_Record_Owner_Decision_for_L3_Read_Only_Research"
    assert context["current_l3_owner_decision_external_action_allowed"] is False
