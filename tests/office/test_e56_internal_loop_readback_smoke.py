from office.mission_command.e56_internal_loop_readback_smoke import run_internal_loop_readback_smoke


def test_brain_reads_back_cycle_status():
    data = run_internal_loop_readback_smoke()
    assert data["passes"] is True
    assert data["checks"]["ceo_brain_sees_selected_action"] is True
    assert data["checks"]["ceo_brain_sees_next_milestone_proposal"] is True

