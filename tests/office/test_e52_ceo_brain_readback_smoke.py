from office.mission_command.e52_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_e52_ceo_brain_reads_back_packet_status():
    data = run_ceo_brain_readback_smoke()
    assert data['passes'] is True
    assert data['checks']['ceo_brain_sees_proof_packet_exists'] is True
    assert data['proof_packet_state']['next_recommended_milestone'] == 'E53_owner_review_and_single_first_user_review_approval_gate'
