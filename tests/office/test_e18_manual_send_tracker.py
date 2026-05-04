import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_manual_send_tracker_does_not_claim_sent():
    data = json.loads((ROOT / "operations/external_validation/e18_manual_send_tracker.json").read_text())
    assert data["sent_count_placeholder"] == 0
    for row in data["rows"]:
        assert row["current_state"] == "not_approved"
        assert row["manual_send_claimed"] is False
        assert row["real_send_receipt_present"] is False
        assert row["external_action_executed"] is False
