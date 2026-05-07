from office.mission_command.e72_cieu_hash_chain_context import (
    build_cieu_hash_chain_context,
    load_e71_promoted_k9_cieu_assets,
    map_k9_cieu_to_bridge_labs_audit_module,
)


def test_e72_loads_e71_promoted_k9_cluster_and_preserves_cieu_tuple():
    selected = load_e71_promoted_k9_cieu_assets()
    assert selected["cluster_id"] == "k9_cieu_hash_chain_spec_cluster"
    assert selected["cluster_was_top_scored"] is True
    assert selected["promoted_asset_count"] >= 1
    assert selected["E71_not_K9Audit_integration_completed"] is True

    context = build_cieu_hash_chain_context()
    assert set(context["imported_CIEU_five_tuple"]) == {"X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"}
    assert "previous_hash" in context["imported_hash_chain_context"]
    assert "current_hash" in context["imported_hash_chain_context"]
    assert "canonical_payload" in context["imported_hash_chain_context"]
    assert context["bridge_labs_status"]["hash_chain_context_imported"] is True
    assert context["bridge_labs_status"]["production_hash_chain_enabled"] is False
    assert context["bridge_labs_status"]["live_ledger_written"] is False
    assert context["bridge_labs_status"]["full_audit_verification_completed"] is False
    assert context["external_action_allowed"] is False


def test_e72_maps_k9_context_to_bridge_labs_module_without_execution_claims():
    mapping = map_k9_cieu_to_bridge_labs_audit_module()
    sample = mapping["sample_internal_record"]
    assert mapping["source_cluster_id"] == "k9_cieu_hash_chain_spec_cluster"
    assert sample["record_status"] == "internal_example_no_execution"
    assert sample["U_t"]["execution_status"] == "proposed_only"
    assert sample["hash_chain_ready_context"]["verification_status"] == "structural_context_only"
    assert mapping["bridge_labs_status"]["production_hash_chain_enabled"] is False
    assert mapping["external_action_allowed"] is False

