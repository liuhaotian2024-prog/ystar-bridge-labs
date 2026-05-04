import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_live_test_config_ready_without_production_or_secrets():
    d = json.loads((ROOT / "operations/external_validation/e27_live_test_config_sync.json").read_text())
    assert d["live_test_config_ready"] is True
    assert d["production_live_config_ready"] is False
    assert d["production_live_enabled"] is False
    assert d["credentials_committed"] is False
    assert d["secrets_committed"] is False
    assert all(name.startswith("TEST_ONLY_") for name in d["fake_credential_variable_names"])
