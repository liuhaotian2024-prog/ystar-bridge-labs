from office.mission_command.e58_case_study_capability_binding_gate import build_e58_capability_binding_payload, run_case_study_capability_binding_gate


def test_case_study_capability_binding_gate_passes_valid_bindings():
    payload = build_e58_capability_binding_payload()
    classes = {item["functional_class"] for item in payload["capability_bindings"]}
    assert "evidence_closure_capability" in classes
    assert "boundary_capability" in classes
    assert "behavior_control_capability" in classes
    data = run_case_study_capability_binding_gate(payload)
    assert data["passed"] is True
    assert data["checks"]["external_action_blocked"] is True

