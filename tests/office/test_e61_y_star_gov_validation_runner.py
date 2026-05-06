from office.mission_command.e61_y_star_gov_validation_runner import run_e61_y_star_gov_validation


def test_e61_y_star_gov_validation_passes_read_only():
    data = run_e61_y_star_gov_validation()
    assert data["passed"] is True
    assert data["read_only_validator"] is True
    assert data["external_action_allowed"] is False
