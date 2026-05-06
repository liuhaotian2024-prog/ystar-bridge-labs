import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e65_completion_gate_passes_when_model_is_integrated():
    data = json.loads((ROOT / "operations/external_validation/e65_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] == "e65_ceo_market_dynamics_intelligence_model_v1_integrated"
    assert data["domain_count"] >= 30
    assert data["signal_type_count"] == 20
    assert data["scoring_axis_count"] >= 14
    assert data["recommended_next_milestone"] == "E66_selected_route_offer_blueprint_using_market_dynamics_model_no_execution"
