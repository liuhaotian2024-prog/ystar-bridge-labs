from office.mission_command.e54_ceo_brain_maturity_diagnosis import diagnose_ceo_brain_maturity

def test_maturity_diagnosis_has_17_dimensions_and_target_l5():
    data=diagnose_ceo_brain_maturity()
    assert len(data['dimensions']) == 17
    assert data['target_level'] == 'L5 cognitive state center'
