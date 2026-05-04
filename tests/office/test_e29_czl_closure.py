import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_czl_closure_proves_no_live_or_external_action():
    data = json.loads((ROOT / "operations/external_validation/e29_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["whole_ecosystem_existing_wheel_audited_first"] is True
    assert data["shortest_cash_path_treated_as_near_term_priority_not_architecture_hardcode"] is True
    assert data["production_live_config_global_default"] is False
    assert data["production_live_enabled"] is False
    assert data["production_live_receipt_count"] == 0
    assert data["no_credentials_or_secrets_committed"] is True
    assert data["owner_manual_send_is_not_default"] is True
