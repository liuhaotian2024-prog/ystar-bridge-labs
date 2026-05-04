import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_existing_wheel_audit_precedes_e28r_build():
    d = json.loads((ROOT / "operations/external_validation/e28r_existing_revenue_mode_wheel_inventory.json").read_text())
    assert d["audit_completed_before_new_e28r_modules"] is True
    assert d["repos_scanned_count"] == 4
    assert d["existing_revenue_mode_wheels_found"] >= 15
    assert d["newly_built_wheels_count"] == 3
    assert d["new_wheel_creation_rule_satisfied"] is True
