from office.mission_command.e71_legacy_asset_promotion_gate import (
    decide_legacy_asset_disposition,
    explain_legacy_promotion_limits,
    get_mainline_binding_plan,
    get_promoted_legacy_assets,
    get_quarantined_legacy_assets,
    load_legacy_asset_registry,
    score_legacy_asset,
)


def test_e71_promotion_gate_api_exposes_registry_scoring_and_limits():
    registry = load_legacy_asset_registry()
    assert registry["asset_count"] >= 60
    k9_asset = "k9_cieu_hash_chain_spec_cluster__CIEU_spec_md"
    assert score_legacy_asset(k9_asset)["priority_band"] == "P0_resurrect_now"
    assert decide_legacy_asset_disposition(k9_asset)["final_disposition"] == "integrate_into_CIEU_route"
    assert get_promoted_legacy_assets()["promoted_count"] > 0
    assert get_quarantined_legacy_assets()["quarantined_count"] > 0
    assert len(get_mainline_binding_plan()["bindings"]) >= 6
    limits = explain_legacy_promotion_limits()
    assert limits["old_assets_are_not_current_truth"] is True
    assert limits["provider_live_execution_is_not_enabled"] is True
    assert limits["external_action_allowed"] is False

