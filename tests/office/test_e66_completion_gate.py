import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_completion_gate_passes_for_confirmed_route_blueprint():
    data = json.loads((ROOT / "operations/external_validation/e66_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] == "e66_model_driven_offer_blueprint_completed_selected_route_confirmed"
    assert data["selected_route"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["recommended_next_milestone"] == "E67_owner_decision_packet_for_controlled_external_review_no_execution"

