from office.mission_command.e55_behavior_center_readback_smoke import load_behavior_center_state_for_brain, run_behavior_center_readback_smoke

def test_ceo_brain_reads_back_behavior_center_state():
    state = load_behavior_center_state_for_brain()
    assert state["external_action_allowed"] is False
    smoke = run_behavior_center_readback_smoke()
    assert smoke["passes"] is True
    assert smoke["checks"]["pending_owner_decision_still_pending"] is True
