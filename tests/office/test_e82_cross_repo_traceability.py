import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e82_traceability_maps_e81_contract_to_ystar_gov_module():
    trace = _load("operations/external_validation/e82_cross_repo_cognitive_os_traceability_matrix.json")

    assert trace["E81_contract_id"] == "ceo_cognitive_os_loop_contract_v1"
    assert trace["E81_pre_action_schema_path"].endswith("e81_ceo_mandatory_pre_action_packet_schema.json")
    assert trace["E81_post_action_schema_path"].endswith("e81_ceo_mandatory_post_action_residual_schema.json")
    assert trace["Y_star_gov_module_path"] == "ystar/governance/ceo_cognitive_os_contract.py"
    assert trace["Y_star_gov_tests_path"] == "tests/governance/test_ceo_cognitive_os_contract.py"
    assert "missing or malformed pre-action CIEU prediction" in trace["denial_rules_mapped"]
    assert "customer_validation_claim" in trace["forbidden_claims_mapped"]


def test_e82_live_cross_repo_fixture_uses_ystar_gov_validator_and_denies_bypass():
    fixture = _load("operations/external_validation/e82_live_cross_repo_validation_fixture.json")

    assert fixture["direct_Y_star_gov_import_used"] is True
    assert fixture["fallback_fixture_used"] is False
    assert fixture["valid_packet_result"]["decision"] == "ALLOW"
    assert fixture["invalid_recent_memory_only_result"]["decision"] == "DENY"
    assert fixture["invalid_missing_counterfactual_result"]["decision"] == "DENY"
    assert fixture["invalid_l4_without_owner_approval_result"]["decision"] == "DENY"
    assert fixture["forbidden_claim_result"]["decision"] == "DENY"

