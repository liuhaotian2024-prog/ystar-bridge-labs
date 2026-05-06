from office.mission_command.e54_ceo_brain_l5_readiness_gate import run_l5_readiness_gate

def test_l5_readiness_gate_passes_and_keeps_pending_owner_decision():
    data=run_l5_readiness_gate()
    assert data['gate_passed'] is True
    assert data['final_status'] == 'ceo_brain_l5_cognitive_center_ready'
    assert data['owner_decision_status'] == 'pending_owner_decision'
    assert data['external_action_allowed'] is False
