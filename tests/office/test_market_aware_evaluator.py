from pathlib import Path

from office.mission_command.e3_market_aware_evaluator import _score, evaluate_market_aware_opportunities


ROOT = Path(__file__).resolve().parents[2]


def test_evaluator_penalizes_missing_competitive_state():
    opportunity = {
        "title": "Some path",
        "owner_burden": "Low",
        "internal_assets": ["A"],
        "behavior_capability_required": [],
        "proof_assets": ["P"],
        "first_experiment": "48h test",
    }
    weak_profile = {"budget_channel": "ops", "direct_competitors": [], "substitutes": [], "differentiation_wedge": "x"}
    strong_profile = {
        "budget_channel": "ops",
        "direct_competitors": ["consultant"],
        "substitutes": ["DIY"],
        "no_action_alternative": "do nothing",
        "diy_alternative": "DIY",
        "differentiation_wedge": "x",
    }
    assert _score(opportunity, weak_profile, False)["competitor_state"] < _score(opportunity, strong_profile, False)["competitor_state"]


def test_evaluator_penalizes_missing_external_evidence():
    opportunity = {
        "title": "Some path",
        "owner_burden": "Low",
        "internal_assets": ["A"],
        "behavior_capability_required": [],
        "proof_assets": ["P"],
        "first_experiment": "48h test",
    }
    profile = {
        "budget_channel": "ops",
        "direct_competitors": ["consultant"],
        "substitutes": ["DIY"],
        "no_action_alternative": "do nothing",
        "diy_alternative": "DIY",
        "differentiation_wedge": "x",
    }
    assert _score(opportunity, profile, False)["external_evidence_strength"] < _score(opportunity, profile, True)["external_evidence_strength"]


def test_evaluator_can_recommend_research_first():
    evaluation = evaluate_market_aware_opportunities(ROOT)
    assert evaluation["recommend_research_first"] is True
    assert evaluation["default_decision"] == "tier1_read_only_research_first"
    assert evaluation["external_action_executed"] is False
