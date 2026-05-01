from pathlib import Path

from office.mission_command.e2_cycle import build_e2_cycle


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_top_two_sample_deliverables_are_generated():
    cycle = build_e2_cycle(REPO_ROOT)
    assert len(cycle["sample_deliverables"]) == 2
    assert all(deliverable["title"].startswith("Sample:") for deliverable in cycle["sample_deliverables"])


def test_owner_decision_packet_does_not_approve_customer_contact_by_default():
    packet = build_e2_cycle(REPO_ROOT)["owner_decision_packet"]
    assert "customer contact" in packet["approval_does_not_cover"]
    assert packet["options"] == ["approve", "reject", "request_revision", "hold"]


def test_no_customer_contact_email_payment_publication_account_form():
    packet = build_e2_cycle(REPO_ROOT)["owner_decision_packet"]
    denied = " ".join(packet["approval_does_not_cover"])
    assert "customer contact" in denied
    assert "email/message sending" in denied
    assert "payment" in denied
    assert "publication" in denied
    assert "account creation" in denied
    assert "form submission" in denied
