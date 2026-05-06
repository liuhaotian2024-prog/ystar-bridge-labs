from office.mission_command.e52_y_star_gov_validation_runner import run_y_star_gov_validation


def test_e52_y_star_gov_validation_passes():
    data = run_y_star_gov_validation()
    assert data['passed'] is True
    assert data['runtime_linkage_delta']['passed'] is True
    assert data['capability_binding_gate']['passed'] is True
