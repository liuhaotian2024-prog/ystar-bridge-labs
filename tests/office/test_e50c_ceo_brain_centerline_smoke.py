from office.mission_command.e50c_ceo_brain_centerline_smoke import run_ceo_brain_centerline_smoke


def test_canonical_runtime_consumes_updated_brain_context_before_route_decision():
    smoke = run_ceo_brain_centerline_smoke()
    assert smoke['passes'] is True
    assert smoke['assertions']['canonical_runtime_saw_brain_context'] is True
    assert smoke['canonical_runtime_consumption']['canonical_brain_context_selected_route'] == 'package_governed_agent_action_proof_packet'
    assert smoke['canonical_runtime_consumption']['no_external_action'] is True
