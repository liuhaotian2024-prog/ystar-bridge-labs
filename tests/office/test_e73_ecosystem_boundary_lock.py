from office.mission_command.e73_readback import get_ecosystem_responsibility_matrix


def test_e73_responsibility_matrix_locks_canonical_owners():
    matrix = get_ecosystem_responsibility_matrix()
    owners = matrix["canonical_owners"]

    assert "engineering_grade_CIEU_ledger" in owners["K9Audit"]["canonical_capabilities"]
    assert "hash_chain_write_semantics" in owners["K9Audit"]["canonical_capabilities"]
    assert "CIEU_log_verification_semantics" in owners["K9Audit"]["canonical_capabilities"]

    assert "pre_execution_governance_decisions" in owners["Y-star-gov"]["canonical_capabilities"]
    assert "ALLOW_DENY_ESCALATE_semantics" in owners["Y-star-gov"]["canonical_capabilities"]

    assert "governed_MCP_execution_envelope" in owners["gov-mcp"]["canonical_capabilities"]
    assert "gov_check_gov_enforce_provider_boundary_semantics" in owners["gov-mcp"]["canonical_capabilities"]

    assert "AI_company_runtime" in owners["bridge-labs"]["canonical_capabilities"]
    assert "real_work_readiness_adjudication" in owners["bridge-labs"]["canonical_capabilities"]
    assert "K9Audit_ledger_or_verifier" in owners["bridge-labs"]["bridge_labs_must_not_duplicate"]
    assert matrix["read_only_repos_mutated"] is False
    assert matrix["external_action_allowed"] is False


def test_e73_overlap_conflict_map_exists_without_high_risk_claims():
    from office.mission_command.e73_ecosystem_boundary_lock import build_overlap_conflict_map

    overlap = build_overlap_conflict_map()
    assert overlap["relevant_file_count"] > 0
    assert overlap["high_risk_patterns"]["bridge_labs_claims_production_hash_chain_ledger"] is False
    assert overlap["high_risk_patterns"]["bridge_labs_independent_cryptographic_verifier_claimed"] is False
    assert overlap["high_risk_patterns"]["bridge_labs_governance_enforcement_claimed"] is False
    assert overlap["high_risk_patterns"]["bridge_labs_live_MCP_provider_execution_claimed"] is False
    assert overlap["read_only_repos_mutated"] is False
