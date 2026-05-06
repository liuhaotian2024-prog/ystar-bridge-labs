from office.mission_command.e53_ceo_brain_readback_smoke import run_e53_ceo_brain_readback_smoke

def test_ceo_brain_reads_back_e53_owner_review_status():
    data = run_e53_ceo_brain_readback_smoke()
    assert data["passes"] is True
    assert data["checks"]["ceo_brain_sees_owner_approval_pending"] is True
    assert data["checks"]["ceo_brain_sees_external_action_blocked"] is True
