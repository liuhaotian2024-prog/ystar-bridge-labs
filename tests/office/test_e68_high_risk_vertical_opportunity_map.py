import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_high_risk_vertical_map_includes_cieu_module_and_verticals():
    data = json.loads((ROOT / "operations/external_validation/e68_high_risk_vertical_opportunity_map.json").read_text())
    assert data["vertical_count"] >= 10
    selected = set(data["selected_verticals"])
    assert "governed_business_operations_blueprint_CIEU_module" in selected
    assert "K9Audit_backed_CIEU_tamper_evident_ledger" in selected

