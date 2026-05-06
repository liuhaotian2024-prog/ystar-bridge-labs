from office.mission_command.e56_internal_loop_dry_run_executor import run_internal_loop_dry_run_executor


def test_dry_run_executor_stays_internal_and_artifact_only():
    data = run_internal_loop_dry_run_executor()
    assert data["executor_status"] == "passed"
    assert len(data["stage_trace"]) == 12
    assert data["server_started"] is False
    assert data["network_used"] is False
    assert data["human_contacted"] is False

