from office.mission_command.e56_internal_company_loop_l5_readiness_gate import run_internal_company_loop_l5_readiness_gate


def test_l5_readiness_gate_requires_all_cycle_stages():
    data = run_internal_company_loop_l5_readiness_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "internal_company_operating_loop_l5_ready"
    assert data["recommended_next_milestone"] == "E57_post_L5_money_route_retest"
    assert data["checks"]["no_external_action_occurred"] is True

