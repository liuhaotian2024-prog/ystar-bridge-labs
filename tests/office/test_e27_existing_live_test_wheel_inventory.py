import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def load(rel): return json.loads((ROOT / rel).read_text())
def test_e27_audit_precedes_new_wheels():
    d = load("operations/external_validation/e27_existing_live_test_wheel_inventory.json")
    assert d["audit_completed_before_new_e27_modules"] is True
    assert set(d["repos_scanned"]) == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert d["existing_live_test_wheels_found"] >= 24
    assert d["reused_wheels_count"] >= 10
    assert d["newly_built_wheels_count"] == 4
    assert d["new_wheel_creation_rule_satisfied"] is True
