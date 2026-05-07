import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_completion_report_states_no_external_action_without_approval():
    completion = _load("operations/external_validation/e76_e77_completion_report.json")

    assert completion["gate_passed"] is True
    assert completion["phase_B_authorization_result"] is False
    assert completion["L3_executed"] is False
    assert completion["new_external_evidence_collected"] is False
    assert completion["external_action_allowed"] is False
    assert completion["why_not_executed"] == "No explicit owner approval artifact or exact prompt approval block exists."


def test_next_milestone_routes_to_decision_waiting_when_pending():
    proposal = _load("operations/external_validation/e76_e77_generated_next_milestone_proposal.json")

    assert proposal["owner_decision_status"] == "pending_owner_decision"
    assert proposal["phase_B_execution_authorized"] is False
    assert proposal["selected_next_milestone"] == "E78_Record_or_Await_Explicit_Owner_Approval_for_L3_Read_Only_Research"
    assert proposal["type"] == "decision_wait_or_recording"

