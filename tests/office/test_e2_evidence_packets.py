from pathlib import Path

from office.mission_command.evidence_packet_builder import (
    build_external_evidence_packets,
    build_internal_evidence_packets,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_internal_evidence_packets_created():
    packets = build_internal_evidence_packets(REPO_ROOT)
    assert len(packets) >= 5
    assert any(packet["category"] == "commercial_history" for packet in packets)
    assert all(packet["private_or_secret_content_included"] is False for packet in packets)


def test_external_evidence_packets_mark_missing_live_evidence():
    packets = build_external_evidence_packets(REPO_ROOT)
    assert packets
    assert all(packet["live_market_evidence"] is False for packet in packets)
    assert any(packet["packet_id"] == "external_not_available" for packet in packets)
