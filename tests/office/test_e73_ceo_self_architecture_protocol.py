from office.mission_command.e73_ceo_self_architecture_protocol import (
    evaluate_new_file_justification,
    load_ceo_self_architecture_protocol,
)


def test_e73_self_architecture_protocol_requires_retrospective_search():
    protocol = load_ceo_self_architecture_protocol()

    assert protocol["protocol_status"] == "required_for_future_feature_construction"
    assert "search_existing_mainline_modules" in protocol["steps"]
    assert "search_promoted_legacy_assets" in protocol["steps"]
    assert "identify_canonical_repo_owner" in protocol["steps"]
    assert "produce_no_duplication_proof" in protocol["steps"]
    assert "new_modules_without_retrospective_search" in protocol["explicit_rejections"]
    assert "duplicate_mechanisms" in protocol["explicit_rejections"]
    assert protocol["external_action_allowed"] is False


def test_e73_self_architecture_protocol_rejects_incomplete_new_file_justification():
    rejected = evaluate_new_file_justification({
        "goal": "add verifier",
        "decision": "create_new_only_if_no_owner_exists",
    })
    assert rejected["accepted"] is False
    assert "modules_searched" in rejected["missing_or_invalid_fields"]
    assert "no_duplication_proof" in rejected["missing_or_invalid_fields"]

    accepted = evaluate_new_file_justification({
        "goal": "create a sample packet adapter",
        "modules_searched": ["E72", "K9Audit"],
        "promoted_legacy_assets_checked": ["k9_cieu_hash_chain_spec_cluster"],
        "canonical_owner": "K9Audit",
        "decision": "create_adapter_contract",
        "dependency_boundary_map": "bridge-labs wraps K9 context only",
        "no_duplication_proof": "no production ledger/verifier in bridge-labs",
        "tests": ["tests/office/test_sample_adapter.py"],
        "rollback_or_deprecation_path": "delete generated adapter artifact",
        "readiness_effect": "supports L2 demo packet only",
    })
    assert accepted["accepted"] is True
    assert accepted["external_action_allowed"] is False
