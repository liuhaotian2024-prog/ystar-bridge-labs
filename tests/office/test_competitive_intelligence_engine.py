from pathlib import Path

from office.mission_command.competitive_intelligence_engine import build_competitive_intelligence
from office.mission_command.opportunity_synthesis_engine import compare_generated_opportunities


ROOT = Path(__file__).resolve().parents[2]


def test_competitive_intelligence_marks_internal_only_when_no_live_evidence():
    opportunities = compare_generated_opportunities(ROOT)[:3]
    intel = build_competitive_intelligence(opportunities, ROOT)
    assert intel["mode"] == "internal_hypothesis_only"
    assert intel["live_research_executed"] is False
    assert intel["external_action_executed"] is False
    assert all(profile["confidence"] == "low_internal_hypothesis_only" for profile in intel["profiles"])
