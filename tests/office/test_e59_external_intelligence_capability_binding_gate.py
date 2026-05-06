from office.mission_command.e59_external_intelligence_capability_binding_gate import run_external_intelligence_capability_binding_gate


def test_e59_capability_binding_maps_capabilities_to_correct_centerlines():
    data = run_external_intelligence_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["page_read_adapter_bound_to_action_runtime_and_governance"] is True
    assert data["checks"]["receipts_evidence_bound_to_evidence_centerline"] is True
    assert data["checks"]["source_policy_bound_to_boundary"] is True

