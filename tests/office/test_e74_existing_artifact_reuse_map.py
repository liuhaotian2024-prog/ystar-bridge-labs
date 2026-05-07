import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e74_records_e65_to_e73_and_product_artifact_reuse():
    reuse = json.loads((ROOT / "operations/external_validation/e74_existing_artifact_reuse_map.json").read_text())
    paths = {row["path"] for row in reuse["artifacts_inspected"]}

    assert "operations/external_validation/e65_market_dynamics_analysis_run.json" in paths
    assert "operations/external_validation/e66_selected_route_offer_blueprint.json" in paths
    assert "operations/external_validation/e67_external_validation_ladder.json" in paths
    assert "operations/external_validation/e68_strategic_portfolio_update.json" in paths
    assert "operations/external_validation/e69_ceo_selected_next_action_decision.json" in paths
    assert "operations/external_validation/e70_self_bootstrap_runtime_state.json" in paths
    assert "operations/external_validation/e71_promoted_legacy_assets.json" in paths
    assert "operations/external_validation/e72_cieu_hash_chain_context_state.json" in paths
    assert "operations/external_validation/e73_no_new_wheel_policy.json" in paths
    assert "products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json" in paths


def test_e74_no_new_wheel_compliance_blocks_duplicate_core_mechanisms():
    reuse = json.loads((ROOT / "operations/external_validation/e74_existing_artifact_reuse_map.json").read_text())
    risks = reuse["duplicate_mechanism_risk_assessment"]

    assert risks["duplicate_K9Audit_ledger_or_verifier_created"] is False
    assert risks["duplicate_Y_star_gov_governance_engine_created"] is False
    assert risks["duplicate_gov_mcp_execution_envelope_created"] is False
    assert risks["parallel_CEO_brain_created"] is False
    assert risks["new_product_mechanism_created"] is False
    assert reuse["canonical_owner_mapping"]["K9Audit"].startswith("CIEU ledger")
    assert reuse["canonical_owner_mapping"]["bridge-labs"].startswith("business/product")
