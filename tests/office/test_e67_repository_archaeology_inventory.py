import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_repository_archaeology_reuses_existing_model_and_public_read_assets():
    data = json.loads((ROOT / "operations/external_validation/e67_repository_archaeology_inventory.json").read_text())
    assert data["asset_count"] >= 12
    assert "office/mission_command/safe_public_page_reader.py" in data["reusable_public_read_assets"]
    assert "operations/external_validation/e65_market_evidence_quality_model.json" in data["reusable_evidence_quality_model_assets"]
    assert data["archaeology_completed_before_implementation"] is True

