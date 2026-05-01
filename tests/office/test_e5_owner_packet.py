from office.mission_command.e5_cycle import build_e5_cycle, write_e5_reports


def _missing_seed_repo(tmp_path):
    inspection = tmp_path / "reports" / "integration" / "e5_implementation_inspection.md"
    inspection.parent.mkdir(parents=True)
    inspection.write_text("inspection", encoding="utf-8")
    return tmp_path


def test_owner_packet_does_not_approve_customer_contact_by_default(tmp_path):
    packet = build_e5_cycle(_missing_seed_repo(tmp_path))["owner_packet"]
    assert "customer contact" in " ".join(packet["approval_does_not_cover"])
    assert packet["external_action_executed"] is False
    assert "contact" not in packet["recommended_next_decision"].lower()


def test_owner_packet_mentions_seed_request_or_receipt(tmp_path):
    cycle = build_e5_cycle(_missing_seed_repo(tmp_path))
    packet = cycle["owner_packet"]
    assert packet["seed_request_path"] or packet["receipt_path"] or packet["blocker_path"]


def test_e5_reports_include_owner_packet_and_seed_request_when_missing(tmp_path):
    written = write_e5_reports(_missing_seed_repo(tmp_path))
    assert "e5_owner_decision_packet.md" in written
    assert "e5_owner_public_source_seed_request.md" in written
