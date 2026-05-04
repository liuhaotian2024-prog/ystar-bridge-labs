import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_route_decision_recommends_manual_send_and_blocks_e16c1():
    data = json.loads((ROOT / "operations/external_validation/e17_route_decision_packet.json").read_text())
    assert data["recommended_route"] == "E17_manual_send_ready"
    assert data["e16c1_real_send_blocked"] is True
    assert data["route_options"]["E16C1_real_send_still_blocked"]["status"] == "blocked"
    assert data["external_action_executed"] is False


def test_route_decision_exposes_owner_next_decisions():
    data = json.loads((ROOT / "operations/external_validation/e17_route_decision_packet.json").read_text())
    for option in ["approve_manual_send", "revise_message", "reject_target", "defer", "import_feedback_if_already_sent_manually"]:
        assert option in data["next_owner_decision_surface"]
