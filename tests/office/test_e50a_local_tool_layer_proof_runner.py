from office.mission_command.e50a_local_tool_layer_proof_runner import run_local_tool_layer_proof


def test_e50a_subprocess_proof_closes_or_records_exact_status():
    result = run_local_tool_layer_proof(timeout=20)
    assert result["final_status"] == "tool_layer_allow_deny_closed"
    assert result["allow_closed"] is True
    assert result["deny_closed"] is True
    assert result["tool_layer_allow_deny_closed"] is True
    assert result["scratch_home_used"] is True
    assert result["scratch_removed"] is True
    assert result["started_real_server"] is False
    assert result["mutated_real_client_config"] is False
    assert result["ports_opened"] == []
    assert result["no_external_action"] is True
