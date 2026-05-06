from office.mission_command.e55_dry_run_action_executor import run_dry_run_executor

def test_dry_run_executor_never_starts_server_or_network():
    data = run_dry_run_executor()
    assert data["executor_status"] == "passed"
    assert data["checks"]["no_server_started"] is True
    assert data["checks"]["no_network_used"] is True
    assert data["checks"]["external_action_refused"] is True
