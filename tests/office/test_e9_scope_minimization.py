from office.mission_command.e9_scope_minimization import E9ActionScope, build_standard_e9_action_scope, validate_e9_action_scope


def test_scope_minimization_requires_target_channel_draft_count_time_followup_data_scope():
    scope = E9ActionScope("a1", "", "", "", "", "", "", "", "")
    errors = validate_e9_action_scope(scope)
    assert "missing_target_scope" in errors
    assert "missing_channel_scope" in errors
    assert "missing_draft_scope" in errors
    assert "missing_count_scope" in errors
    assert "missing_time_scope" in errors
    assert "missing_followup_scope" in errors
    assert "missing_data_scope" in errors
    assert "missing_feedback_scope" in errors


def test_standard_scope_is_valid():
    assert validate_e9_action_scope(build_standard_e9_action_scope()) == []
