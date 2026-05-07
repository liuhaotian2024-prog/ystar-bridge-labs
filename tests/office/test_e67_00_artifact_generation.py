from office.mission_command.e67_external_validation_model import write_all_e67_artifacts


def test_e67_artifacts_generate_end_to_end_with_truthful_public_read_status():
    gate = write_all_e67_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] in {
        "e67_non_contact_external_validation_upgrade_completed",
        "e67_non_contact_validation_partial_with_public_read_blocker",
    }

