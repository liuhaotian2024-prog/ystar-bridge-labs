import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_owner_decision_defaults_to_pending_without_explicit_approval():
    record = _load("operations/external_validation/e76_e77_owner_decision_record.json")

    assert record["decision_status"] == "pending_owner_decision"
    assert record["prompt_approval_block_present"] is False
    assert record["machine_readable_approval_artifact_found"] is False
    assert record["phase_b_execution_authorized"] is False
    assert record["E75_approval_status"] == "pending_owner_decision"
    assert record["E75_approval_granted"] is False


def test_combined_milestone_request_is_not_treated_as_approval():
    record = _load("operations/external_validation/e76_e77_owner_decision_record.json")
    gate = _load("operations/external_validation/e76_e77_phase_gate_result.json")

    assert record["do_not_infer_approval_from_combined_milestone_request"] is True
    assert gate["phase_A_always_ran"] is True
    assert gate["phase_B_execution_authorized"] is False
    assert gate["approval_artifact_or_prompt_block"] is None

