from office.mission_command.e53_completion_gate import run_e53_completion_gate

def test_completion_gate_pending_owner_decision():
    data = run_e53_completion_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "owner_review_packet_ready_pending_owner_decision"
    assert data["owner_decision_status"] == "pending_owner_decision"
    assert data["external_action_allowed"] is False
