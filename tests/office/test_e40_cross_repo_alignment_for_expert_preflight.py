from office.mission_command.e40_cross_repo_alignment_for_expert_preflight import build_cross_repo_alignment_for_expert_preflight


def test_cross_repo_alignment_is_read_only_and_non_executing():
    alignment = build_cross_repo_alignment_for_expert_preflight()
    proofs = alignment["proofs"]
    assert proofs["evidence_brief_does_not_replace_CIEU"] is True
    assert proofs["review_rubric_does_not_replace_check_enforce"] is True
    assert proofs["expert_feedback_would_not_become_canonical_learning_automatically"] is True
    assert proofs["message_draft_is_not_execution"] is True
    assert alignment["Y-star-gov_files_modified"] is False
    assert alignment["gov_mcp_files_modified"] is False
    assert alignment["duplicate_governance_kernel_created"] is False
    assert alignment["duplicate_mcp_execution_layer_created"] is False
