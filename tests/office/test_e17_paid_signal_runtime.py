import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_paid_signal_packet_is_ready_but_does_not_claim_customer_signal():
    data = json.loads((ROOT / "operations/external_validation/e17_paid_signal_readiness_packet.json").read_text())
    assert data["current_feedback_state"] == "no_response_yet"
    assert data["paid_signal_strength"] == 0
    assert data["next_allowed_commercial_action"] == "owner_manual_send_first"
    assert data["cieU_writeback_allowed"] is False
    assert data["external_action_executed"] is False


def test_paid_signal_packet_allows_no_send_provider_preparation_only():
    data = json.loads((ROOT / "operations/external_validation/e17_paid_signal_readiness_packet.json").read_text())
    assert data["provider_adapter_preparation_allowed"] is True
    assert any("no-send" in item for item in data["limitations"])
