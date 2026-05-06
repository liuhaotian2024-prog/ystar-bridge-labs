import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e66_repository_archaeology_reuses_e65_assets():
    data = json.loads((ROOT / "operations/external_validation/e66_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] >= 10
    assert "office/mission_command/e65_market_dynamics_model.py" in data["E65_model_API_assets_reused"]
    assert data["archaeology_completed_before_blueprint"] is True

