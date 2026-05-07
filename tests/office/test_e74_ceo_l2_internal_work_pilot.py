import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e74_loads_e73_l2_ready_and_stays_l2_only():
    plan = _load("operations/external_validation/e74_l2_internal_work_cycle_plan.json")
    completion = _load("operations/external_validation/e74_completion_report.json")

    assert plan["readiness_basis"]["E73_L2_decision"] == "ready"
    assert plan["readiness_basis"]["E73_L3_decision"] == "conditionally_ready"
    assert "no external research execution" in plan["work_boundaries"]
    assert completion["gate_passed"] is True
    assert completion["L2_remains_ready"] is True
    assert completion["L3_after_E74"] == "ready_for_owner_decision_packet_finalization_not_execution"
    assert completion["external_action_allowed"] is False


def test_e74_completion_is_real_work_not_construction():
    proposal = _load("operations/external_validation/e74_generated_next_milestone_proposal.json")
    packet = _load("operations/external_validation/e74_owner_facing_l3_readiness_packet.json")

    assert packet["packet_title"] == "Governed Business Operations Blueprint + CIEU Audit Module: L3 Read-Only Research Readiness Packet"
    assert packet["packet_status"] == "owner_reviewable_internal_no_execution"
    assert proposal["selected_next_milestone"] == "E75_L3_Read_Only_External_Research_Owner_Decision_Packet_Finalization"
    assert proposal["readiness_level_advanced"] == "L2_to_L3_owner_decision_preparation"
    assert "not a new runtime mechanism" in proposal["why_not_just_more_construction"]
    assert proposal["external_action_allowed"] is False
