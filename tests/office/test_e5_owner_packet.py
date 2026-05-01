from pathlib import Path

from office.mission_command.e5_cycle import build_e5_cycle, write_e5_reports


ROOT = Path(__file__).resolve().parents[2]


def test_owner_packet_does_not_approve_customer_contact_by_default():
    packet = build_e5_cycle(ROOT)["owner_packet"]
    assert "customer contact" in " ".join(packet["approval_does_not_cover"])
    assert packet["external_action_executed"] is False
    assert "contact" not in packet["recommended_next_decision"].lower()


def test_owner_packet_mentions_seed_request_or_receipt():
    cycle = build_e5_cycle(ROOT)
    packet = cycle["owner_packet"]
    assert packet["seed_request_path"] or packet["receipt_path"] or packet["blocker_path"]


def test_e5_reports_include_owner_packet_and_seed_request_when_missing():
    written = write_e5_reports(ROOT)
    assert "e5_owner_decision_packet.md" in written
    assert "e5_owner_public_source_seed_request.md" in written
