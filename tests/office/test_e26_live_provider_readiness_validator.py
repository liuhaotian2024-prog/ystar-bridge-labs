import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_live_provider_readiness_remains_blocked():
    d=json.loads((ROOT/"operations/external_validation/e26_live_provider_readiness_validator.json").read_text())
    assert d["live_ready"] is False
    assert d["live_ready_action_count"]==0
    assert d["live_blocked_action_count"]==1
    assert "live_enabled_false" in d["reason_codes"]
    assert "global_live_disabled" in d["reason_codes"]
