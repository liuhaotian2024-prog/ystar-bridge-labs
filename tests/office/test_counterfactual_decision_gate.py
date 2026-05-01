from pathlib import Path

from office.mission_command.counterfactual_decision_gate import (
    evaluate_counterfactual_gate,
    explain_default_decision,
    maybe_change_default_recommendation,
)
from office.mission_command.counterfactual_reasoning import build_counterfactual_matrix
from office.mission_command.meta_development_method_kernel import build_meta_development_trace


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_counterfactual_gate_can_change_default():
    default = {
        "opportunity_id": "heavy",
        "title": "Owner Heavy External Push",
        "method_score": 2,
        "owner_burden": "High owner burden",
        "behavior_capability_required": ["customer contact"],
    }
    alternative = {
        "opportunity_id": "light",
        "title": "Low Burden Internal Diagnostic",
        "method_score": 8,
        "owner_burden": "Low if Aiden prepares packet",
        "behavior_capability_required": ["sample deliverable"],
    }
    cases = build_counterfactual_matrix([default, alternative], {})
    gate = evaluate_counterfactual_gate([default, alternative], cases, [], {"external": "ARCHITECTURE_ONLY"})
    changed = maybe_change_default_recommendation(default, [default, alternative], gate)
    assert changed["title"] == "Low Burden Internal Diagnostic"


def test_counterfactual_gate_confirms_default_when_fast_disconfirming_and_low_owner_burden():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    default = trace["top_opportunities"][0]
    gate = trace["counterfactual_gate_result"]
    confirmed = maybe_change_default_recommendation(default, trace["top_opportunities"], gate)
    assert confirmed["title"] == trace["default_recommendation"]["title"]
    assert "confirms" in explain_default_decision(confirmed, gate)


def test_counterfactual_gate_detects_buyer_nonexistence_risk():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    ranked = trace["counterfactual_gate_result"]["ranked"]
    assert any(item["risk_flags"]["buyer_nonexistence_risk"] for item in ranked)
