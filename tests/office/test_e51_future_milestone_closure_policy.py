from office.mission_command.e51_future_milestone_closure_policy import build_future_milestone_closure_policy


def test_e51_future_milestone_closure_policy_blocks_report_only_p0():
    policy = build_future_milestone_closure_policy()
    assert 'readback_proof' in policy['required_fields']
    assert policy['no_report_only_p0'] is True
    assert any('decision packet' in item for item in policy['blocking_failures'])
