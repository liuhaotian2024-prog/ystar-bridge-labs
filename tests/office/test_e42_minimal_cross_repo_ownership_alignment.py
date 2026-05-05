from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_minimal_cross_repo_ownership_alignment():
    artifact = get_artifact("e42_minimal_cross_repo_ownership_alignment")
    owners = {item["repo"]: item["owns"] for item in artifact["ownership_boundaries"]}
    assert owners["Y-star-gov"] == "governance kernel"
    assert owners["gov-mcp"] == "execution/tool boundary"
    assert artifact["duplicate_governance_kernel_created"] is False
    assert artifact["duplicate_MCP_execution_layer_created"] is False
