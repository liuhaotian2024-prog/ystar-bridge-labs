import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_archaeology_reuses_cieu_k9_e65_e67_assets():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_route_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] >= 20
    assert "E65 Market Dynamics Model" in data["what_must_not_be_rebuilt"]
    assert "E67 external validation overlay" in data["what_must_not_be_rebuilt"]
    assert data["reusable_K9Audit_read_only_context"]

