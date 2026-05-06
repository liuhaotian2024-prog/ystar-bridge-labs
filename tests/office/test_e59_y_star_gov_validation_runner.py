from office.mission_command.e59_y_star_gov_validation_runner import run_e59_y_star_gov_validation


def test_e59_y_star_gov_validation_passes_read_only():
    data = run_e59_y_star_gov_validation()
    assert data["passed"] is True
    assert data["runtime_linkage_valid"] is True
    assert data["readback_proof_valid"] is True
    assert data["read_only_validator"] is True

