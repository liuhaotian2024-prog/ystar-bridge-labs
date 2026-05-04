import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_czl_closure_proves_no_real_external_action():
    data = json.loads((ROOT / "operations/external_validation/e25_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_customer_contacted"] is True
    assert data["no_message_sent"] is True
    assert data["no_live_receipt_created"] is True
    assert data["owner_manual_send_is_not_default"] is True
