from office.mission_command.e56_y_star_gov_validation_runner import run_e56_y_star_gov_validation


def test_y_star_gov_validation_passes_read_only():
    data = run_e56_y_star_gov_validation()
    assert data["passed"] is True
    assert data["read_only_validator"] is True
    assert data["external_action_allowed"] is False

