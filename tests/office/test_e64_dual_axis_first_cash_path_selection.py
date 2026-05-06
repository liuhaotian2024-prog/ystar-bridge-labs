import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_final_selection_uses_both_axes_not_defaulting_to_e63():
    data = json.loads((ROOT / "operations/external_validation/e64_dual_axis_first_cash_path_selection.json").read_text())
    assert data["best_open_world_market_optimal_path"] == "founder_operator_decision_brief_service"
    assert data["best_YBridge_unique_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["selected_final_first_cash_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert data["E63_selected_path_survives_dual_axis_retest"] is True
    assert "refined_into_hybrid" in data["E63_selected_path_result"]
    assert data["external_action_allowed"] is False
