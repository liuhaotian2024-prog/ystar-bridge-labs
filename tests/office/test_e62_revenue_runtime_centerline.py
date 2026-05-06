from office.mission_command.e62_autonomous_revenue_runtime_centerline import run_autonomous_revenue_runtime_centerline


def test_e62_revenue_runtime_centerline_recenters_primary_objective():
    data = run_autonomous_revenue_runtime_centerline()
    assert data["centerline_status"] == "autonomous_revenue_runtime_recentered_internal_only"
    assert "autonomous value creation" in data["primary_objective"]
    assert "proof packets" in data["secondary_artifacts"]
    assert data["external_business_execution_owner_gated"] is True
    assert data["autonomous_revenue_achieved"] is False
