import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_post_action_residual_schema_requires_cieu_and_learning_fields():
    schema = _load("operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json")
    required = set(schema["minimum_required_fields"])

    for field in [
        "linked_pre_action_packet_id",
        "CIEU_record",
        "residuals",
        "overclaim_check",
        "no_new_wheel_check",
        "owner_usefulness_check",
        "intelligence_gate_result",
        "capability_state_updates",
        "YstarGov_sync_status",
        "what_not_to_do_next",
    ]:
        assert field in required


def test_e81_post_action_schema_requires_cieu_five_tuple():
    schema = _load("operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json")

    assert set(schema["CIEU_record_required_fields"]) == {"X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"}
