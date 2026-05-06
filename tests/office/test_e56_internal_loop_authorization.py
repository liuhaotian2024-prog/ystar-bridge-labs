from office.mission_command.e56_internal_loop_authorization import run_internal_loop_authorization


def test_authorization_precedes_dry_run_and_denies_external():
    data = run_internal_loop_authorization()
    assert data["authorization_status"] == "passed"
    assert data["selected_action_authorization"]["authorization_status"] == "dry_run_only"
    assert data["external_action_authorization"]["authorization_status"] == "deny"
    assert data["checks"]["action_has_evidence_path"] is True

