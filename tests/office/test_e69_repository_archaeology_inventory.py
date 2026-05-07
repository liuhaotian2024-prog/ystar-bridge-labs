import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e69_archaeology_reuses_installed_state_assets():
    data = json.loads((ROOT / "operations/external_validation/e69_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] >= 8
    assert "E65 market dynamics model" in data["what_must_not_be_rebuilt"]
    assert "E68 CIEU route model" in data["what_must_not_be_rebuilt"]
    assert "office/mission_command/e68_ceo_cieu_route_readback.py" in data["reusable_CEO_state_loaders"]

