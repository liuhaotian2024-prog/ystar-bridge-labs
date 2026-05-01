from pathlib import Path

from office.mission_command.e4_cycle import build_e4_cycle
from office.mission_command.strict_czl import strict_czl_is_blocked


ROOT = Path(__file__).resolve().parents[2]


def test_strict_e4_blocked_full_rt1_nonzero_without_live_research():
    state = build_e4_cycle(ROOT)["strict_czl"]
    assert state["status"] == "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG"
    assert state["feasible_internal_rt1_score"] == 0
    assert state["full_mission_rt1_score"] > 0


def test_strict_e4_complete_requires_receipt_and_source_summaries():
    cycle = build_e4_cycle(ROOT)
    runtime = cycle["runtime"]
    assert runtime["live_research_executed"] is False
    assert cycle["strict_czl"]["full_mission_rt1_score"] > 0


def test_no_cieu_write_and_no_external_side_effects():
    cycle = build_e4_cycle(ROOT)
    assert cycle["external_action_executed"] is False
    assert cycle["runtime"]["external_action_executed"] is False
    assert "CIEU" in str(cycle["owner_packet"]["approval_does_not_cover"])
