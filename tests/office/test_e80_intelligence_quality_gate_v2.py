import json
from pathlib import Path

from office.mission_command.e80_ceo_online_cognition_loop import evaluate_intelligence_output


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_intelligence_gate_v2_fails_generic_prompt_memory_output():
    gate = _load("operations/external_validation/e80_ceo_intelligence_quality_gate_v2.json")

    assert gate["gate_passed_for_E80_demo"] is True
    assert gate["generic_output_example"]["result"]["passed"] is False
    assert "uses_prompt_hints_only" in gate["generic_output_example"]["result"]["failure_reasons"]
    assert "no_repository_evidenced_capabilities_used" in gate["generic_output_example"]["result"]["failure_reasons"]


def test_e80_intelligence_evaluator_rejects_missing_counterfactuals_and_residuals():
    result = evaluate_intelligence_output({
        "capabilities_used": ["cap_repository_evidence"],
        "uses_prompt_hints_only": False,
        "buyer": "founder/operator",
        "trigger": "agent workflow receives write access",
        "tradeoff": "choose feedback over more infrastructure",
        "what_not_to_do": "do not build another CEO brain",
        "counterfactuals": [],
        "pre_action_residual_predictions": [],
        "adversarial_critique": "Could still be too abstract",
        "moves_toward_feedback_or_revenue": True,
    })

    assert result["passed"] is False
    assert "missing_counterfactuals" in result["failure_reasons"]
    assert "missing_pre_action_residual_predictions" in result["failure_reasons"]
