import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_audit_precedes_new_wheels_and_uses_four_repos():
    d = json.loads((ROOT / "operations/external_validation/e28_existing_production_live_wheel_inventory.json").read_text())
    assert d["audit_completed_before_new_e28_modules"] is True
    assert set(d["repos_scanned"]) == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert d["existing_production_live_wheels_found"] >= 28
    assert d["reused_wheels_count"] >= 14
    assert d["newly_built_wheels_count"] == 5
    assert d["gov_mcp_modification_needed"] is False
