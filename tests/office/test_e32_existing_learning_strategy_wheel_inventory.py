import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_existing_learning_strategy_wheel_inventory_reuses_ecosystem_wheels():
    data = json.loads((ROOT / "operations/external_validation/e32_existing_learning_strategy_wheel_inventory.json").read_text())
    assert data["repos_scanned_count"] == 4
    assert data["existing_learning_strategy_wheels_found"] >= 20
    assert data["reused_wheels_count"] >= 15
    assert data["safe_research_path_available"] is True
    assert data["gov_mcp_modified"] is False
