from office.mission_command.e64_dual_axis_revenue_core import write_all_e64_artifacts


def test_e64_artifacts_generate_end_to_end():
    gate = write_all_e64_artifacts()
    assert gate["gate_passed"] is True
    assert gate["selected_final_first_cash_path"] == "governed_business_operations_blueprint_for_agent_teams"
    assert gate["recommended_next_milestone"] == "E65_draft_runtime_harness_deployment_offer_and_delivery_blueprint_no_execution"
