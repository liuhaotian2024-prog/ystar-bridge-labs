from office.mission_command.e60_market_readiness_anti_drift_gate import run_market_readiness_anti_drift_gate


def test_e60_anti_drift_gate_passes_and_has_live_limitation_reader():
    data = run_market_readiness_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["selected_route_has_next_runtime_reader"] is True
    assert data["checks"]["live_read_limitation_has_reader"] is True
    assert data["checks"]["fixture_only_not_live_market_freshness"] is True
