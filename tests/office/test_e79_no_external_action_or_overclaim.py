import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_no_forbidden_claim_fields_are_true():
    for rel in [
        "operations/external_validation/e79_ceo_readback.json",
        "operations/external_validation/e79_completion_report.json",
    ]:
        artifact = _load(rel)
        for field in [
            "customer_validation_claimed",
            "expert_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "compliance_legal_claimed",
            "production_deployment_claimed",
            "L4_execution_claimed",
            "L5_readiness_claimed",
            "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
        ]:
            assert artifact[field] is False


def test_e79_no_external_action_outreach_publication_or_readonly_repo_mutation():
    completion = _load("operations/external_validation/e79_completion_report.json")

    assert completion["no_external_action"] is True
    assert completion["no_outreach"] is True
    assert completion["no_publication"] is True
    assert completion["read_only_repos_mutated"] is False
    assert completion["external_action_allowed"] is False


def test_e79_next_milestone_routing_is_quality_driven_not_revenue_or_mass_outreach():
    proposal = _load("operations/external_validation/e79_generated_next_milestone_proposal.json")

    assert proposal["selected_next_milestone"] == "E80_Record_Owner_Decision_for_L4_External_Feedback_No_Execution_Or_Execute_If_Approved"
    assert proposal["type"] == "owner_decision_gate"
    assert proposal["owner_decision_required"] is True
    assert proposal["external_action_allowed"] is False
    assert proposal["not_selected"]["direct_L4_execution"].startswith("not authorized")
