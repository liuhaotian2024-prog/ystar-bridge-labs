from office.mission_command.e44a_full_history_replay_cascade import PRE_E31_FAMILIES, run_full_history_cognition_replay

TASK = {
    "task_title": "E43 full history replay",
    "task_description": "Prepare fastest credible path toward one real external user installing and understanding agent-company runtime value.",
}

def test_full_history_replay_invokes_pre_e31_families():
    result = run_full_history_cognition_replay(TASK)
    invoked = [item["family"] for item in result["pre_E31_capability_effects"] if item["invoked"]]
    for expected in PRE_E31_FAMILIES:
        assert expected in invoked
    assert result["full_history_route_adjustment"]["route_changed"] is True
    assert result["no_external_action"] is True
    assert result["customer_validation_claimed"] is False
