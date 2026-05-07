import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_completion_report_has_no_forbidden_claims_or_external_action():
    report = _load("operations/external_validation/e80_completion_report.json")
    safety = report["safety_statement"]

    assert report["base_verified"] is True
    assert safety["external_action"] is False
    assert safety["outreach"] is False
    assert safety["publication"] is False
    assert safety["customer_validation_claim"] is False
    assert safety["expert_validation_claim"] is False
    assert safety["paid_signal_claim"] is False
    assert safety["pricing_validation_claim"] is False
    assert safety["compliance_legal_claim"] is False
    assert safety["production_deployment_claim"] is False
    assert safety["L4_execution_claim"] is False
    assert safety["L5_readiness_claim"] is False
    assert safety["duplicate_K9_Y_star_gov_gov_mcp_core_implementation"] is False


def test_e80_next_milestone_is_not_vague_infrastructure_or_revenue_work():
    proposal = _load("operations/external_validation/e80_generated_next_milestone_proposal.json")

    assert proposal["proposed_milestone_id"] == "E81_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_If_Approved"
    assert proposal["owner_approval_required"] is True
    assert proposal["external_action_authorized_now"] is False
    assert "generic_more_infrastructure" in proposal["forbidden_routes"]
    assert "L5_revenue_work" in proposal["forbidden_routes"]
