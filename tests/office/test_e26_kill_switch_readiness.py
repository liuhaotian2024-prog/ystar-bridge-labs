import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_kill_switch_defaults_safe():
    d=json.loads((ROOT/"operations/external_validation/e26_kill_switch_readiness.json").read_text())
    assert d["kill_switch_ready"] is True
    assert d["live_execution_allowed_now"] is False
    assert "global_live_disabled" in d["reason_codes"]
    assert "action" in d["supported_scopes"]
