import json
from pathlib import Path

from office.mission_command.e38_owner_decision_packet_for_e39 import build_owner_decision_packet_for_e39


ROOT = Path(__file__).resolve().parents[2]


def test_owner_packet_and_czl_closure_are_safe():
    data = build_owner_decision_packet_for_e39()
    assert data["recommended_option"].startswith("A")
    assert data["final_product_selected"] is False
    closure = json.loads((ROOT / "operations/external_validation/e38_czl_closure.json").read_text())
    for key in ["customer_contact_occurred", "expert_contact_occurred", "message_sent", "published_externally", "form_submitted", "login_occurred", "provider_api_called", "payment_occurred", "customer_validation_claimed", "paid_signal_claimed"]:
        assert closure[key] is False
    assert closure["evidence_receipts_generated_only_for_real_public_sources"] is True
