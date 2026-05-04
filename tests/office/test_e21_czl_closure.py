import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e21_czl_closure_proves_no_external_effects_and_distinct_receipts():
    data = json.loads((ROOT / "operations/external_validation/e21_czl_closure.json").read_text())
    assert data["Rt_plus_1"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_message_sent"] is True
    assert data["no_live_receipt_created"] is True
    assert data["dry_run_and_live_receipts_remain_distinct"] is True
    assert data["owner_manual_send_is_not_default"] is True
