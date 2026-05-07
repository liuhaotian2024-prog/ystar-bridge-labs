import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_completion_report_records_no_external_action_or_forbidden_claims():
    completion = _load("operations/external_validation/e81_completion_report.json")
    safety = completion["safety_statement"]

    assert completion["Y_star_gov_mutated"] is False
    assert completion["Y_star_gov_not_mutated_reason"]
    assert completion["current_enforcement_mode"] == "bridge_labs_pre_sync_validator"
    assert completion["YstarGov_sync_status"] == "YstarGov_pending_owner_approved_patch"

    forbidden_flags = [
        "external_action",
        "outreach",
        "publication",
        "read_only_repo_mutation",
        "customer_validation_claim",
        "expert_validation_claim",
        "paid_signal_claim",
        "pricing_validation_claim",
        "compliance_legal_claim",
        "production_deployment_claim",
        "L4_execution_claim",
        "L5_readiness_claim",
        "duplicate_K9_Y_star_gov_gov_mcp_core_implementation",
    ]
    assert all(safety[flag] is False for flag in forbidden_flags)


def test_e81_next_milestone_is_not_external_action_or_vague_infrastructure():
    proposal = _load("operations/external_validation/e81_generated_next_milestone_proposal.json")

    assert proposal["proposed_milestone_id"] == "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch"
    assert proposal["type"] == "governance_sync_patch"
    assert proposal["owner_approval_required"] is True
    assert proposal["external_action_authorized_now"] is False
    assert "vague_more_infrastructure" in proposal["forbidden_routes"]
    assert "L5_revenue_work" in proposal["forbidden_routes"]
