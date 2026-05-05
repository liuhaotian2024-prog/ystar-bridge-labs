from office.mission_command.e39_cross_repo_alignment_after_capability_import import build_cross_repo_alignment_after_capability_import


def test_cross_repo_alignment_preserves_kernel_and_execution_boundaries():
    alignment = build_cross_repo_alignment_after_capability_import()
    checks = alignment["specific_checks"]
    assert checks["claim_graph_does_not_replace_CIEU"] is True
    assert checks["contradiction_graph_does_not_replace_governance_kernel"] is True
    assert checks["durable_research_thread_does_not_replace_CZL"] is True
    assert checks["decision_eval_benchmark_does_not_replace_Y_star_gov_check_enforce"] is True
    assert checks["no_execution_adapter_implemented_in_Labs"] is True
    assert alignment["Y-star-gov_files_modified"] is False
    assert alignment["gov_mcp_files_modified"] is False
    assert alignment["duplicate_governance_kernel_created"] is False
    assert alignment["duplicate_mcp_execution_layer_created"] is False
