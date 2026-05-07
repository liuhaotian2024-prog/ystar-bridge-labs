import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e78_no_forbidden_claim_fields_are_true():
    for rel in [
        "operations/external_validation/e78_ceo_readback.json",
        "operations/external_validation/e78_completion_report.json",
    ]:
        artifact = _load(rel)
        for field in [
            "customer_validation_claimed",
            "expert_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "compliance_legal_claimed",
            "production_deployment_claimed",
            "live_ledger_claimed",
            "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
        ]:
            assert artifact[field] is False


def test_e78_no_contact_publication_payment_login_or_readonly_repo_mutation():
    completion = _load("operations/external_validation/e78_completion_report.json")

    assert completion["no_customer_outreach"] is True
    assert completion["no_expert_outreach"] is True
    assert completion["no_publication"] is True
    assert completion["no_payment"] is True
    assert completion["no_login_gated_action"] is True
    assert completion["read_only_repos_mutated"] is False

