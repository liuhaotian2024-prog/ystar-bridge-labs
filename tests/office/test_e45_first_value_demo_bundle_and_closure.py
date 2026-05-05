import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_bundle_owner_packet_and_closure():
    bundle = json.loads((ROOT / "operations/external_validation/e45_first_value_demo_bundle.json").read_text())
    owner = json.loads((ROOT / "operations/external_validation/e45_owner_approved_first_external_attempt_packet.unsent.json").read_text())
    closure = json.loads((ROOT / "operations/external_validation/e45_czl_closure.json").read_text())
    assert bundle["name"] == "First Value Demo Bundle: Governed Agent Action Proof Packet"
    assert bundle["customer_validation_claimed"] is False
    assert owner["message_draft_status"] == "unsent"
    assert owner["real_human_targets_identified"] is False
    for key in ["no_customer_contact", "no_expert_contact", "no_send", "no_publish", "no_login", "no_provider_API_or_tool_execution", "no_internet_install", "no_payment", "no_secret_use"]:
        assert closure[key] is True
