import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_route_selection_is_methodological_not_preset():
    data = json.loads((ROOT / "operations/external_validation/e30_methodological_route_selection.json").read_text())
    assert data["selected_route"] == "paid_readiness_review_signal_package"
    assert data["selected_by_method_not_menu"] is True
    assert data["production_config_selected"] is False
    assert data["future_branch_optionality_preserved"] is True
    assert any(route["route"] == "production_live_canary" for route in data["blocked_routes"])
