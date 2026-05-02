from office.mission_command.e9_owner_decision_packet import build_e9_owner_decision_packet


def test_e9_owner_packet_mentions_pattern_mining_findings():
    packet = build_e9_owner_decision_packet({"top_patterns_adopted": ["HITL"], "runtime_upgrades": [], "validation_signal": "blocked_no_feedback"})
    assert "HITL" in packet["top_patterns_adopted"]


def test_e9_owner_packet_recommends_paid_pilot_only_after_positive_signal():
    packet = build_e9_owner_decision_packet({"validation_signal": "blocked_no_feedback", "execution": {}})
    assert packet["recommended_next_decision"] != "approve_E10_paid_pilot_prep"
    positive = build_e9_owner_decision_packet({"validation_signal": "strong_positive", "execution": {"executed": True}})
    assert positive["recommended_next_decision"] == "approve_E10_paid_pilot_prep"
