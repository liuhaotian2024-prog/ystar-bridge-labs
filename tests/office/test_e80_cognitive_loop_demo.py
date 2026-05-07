import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_live_demo_uses_evidence_backed_capabilities_and_multiple_actions():
    demo = _load("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json")

    assert demo["evidence_backed_capability_recall"]
    assert len(demo["competing_actions"]) >= 6
    assert len(demo["counterfactual_comparison"]) >= 6
    assert demo["selected_decision"]
    assert "Discovery-first activation" in demo["selected_decision_reason"]


def test_e80_live_demo_includes_pre_action_residual_predictions_and_adversarial_critique():
    demo = _load("operations/external_validation/e80_cognitive_loop_demo_current_strategy_decision.json")

    for candidate in demo["counterfactual_comparison"]:
        residual = candidate["pre_action_CIEU_prediction"]
        for key in ["X_t", "candidate_U_t", "Y_star_t", "expected_Y_t_plus_1", "likely_R_t_plus_1"]:
            assert key in residual
    assert demo["adversarial_critique"]
    assert demo["what_not_to_do_next"]
    assert "do not create another broad CEO brain or generic runtime" in demo["what_not_to_do_next"]
