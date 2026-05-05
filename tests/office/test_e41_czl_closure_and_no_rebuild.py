from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e41_czl_closure_and_no_rebuild_gate():
    closure = get_artifact("e41_czl_closure")
    gate = get_artifact("e41_no_rebuild_alignment_gate")
    assert closure["E40_route_drift_corrected"] is True
    assert closure["frontier_capability_import_loop_created"] is True
    assert closure["provider_api_or_tool_execution_occurred"] is False
    assert closure["expert_contact_occurred"] is False
    assert closure["customer_validation_claimed"] is False
    assert closure["paid_signal_claimed"] is False
    assert gate["gate_passed"] is True
    assert gate["duplicate_governance_kernel_created"] is False
    assert gate["duplicate_MCP_execution_layer_created"] is False
    assert gate["second_CEO_brain_created"] is False
    assert gate["second_CEO_KG_created"] is False
