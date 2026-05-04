import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_czl_closure_proves_no_external_or_fake_evidence():
    data=load("operations/external_validation/e23_czl_closure.json")
    assert data["Rt_plus_1"] == 0
    assert data["no_real_external_action_occurred"] is True
    assert data["no_provider_api_called"] is True
    assert data["no_message_sent"] is True
    assert data["no_live_receipt_created"] is True
    assert data["no_fake_evidence_created"] is True
    assert data["no_fake_suppression_evidence_created"] is True
    assert data["owner_manual_send_is_not_default"] is True
