import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e64_ceo_brain_reads_dual_axis_state_back():
    data = json.loads((ROOT / "operations/external_validation/e64_ceo_brain_readback_smoke_result.json").read_text())
    assert data["passes"] is True
    state = data["observed_state"]
    assert state["best_market_optimal_path"] == "founder_operator_decision_brief_service"
    assert state["best_YBridge_unique_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert state["selected_final_first_cash_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert state["external_action_allowed"] is False
