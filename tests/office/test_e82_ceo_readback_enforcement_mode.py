import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e82_readback_reports_dual_enforcement_and_no_l4_execution():
    readback = _load("operations/external_validation/e82_ceo_cognitive_os_readback.json")

    assert readback["previous_mode"] == "bridge_labs_pre_sync_validator"
    assert readback["current_enforcement_mode"] == "dual_enforced_bridge_labs_and_YstarGov"
    assert readback["canonical_governance_owner"] == "Y-star-gov"
    assert readback["YstarGov_synced"] is True
    assert readback["future_CEO_work_requires_pre_action_packet"] is True
    assert readback["future_CEO_work_requires_post_action_residual"] is True
    assert readback["L4_execution_authorized"] is False
    assert readback["L5_ready"] is False


def test_e82_completion_report_records_no_external_action_or_forbidden_claims():
    completion = _load("operations/external_validation/e82_completion_report.json")
    safety = completion["safety_statement"]

    assert completion["current_enforcement_mode"] == "dual_enforced_bridge_labs_and_YstarGov"
    assert completion["bypass_status"] == "denied"
    assert completion["next_recommended_milestone"] == "E83_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_Through_YStarGov_Cognitive_OS_If_Approved"
    assert safety["external_action"] is False
    assert safety["outreach"] is False
    assert safety["publication"] is False
    assert safety["payment"] is False
    assert safety["customer_validation_claim"] is False
    assert safety["paid_signal_claim"] is False
    assert safety["pricing_validation_claim"] is False
    assert safety["compliance_legal_claim"] is False
    assert safety["production_deployment_claim"] is False
    assert safety["L4_execution_claim"] is False
    assert safety["L5_readiness_claim"] is False
    assert safety["parallel_Y_star_gov_governance_engine"] is False
