from office.mission_command.e61_live_public_read_capability_binding_gate import run_live_public_read_capability_binding_gate


def test_e61_capability_binding_gate_binds_smoke_probe_to_behavior_center():
    data = run_live_public_read_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["smoke_probe_bound_to_behavior_center_and_governance"] is True
    assert data["checks"]["receipts_bound_to_evidence_centerline"] is True
