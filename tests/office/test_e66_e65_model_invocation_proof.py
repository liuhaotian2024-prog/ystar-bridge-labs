import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_invokes_e65_model_api_not_copying_outputs():
    data = json.loads((ROOT / "operations/external_validation/e66_e65_model_invocation_proof.json").read_text())
    assert data["invocation_status"] == "passed"
    assert data["E65_model_actually_used_instead_of_copied"] is True
    assert data["profile_top_routes"]["fastest_cash_profile"] == "founder_operator_decision_brief_service"
    assert data["profile_top_routes"]["balanced_CEO_profile"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["returned_decision_stability_score"] == 60.0

