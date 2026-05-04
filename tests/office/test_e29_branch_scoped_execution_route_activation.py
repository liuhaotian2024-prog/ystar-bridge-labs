import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_branch_scoped_route_recommends_config_only_for_active_branch():
    data = json.loads((ROOT / "operations/external_validation/e29_branch_scoped_execution_route_activation.json").read_text())
    assert data["selected_route"] == "secure_production_config_preparation"
    assert data["production_live_config_recommended"] is True
    assert data["production_live_config_recommendation_scope"] == "active_branch_only"
    assert data["production_live_config_global_default"] is False
    assert data["evidence_expansion_recommended"] is True
    assert data["canary_executed"] is False
    assert data["production_live_enabled"] is False
    assert data["production_live_receipt_count"] == 0
