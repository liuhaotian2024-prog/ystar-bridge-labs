from office.mission_command.e55_behavior_capability_binding_gate import build_e55_capability_binding_payload, run_behavior_capability_binding_gate

def test_behavior_capability_binding_gate_binds_behavior_to_runtime_and_governance():
    payload = build_e55_capability_binding_payload()
    action_model = next(r for r in payload["capability_bindings"] if r["capability_id"] == "e55_action_model")
    assert "canonical_action_runtime" in action_model["actual_binding"]
    assert run_behavior_capability_binding_gate()["passed"] is True
