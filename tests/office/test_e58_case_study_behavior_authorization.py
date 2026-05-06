from office.mission_command.e58_case_study_behavior_authorization import run_case_study_behavior_authorization


def test_case_study_behavior_authorization_allows_internal_and_denies_external():
    data = run_case_study_behavior_authorization()
    assert data["passed"] is True
    assert data["allowed_internal_actions"]["package_case_study"]["authorization_status"] == "dry_run_only"
    assert data["allowed_internal_actions"]["prepare_E59_requirements"]["authorization_status"] == "dry_run_only"
    assert data["denied_actions"]["outreach"]["authorization_status"] == "deny"
    assert data["denied_actions"]["publication"]["authorization_status"] == "deny"
    assert data["denied_actions"]["customer_validation_claim"]["authorization_status"] == "deny"
    assert data["denied_actions"]["paid_signal_claim"]["authorization_status"] == "deny"
    assert data["denied_actions"]["real_mcp_transport_claim"]["authorization_status"] == "deny"
    assert data["denied_actions"]["external_intelligence_l5_claim"]["authorization_status"] == "deny"

