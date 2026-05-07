import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e72_product_binding_is_internal_and_no_execution():
    binding = json.loads((ROOT / "operations/external_validation/e72_cieu_audit_module_product_binding.json").read_text())
    assert binding["selected_product"] == "governed_business_operations_blueprint_for_agent_teams"
    assert binding["module"] == "CIEU Audit Module"
    assert binding["binding_status"] == "internal_structural_context_bound_no_execution"
    assert binding["source_legacy_cluster_consumed"] == "k9_cieu_hash_chain_spec_cluster"
    assert "internal structural integration" in binding["what_it_can_currently_claim"]
    assert "production deployment" in binding["what_it_cannot_claim"]
    assert "live audit ledger" in binding["what_it_cannot_claim"]
    assert binding["external_action_allowed"] is False


def test_e72_product_files_reflect_hash_chain_context_without_overclaim():
    module = json.loads((ROOT / "products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json").read_text())
    offer = json.loads((ROOT / "products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json").read_text())
    assert module["status"] == "internal_only_hash_chain_context_bound"
    assert module["hash_chain_context"]["previous_hash"]
    assert module["hash_chain_context"]["current_hash"]
    assert "production deployment" in module["does_not_claim"]
    assert offer["hash_chain_context_imported"] is True
    assert offer["production_hash_chain_enabled"] is False
    assert offer["live_audit_ledger_enabled"] is False
    assert offer["customer_validation_claimed"] is False
    assert offer["paid_signal_claimed"] is False
    assert offer["legal_compliance_claimed"] is False
    assert offer["external_action_allowed"] is False

