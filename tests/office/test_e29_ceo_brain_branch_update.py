import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_brain_tracks_branch_scope_and_next_horizon():
    data = json.loads((ROOT / "operations/external_validation/e29_ceo_brain_branch_update.json").read_text())
    assert data["active_branch"] == "revenue_mode_shortest_cash_path"
    assert data["selected_route"] == "secure_production_config_preparation"
    assert data["production_live_config_recommendation_scope"] == "branch_scoped_to_revenue_mode_shortest_cash_path"
    assert data["next_decision_horizon"] == "E30_secure_production_config_preparation_for_shortest_cash_path"
    assert data["owner_manual_send_default"] is False
