import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_credential_contract_has_no_secrets_or_owner_secret_request():
    d = json.loads((ROOT / "operations/external_validation/e28_secure_credential_source_contract.json").read_text())
    assert d["config_contract_ready"] is True
    assert d["credentials_committed"] is False
    assert d["credential_values_committed"] is False
    assert d["production_credentials_configured"] is False
    assert d["owner_secret_input_requested"] is False
    assert d["production_live_remains_blocked_until_secure_setup"] is True
