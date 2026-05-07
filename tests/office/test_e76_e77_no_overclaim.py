import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e76_e77_no_forbidden_claim_fields_are_true():
    artifacts = [
        _load("operations/external_validation/e76_e77_ceo_readback.json"),
        _load("operations/external_validation/e76_e77_completion_report.json"),
    ]

    forbidden_true_fields = [
        "customer_validation_claimed",
        "paid_signal_claimed",
        "pricing_validation_claimed",
        "compliance_legal_claimed",
        "production_deployment_claimed",
        "live_ledger_claimed",
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
    ]
    for artifact in artifacts:
        for field in forbidden_true_fields:
            assert artifact[field] is False


def test_read_only_repos_not_mutated_and_no_false_first_read_claim():
    completion = _load("operations/external_validation/e76_e77_completion_report.json")

    assert completion["read_only_repos_mutated"] is False
    assert completion["false_first_external_read_only_research_claimed"] is False
    assert completion["L4_ready"] is False
    assert completion["L5_ready"] is False

