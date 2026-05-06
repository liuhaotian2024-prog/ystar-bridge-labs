from office.mission_command.e55_y_star_gov_validation_runner import run_e55_y_star_gov_validation

def test_y_star_gov_validation_passes_readonly():
    data = run_e55_y_star_gov_validation()
    assert data["passed"] is True
    assert data["used_read_only_y_star_gov"] is True
