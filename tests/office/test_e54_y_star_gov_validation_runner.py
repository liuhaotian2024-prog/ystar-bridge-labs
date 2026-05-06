from office.mission_command.e54_y_star_gov_validation_runner import run_e54_y_star_gov_validation

def test_y_star_gov_validation_passes():
    assert run_e54_y_star_gov_validation()['passed'] is True
