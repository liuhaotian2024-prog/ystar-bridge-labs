from office.mission_command.e62_repository_archaeology_inventory import run_repository_archaeology_inventory


def test_e62_archaeology_runs_before_revenue_runtime_assumptions():
    data = run_repository_archaeology_inventory()
    assert data["asset_count"] > 0
    assert data["phase_0_completed_before_new_runtime_layer"] is True
    assert "safe_public_page_reader" in " ".join(data["what_must_not_be_rebuilt"])
    assert data["supports_autonomous_revenue_operation"] is True
