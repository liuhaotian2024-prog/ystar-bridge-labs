import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_kill_switch_block_and_allow_profiles_are_test_only():
    d = json.loads((ROOT / "operations/external_validation/e27_kill_switch_live_test_gate.json").read_text())
    assert d["kill_switch_test_gate_ready"] is True
    assert d["block_profile_passed"] is True
    assert d["allow_profile_passed"] is True
    assert d["allow_profile_scope"] == "non_production_live_test_only"
    assert d["production_live_remains_blocked"] is True
