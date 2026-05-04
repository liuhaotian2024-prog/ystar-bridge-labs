import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(rel): return json.loads((ROOT/rel).read_text())
def test_e26_existing_wheel_audit_precedes_new_wheels():
    d=load("operations/external_validation/e26_existing_live_readiness_wheel_inventory.json")
    assert d["audit_completed_before_new_e26_modules"] is True
    assert set(d["repos_scanned"])=={"ystar-bridge-labs","gov-mcp","Y-star-gov","ystar-company"}
    assert d["existing_live_readiness_wheels_found"]>=15
    assert d["reused_wheels_count"]>=8
    assert d["new_wheel_creation_rule_satisfied"] is True
