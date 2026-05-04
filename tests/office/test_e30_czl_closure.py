import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_czl_closure_proves_no_external_action_or_live():
    data = json.loads((ROOT / "operations/external_validation/e30_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["whole_ecosystem_existing_wheel_audited_first"] is True
    assert data["action_space_generated_openly"] is True
    assert data["route_selected_by_method_not_hardcoded_menu"] is True
    assert data["production_config_assumed_next"] is False
    assert data["production_live_enabled"] is False
    assert data["production_live_receipt_count"] == 0
    assert data["no_credentials_or_secrets_committed"] is True
    assert data["owner_manual_send_is_not_default"] is True
