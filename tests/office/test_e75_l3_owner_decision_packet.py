import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e75_loads_e74_and_finalizes_owner_decision_packet_not_execution():
    packet = _load("operations/external_validation/e75_l3_owner_decision_packet.json")
    completion = _load("operations/external_validation/e75_completion_report.json")

    assert packet["packet_status"] == "owner_decision_ready_no_execution"
    assert packet["approval_status"] == "pending_owner_decision"
    assert packet["references_to_E74"]["E74_completion_status"] == "e74_ceo_l2_internal_autonomous_work_pilot_completed"
    assert packet["L3_executed"] is False
    assert completion["gate_passed"] is True
    assert completion["L3_executed"] is False
    assert completion["next_step_type"] == "owner_decision_not_construction"


def test_e75_packet_has_four_owner_decision_options():
    form = _load("operations/external_validation/e75_l3_owner_approval_form.json")
    option_ids = {row["option_id"] for row in form["decision_options"]}

    assert option_ids == {
        "APPROVE_L3_READ_ONLY_RESEARCH_PILOT",
        "APPROVE_WITH_SCOPE_REDUCTION",
        "REQUEST_MORE_L2_INTERNAL_WORK",
        "REJECT_L3_FOR_NOW",
    }
    assert form["approval_status"] == "pending_owner_decision"
    assert form["approval_granted"] is False
    assert form["empty_owner_fields"]["owner_selected_option"] is None
