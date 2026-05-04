import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_czl_closure_proves_no_external_action_and_no_production_live():
    d = json.loads((ROOT / "operations/external_validation/e27_czl_closure.json").read_text())
    assert d["Rt_plus_1"] == 0
    assert d["whole_ecosystem_existing_wheel_audited_first"] is True
    assert d["no_real_external_action_occurred"] is True
    assert d["no_provider_api_called"] is True
    assert d["no_customer_contacted"] is True
    assert d["no_message_sent"] is True
    assert d["production_live_mode_not_enabled"] is True
    assert d["production_live_receipt_count"] == 0
    assert d["owner_manual_send_is_not_default"] is True
