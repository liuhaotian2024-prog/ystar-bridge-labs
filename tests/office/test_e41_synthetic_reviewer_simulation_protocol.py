from office.mission_command.e41_synthetic_reviewer_simulation_protocol import build_synthetic_reviewer_simulation_protocol


def test_e41_synthetic_reviewer_simulation_protocol_contract():
    artifact = build_synthetic_reviewer_simulation_protocol()
    labels = set(artifact["hard_labels"])
    assert {"synthetic_output", "internal_simulation_only", "not_customer_validation", "not_expert_feedback", "not_paid_signal", "not_canonical_learning"}.issubset(labels)
    assert artifact["external_tool_called"] is False
    assert artifact["provider_api_or_tool_execution_occurred"] is False

