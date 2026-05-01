from pathlib import Path

from office.mission_command.e3_cycle import build_e3_cycle


ROOT = Path(__file__).resolve().parents[2]


def test_owner_packet_does_not_approve_customer_contact_by_default():
    packet = build_e3_cycle(ROOT)["owner_decision_packet"]
    assert packet["recommended_next_decision"] == "approve_or_revise_tier1_live_read_only_research_enablement"
    assert "customer contact" in packet["approval_does_not_cover"]
    assert packet["external_action_executed"] is False
    assert packet["options"] == ["approve", "reject", "request_revision", "hold"]


def test_no_external_side_effects():
    cycle = build_e3_cycle(ROOT)
    assert cycle["external_action_executed"] is False
    assert cycle["owner_decision_packet"]["external_action_executed"] is False
    assert cycle["strict_czl"]["full_mission_rt1_score"] > 0


def test_no_coo_invented():
    text = str(build_e3_cycle(ROOT))
    assert "COO" not in text
