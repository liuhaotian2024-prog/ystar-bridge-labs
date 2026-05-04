import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_e22_czl_closure_proves_no_external_action_and_live_blocked():
    data = load("operations/external_validation/e22_czl_closure.json")
    assert data["Rt_plus_1"] == 0
    assert data["selected_count"] == 5
    assert data["dry_run_executed_count"] == 5
    assert data["live_receipt_count"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_message_sent"] is True
    assert data["no_live_receipt_created"] is True
