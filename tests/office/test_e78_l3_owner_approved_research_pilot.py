import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e78_records_owner_approval_and_executes_l3_public_read_only():
    plan = _load("operations/external_validation/e78_l3_owner_approved_research_run_plan.json")
    completion = _load("operations/external_validation/e78_completion_report.json")

    assert plan["approval_block_present"] is True
    assert plan["owner_decision_status"] == "APPROVE_L3_READ_ONLY_RESEARCH_PILOT"
    assert plan["phase_B_L3_authorized"] is True
    assert completion["owner_approval_block_detected"] is True
    assert completion["L3_executed"] is True
    assert completion["gate_passed"] is True


def test_e78_is_post_e73_gated_not_historical_first_read_claim():
    plan = _load("operations/external_validation/e78_l3_owner_approved_research_run_plan.json")
    completion = _load("operations/external_validation/e78_completion_report.json")

    assert "post-E73" in plan["lineage_correction"]
    assert "not the first public-read research" in plan["lineage_correction"]
    assert completion["false_first_external_read_only_research_claimed"] is False

