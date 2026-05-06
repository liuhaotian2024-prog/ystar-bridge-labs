from office.mission_command.e57_commercial_route_decision import run_commercial_route_decision


def test_commercial_route_decision_changes_to_runtime_harness_without_overclaiming():
    data = run_commercial_route_decision()
    assert data["best_route_changed_from_E50B"] is True
    assert data["selected_route"] == "AI_agent_company_runtime_harness_case_study"
    assert data["nearest_alternative"] == "full_governed_execution_causal_audit_proof_stack"
    assert data["customer_validation_claimed"] is False
    assert data["paid_signal_claimed"] is False
    assert data["real_mcp_transport_claimed"] is False

