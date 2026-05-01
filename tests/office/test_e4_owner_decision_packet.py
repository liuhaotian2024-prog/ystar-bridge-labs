from pathlib import Path

from office.mission_command.e4_cycle import build_e4_cycle


ROOT = Path(__file__).resolve().parents[2]


def test_owner_packet_does_not_approve_customer_contact_by_default():
    packet = build_e4_cycle(ROOT)["owner_packet"]
    assert "customer contact" in packet["approval_does_not_cover"]
    assert packet["external_action_executed"] is False
    assert packet["options"] == ["approve", "reject", "request_revision", "hold"]


def test_owner_packet_mentions_receipt_or_blocker():
    packet = build_e4_cycle(ROOT)["owner_packet"]
    provider = packet["provider_status"]
    assert provider["blocker_path"] or provider["receipt_path"]
    assert packet["exact_next_owner_action"]


def test_no_external_sending_customer_contact_email_payment_publication_account_form_core_writeback():
    packet = build_e4_cycle(ROOT)["owner_packet"]
    denied = " ".join(packet["approval_does_not_cover"])
    for item in ["customer contact", "email", "publication", "payment", "account creation", "form submission", "core DB"]:
        assert item in denied


def test_no_obligation_auto_registration_cieu_write_no_coo():
    text = str(build_e4_cycle(ROOT))
    assert "obligation registration" in text
    assert "CIEU" in text
    assert "COO" not in text
