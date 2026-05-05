from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_minimal_cross_repo_alignment_boundaries():
    artifact = get_artifact("e43_minimal_cross_repo_alignment")
    assert artifact["Y-star-gov"]["role"] == "governance kernel"
    assert artifact["gov-mcp"]["role"] == "execution boundary"
    assert artifact["K9Audit"]["role"] == "audit layer"
    assert artifact["duplicate_governance_kernel_created"] is False
    assert artifact["duplicate_MCP_execution_layer_created"] is False
