from office.mission_command.e66_model_driven_offer_core import write_all_e66_artifacts


def test_e66_artifacts_generate_end_to_end():
    gate = write_all_e66_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] == "e66_model_driven_offer_blueprint_completed_selected_route_confirmed"

