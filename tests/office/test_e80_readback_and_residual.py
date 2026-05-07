import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e80_readback import run_e80_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_readback_reports_discovery_first_activation_status():
    readback = _load("operations/external_validation/e80_ceo_cognitive_activation_readback.json")
    smoke = run_e80_readback_smoke(ROOT)

    assert smoke["passes"] is True
    assert readback["E80_R2_status"] == "discovery_first_ceo_cognition_loop_activated"
    assert readback["capabilities_discovered"] > 1000
    assert readback["repository_discovered_not_prompt_hinted_count"] > 0
    assert readback["prompt_hinted_unverified_count"] > 0
    assert readback["external_action_allowed"] is False


def test_e80_ceo_adapter_can_read_discovery_first_state():
    context = load_ceo_brain_context({"task_title": "E80 readback", "task_description": "discovery-first cognition"})

    assert context["current_e80_status"] == "discovery_first_ceo_cognition_loop_activated"
    assert context["current_e80_capabilities_discovered"] > 1000
    assert context["current_e80_repository_discovered_not_prompt_hinted_count"] > 0
    assert context["current_e80_prompt_hinted_unverified_count"] > 0
    assert context["current_e80_external_action_allowed"] is False
    assert context["current_e80_L4_execution_authorized"] is False


def test_e80_cieu_residual_has_five_tuple_and_expected_residuals():
    residual = _load("operations/external_validation/e80_cieu_residual_for_discovery_first_ecosystem_activation.json")

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
    assert residual["U_t"]["external_action_executed"] is False
    assert "no customer validation" in residual["R_t_plus_1"]["residual_gaps"]
    assert "no paid signal" in residual["R_t_plus_1"]["residual_gaps"]
