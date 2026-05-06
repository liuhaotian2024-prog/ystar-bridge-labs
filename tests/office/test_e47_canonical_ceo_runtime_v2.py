from office.mission_command.e47_canonical_ceo_runtime_v2 import run_canonical_ceo_runtime_v2, build_money_route_retest


def test_runtime_v2_invokes_all_adapters_and_selects_route():
    result = run_canonical_ceo_runtime_v2({"task_title": "money route", "task_description": "shortest credible route to real user or paid signal"})
    assert result["coverage_gate"]["passed"] is True
    assert result["coverage_gate"]["unknown_status_count"] == 0
    assert result["all_mandatory_adapters_invoked"] is True
    assert result["mandatory_adapter_count"] == 12
    assert result["route_decision"]["selected_route_id"] == "governed_agent_action_proof_packet"
    assert result["closure_packet"]["route_decision_produced"] is True
    assert result["no_external_action"] is True
    money = build_money_route_retest()
    assert money["coverage_gate_passed_before_retest"] is True
    assert len(money["route_matrix"]) >= 12
