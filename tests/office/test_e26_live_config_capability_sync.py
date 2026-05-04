import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_live_config_has_schema_but_no_secrets_or_live_enablement():
    d=json.loads((ROOT/"operations/external_validation/e26_live_config_capability_sync.json").read_text())
    assert d["live_config_schema_ready"] is True
    assert d["credential_values_committed"] is False
    assert d["secrets_committed"] is False
    assert d["live_enabled"] is False
    assert "live_enabled_false" in d["live_blocked_reason"]
