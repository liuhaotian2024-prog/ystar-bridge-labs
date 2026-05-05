import json
from pathlib import Path

from office.mission_command.e37_owner_approval_packet_for_e38 import build_owner_approval_packet_for_e38


ROOT = Path(__file__).resolve().parents[2]


def test_owner_packet_and_czl_closure_are_safe():
    data = build_owner_approval_packet_for_e38()
    assert data["packet_status"] == "created_owner_decision_pending"
    assert data["no_contact_boundary"] is True
    assert data["no_send_boundary"] is True
    assert data["no_publication_boundary"] is True
    closure = json.loads((ROOT / "operations/external_validation/e37_czl_closure.json").read_text())
    assert closure["customer_contact_occurred"] is False
    assert closure["message_sent"] is False
    assert closure["published_externally"] is False
    assert closure["form_submitted"] is False
    assert closure["provider_api_called"] is False
    assert closure["payment_occurred"] is False
    assert closure["customer_validation_claimed"] is False
    assert closure["paid_signal_claimed"] is False
