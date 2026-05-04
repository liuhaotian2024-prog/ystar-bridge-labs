import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_route_decision_requires_branch_confirmation_before_e29():
    d = json.loads((ROOT / "operations/external_validation/e28r_route_decision.json").read_text())
    assert d["route_decision"] == "confirm_revenue_mode_branch_before_E29_execution_route"
    assert d["production_live_configuration_global_default"] is False
    assert d["recommended_next_milestone"] == "E29_revenue_mode_branch_selection_confirmation"
    assert d["production_live_enabled"] is False
    assert d["production_live_receipt_count"] == 0
