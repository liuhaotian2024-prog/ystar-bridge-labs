import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_generated_codex_job_proposal_is_internal_no_execution():
    data = json.loads((ROOT / "operations/external_validation/e70_generated_codex_job_proposal.json").read_text())
    assert data["proposal_id"] == "e70_codex_job_E71_execute_internal_CIEU_module_integration_no_external_action"
    assert data["proposed_milestone_id"] == "E71_execute_internal_CIEU_module_integration_no_external_action"
    assert data["generated_by_CEO_self_bootstrap_runtime"] is True
    assert data["owner_approval_status"] == "pending_owner_decision"
    assert data["external_action_allowed"] is False
