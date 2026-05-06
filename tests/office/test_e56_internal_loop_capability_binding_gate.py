from office.mission_command.e56_internal_loop_capability_binding_gate import run_internal_loop_capability_binding_gate


def test_internal_loop_capability_binding_gate_passes():
    data = run_internal_loop_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["behavior_binds_to_canonical_runtime"] is True
    assert data["checks"]["evidence_binds_to_KG_CZL_CIEU"] is True

