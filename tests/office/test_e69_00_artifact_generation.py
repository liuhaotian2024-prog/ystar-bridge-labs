from office.mission_command.e69_ceo_next_action_planner import write_all_e69_artifacts


def test_e69_artifacts_generate_end_to_end():
    gate = write_all_e69_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] == "e69_ceo_selected_cieu_module_integration_as_next_action"

