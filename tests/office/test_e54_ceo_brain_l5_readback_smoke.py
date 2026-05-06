from office.mission_command.e54_ceo_brain_l5_readback_smoke import run_l5_readback_smoke

def test_l5_readback_smoke_sees_registry_and_e53_completion():
    data=run_l5_readback_smoke()
    assert data['passes'] is True
    assert data['checks']['brain_sees_e53_completion_gate_fresh_registry'] is True
    assert data['checks']['brain_sees_owner_approval_pending_no_external_action'] is True
