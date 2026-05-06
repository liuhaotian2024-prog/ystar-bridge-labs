import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_cross_selection_finds_overlap_and_fallbacks():
    data = json.loads((ROOT / "operations/external_validation/e64_dual_axis_cross_selection_matrix.json").read_text())
    assert data["does_market_optimal_and_YBridge_unique_overlap"] is True
    assert data["first_cash_wedge"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["fallback_cash_support_route"] == "founder_operator_decision_brief_service"
    assert data["long_term_strategic_direction"] == "AI_agent_company_runtime_harness_deployment_blueprint"
