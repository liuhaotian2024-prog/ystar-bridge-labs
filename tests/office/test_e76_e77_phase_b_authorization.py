import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_phase_b_does_not_run_without_explicit_approval():
    gate = _load("operations/external_validation/e76_e77_phase_gate_result.json")
    placeholder = _load("operations/external_validation/e76_e77_disabled_l3_execution_placeholder.json")

    assert gate["phase_B_execution_authorized"] is False
    assert gate["phase_B_execution_status"] == "not_executed_pending_owner_approval"
    assert placeholder["status"] == "not_executed_pending_owner_approval"
    assert placeholder["L3_executed"] is False
    assert placeholder["source_evidence_collected"] is False
    assert placeholder["real_source_receipts_generated"] is False


def test_no_real_l3_receipt_or_synthesis_outputs_created_when_disabled():
    forbidden_real_outputs = [
        "operations/external_validation/e76_e77_l3_source_receipts.json",
        "operations/external_validation/e76_e77_l3_evidence_synthesis.json",
        "operations/external_validation/e76_e77_l3_post_run_readiness_assessment.json",
    ]

    for rel in forbidden_real_outputs:
        assert not (ROOT / rel).exists()

