from office.mission_command.e53_first_user_review_risk_gate import evaluate_first_user_review_risk_gate

def test_risk_gate_blocks_pending_owner_decision():
    data = evaluate_first_user_review_risk_gate()
    assert data["gate_status"] == "blocked_pending_owner_decision"
    assert data["external_action_allowed"] is False
    assert data["checks"]["no_real_reviewer_identified"] is True
    assert data["checks"]["no_outreach_sent"] is True
