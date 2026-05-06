import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_model_driven_revenue_analysis_answers_profile_questions():
    data = json.loads((ROOT / "operations/external_validation/e66_model_driven_revenue_analysis.json").read_text())
    assert data["analysis_status"] == "completed"
    assert data["top_route_under_fastest_cash_profile"] == "founder_operator_decision_brief_service"
    assert data["top_route_under_strategic_defensibility_profile"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["top_route_under_balanced_CEO_profile"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["still_depends_only_on_T2_public_read_evidence"] if "still_depends_only_on_T2_public_read_evidence" in data else data["comparison_against_E64"]["still_depends_only_on_T2_public_read_evidence"]

