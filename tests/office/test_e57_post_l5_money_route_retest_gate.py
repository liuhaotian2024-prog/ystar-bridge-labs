from office.mission_command.e57_post_l5_money_route_retest_gate import run_post_l5_money_route_retest_gate


def test_completion_gate_passes_only_with_readback_and_no_overclaim():
    data = run_post_l5_money_route_retest_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] == "post_l5_money_route_retest_closed"
    assert data["recommended_next_milestone"] == "E58_package_AI_agent_company_runtime_harness_case_study"
    assert data["checks"]["no_customer_validation_claim"] is True
    assert data["checks"]["no_paid_signal_claim"] is True
    assert data["checks"]["no_real_mcp_transport_claim"] is True

