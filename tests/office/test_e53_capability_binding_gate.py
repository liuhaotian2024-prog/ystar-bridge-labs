from office.mission_command.e53_capability_binding_gate import build_e53_capability_binding_payload, run_e53_capability_binding_gate

def test_capability_binding_gate_passes_valid_bindings():
    data = run_e53_capability_binding_gate()
    assert data["passed"] is True
    assert data["checks"]["no_future_review_protocol_executes_without_owner_approval"] is True

def test_behavior_bypass_denied():
    payload = build_e53_capability_binding_payload()
    for record in payload["capability_bindings"]:
        if record["capability_id"] == "e53_first_user_review_protocol":
            record["actual_binding"] = ["Y_star_gov_boundary"]
            record["binding_status"] = "wrong_centerline"
    data = run_e53_capability_binding_gate(payload)
    assert data["passed"] is False
    assert data["gate"]["allowed"] is False
