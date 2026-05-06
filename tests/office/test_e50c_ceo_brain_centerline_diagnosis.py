from office.mission_command.e50c_ceo_brain_centerline_diagnosis import diagnose_ceo_brain_centerline


def test_diagnosis_records_written_but_not_readback_baseline_and_current_connection():
    data = diagnose_ceo_brain_centerline()
    assert data['baseline_status_before_e50c'] == 'ceo_brain_written_but_not_read_back'
    assert data['current_status_after_e50c'] == 'ceo_brain_centerline_connected'
    assert data['e50b_selected_route_artifact'] == 'package_governed_agent_action_proof_packet'
    assert data['governance_boundary_preserved'] is True
