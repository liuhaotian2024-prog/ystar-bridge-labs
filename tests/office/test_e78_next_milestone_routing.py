import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e78_next_milestone_is_l4_packet_prep_not_l4_execution_or_l5():
    proposal = json.loads((ROOT / "operations/external_validation/e78_generated_next_milestone_proposal.json").read_text())
    assessment = json.loads((ROOT / "operations/external_validation/e78_l3_post_run_readiness_assessment.json").read_text())

    assert proposal["selected_next_milestone"] == "E79_L4_Owner_Decision_Packet_Preparation_No_External_Action"
    assert proposal["type"] == "owner_decision_preparation_not_execution"
    assert "L4_execution" in proposal["not_selected"]
    assert "L5_revenue_work" in proposal["not_selected"]
    assert assessment["L4_owner_decision_packet_preparation_justified"] is True
    assert assessment["L4_execution_ready"] is False
    assert assessment["L5_revenue_ready"] is False

