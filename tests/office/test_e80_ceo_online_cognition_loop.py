import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_ceo_online_cognition_loop_has_all_required_stages():
    spec = _load("operations/external_validation/e80_ceo_online_cognition_loop_spec.json")
    stages = {stage["stage_id"] for stage in spec["stages"]}

    for stage in [
        "mission_and_owner_constraint_recall",
        "full_capability_inventory_recall",
        "relevant_historical_asset_retrieval",
        "current_problem_classification",
        "canonical_owner_selection",
        "existing_module_reuse_extend_wrap_create_new_decision",
        "long_memory_KG_brain_recall_if_evidence_supported",
        "field_dimensional_reasoning_if_evidence_supported",
        "thesis_generation",
        "counterfactual_action_comparison",
        "pre_action_CIEU_residual_prediction",
        "adversarial_critique",
        "commercial_sharpness_gate",
        "no_new_wheel_gate",
        "decision",
        "post_action_CIEU_residual_and_learning_update",
    ]:
        assert stage in stages


def test_e80_loop_blocks_recent_memory_and_generic_output_failure_modes():
    spec = _load("operations/external_validation/e80_ceo_online_cognition_loop_spec.json")

    assert spec["evidence_driven_by_inventory"] is True
    assert spec["not_a_new_CEO_brain"] is True
    assert "fails_if_recent_milestone_only_reasoning" in spec["failure_conditions"]
    assert "fails_if_no_counterfactual_comparison" in spec["failure_conditions"]
    assert "fails_if_no_pre_action_CIEU_residual_prediction" in spec["failure_conditions"]
    assert spec["honest_activation_statuses"]["sixD_or_field_brain"] != "missing"
