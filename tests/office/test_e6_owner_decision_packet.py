from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e6_owner_packet_does_not_approve_customer_contact_by_default():
    text = (ROOT / "reports" / "integration" / "e6_owner_decision_packet.md").read_text(encoding="utf-8")
    assert "Customer contact is not approved by default." in text
    assert "publication is not approved" in text.lower()
    assert "form/payment/account actions are not approved" in text.lower()


def test_e6_owner_packet_mentions_receipt_or_blocker():
    text = (ROOT / "reports" / "integration" / "e6_owner_decision_packet.md").read_text(encoding="utf-8")
    assert "receipt_path: reports/integration/e6_tier1_research_budget_receipt.md" in text
    assert "provider_mode: source_seed_live_public_read_only" in text


def test_no_external_sending_email_payment_publication_account_or_form():
    text = (ROOT / "reports" / "integration" / "e6_owner_decision_packet.md").read_text(encoding="utf-8")
    for phrase in ["email/message", "publication", "form submission", "payment", "account creation"]:
        assert phrase in text
    assert "external_action_executed: False" in text
