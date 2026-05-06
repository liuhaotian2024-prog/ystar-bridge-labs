from office.mission_command.e56_internal_loop_anti_drift_gate import run_internal_loop_anti_drift_gate


def test_internal_loop_anti_drift_gate_passes_and_has_readback():
    data = run_internal_loop_anti_drift_gate()
    assert data["passed"] is True
    assert data["checks"]["readback_proof_valid"] is True
    assert data["checks"]["KG_CZL_CIEU_linked"] is True

