import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_pre_action_packet_schema_requires_cognitive_nervous_system_fields():
    schema = _load("operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json")
    required = set(schema["minimum_required_fields"])

    for field in [
        "discovered_capabilities_consulted",
        "historical_assets_consulted",
        "canonical_owner_map",
        "no_new_wheel_decision",
        "counterfactual_comparison",
        "predicted_CIEU_records",
        "adversarial_critique",
        "what_not_to_do",
        "owner_approval_state",
        "bypass_attempt",
        "loop_stage_results",
    ]:
        assert field in required


def test_e81_pre_action_schema_requires_cieu_prediction_tuple():
    schema = _load("operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json")

    assert set(schema["predicted_CIEU_record_required_fields"]) == {
        "X_t",
        "U_t",
        "Y_star_t",
        "expected_Y_t_plus_1",
        "predicted_R_t_plus_1",
        "residual_severity",
    }
    assert schema["bypass_attempt_allowed_values"] == [False]
