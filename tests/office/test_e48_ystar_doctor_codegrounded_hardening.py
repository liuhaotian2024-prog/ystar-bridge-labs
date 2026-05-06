from office.mission_command.e48_ystar_doctor_codegrounded_hardening import analyze_ystar_doctor


def test_e48_ystar_doctor_is_classified_not_assumed():
    data = analyze_ystar_doctor()
    assert data['ystar_doctor_status_classified_or_fixed'] is True
    assert data['demo_command_attempted']['command'] == ['python3', '-m', 'ystar', 'demo']
    assert data['patch_required'] is False
    assert data['no_external_action'] is True
    assert data['repo_doctor_classification']
